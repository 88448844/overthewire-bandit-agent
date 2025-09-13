import yaml, time, re, os, sys

# Get the directory where this script is located to build absolute paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from ssh_client import SSHSession
from agent import Reasoner
from tools import build_tool_context
from policies import extract_flag, is_safe
from storage import Store
from research import get_research_plan

# Construct absolute paths for data files
LEVELS_PATH = os.path.join(SCRIPT_DIR, "levels.yaml")
SYSTEM_PROMPT_PATH = os.path.join(SCRIPT_DIR, "SYSTEM_PROMPT.txt")
STATE_PATH = os.path.join(SCRIPT_DIR, "state.json")


# Load the system prompt from the dedicated file
try:
    with open(SYSTEM_PROMPT_PATH, "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    print(f"FATAL: SYSTEM_PROMPT.txt not found at {SYSTEM_PROMPT_PATH}")
    sys.exit(1)

def run_level(cfg, research_cfg, store, prev_flag=None, max_steps=12):
    host, port = cfg["host"], cfg["port"]
    user = cfg["user"]
    password = cfg.get("password") or prev_flag
    goal = cfg["goal"]
    flag_regex = cfg["flag_regex"]

    if not password:
        print(f"Error: No password available for level {cfg['level']}. Skipping.")
        return None

    print(f"--- Starting Level {cfg['level']} ---")

    sess = SSHSession(host, port, user, password)
    try:
        sess.connect()
    except Exception as e:
        print(f"SSH connection failed for level {cfg['level']}: {e}")
        print("Check your credentials and network connection.")
        return None

    model = Reasoner()

    # Initial observation
    last_out = sess.read()
    if not last_out.strip():
        last_out = sess.send("pwd") + "\n" + sess.send("ls -la")
    
    pwd = f"/home/{user}" # Initial assumption

    # Research phase
    plan = None
    if research_cfg.get("enable", True):
        plan = get_research_plan(cfg["level"])
        if plan:
            print(f"[Research] New goal: {plan.get('goal')}")
            goal = plan.get("goal") # Override goal from YAML
        else:
            print("[Research] No research plan found. Using original goal.")
    
    print(f"Goal: {goal}")

    steps = 0
    repeated_error_count = 0
    last_error = ""
    history = []

    while steps < max_steps:
        print(f"\n[Step {steps+1}/{max_steps}]")
        steps += 1

        # Seeding command from research plan on first step
        if steps == 1 and plan and plan.get("commands"):
            cmd = plan["commands"][0]
            if not is_safe(cmd):
                cmd = "ls -la" # Fallback
        else:
            tool_ctx = build_tool_context(cfg["level"], goal, pwd, history, flag_regex)
            cmd = model.decide(SYSTEM_PROMPT, tool_ctx).strip()

        print(f"Executing command: {cmd}")

        if cmd.startswith("FLAG_FOUND:"):
            flag = cmd.split("FLAG_FOUND:")[-1].strip()
            print(f"Model declared flag found: {flag}")
            store.save_flag(cfg["level"], flag)
            sess.close()
            return flag

        if cmd.startswith("cd "):
            out = sess.send(cmd)
            pwd_out = sess.send("pwd")
            pwd_lines = pwd_out.strip().splitlines()
            if pwd_lines:
                new_pwd = pwd_lines[-1].strip()
                if new_pwd.startswith("/"):
                    pwd = new_pwd
            last_out = out + "\n" + pwd_out
        else:
            last_out = sess.send(cmd)
        
        history.append((cmd, last_out))

        print("--- Output ---")
        print(last_out.strip())
        print("--- End Output ---")

        # Heuristics for getting stuck
        if "No such file or directory" in last_out:
            if last_error == "No such file or directory":
                repeated_error_count += 1
            else:
                repeated_error_count = 1
                last_error = "No such file or directory"
        else:
            repeated_error_count = 0

        if repeated_error_count >= 2:
            print("[Heuristic] Stuck in 'No such file' loop. Re-evaluating...")
            # Could trigger re-research here if implemented
            repeated_error_count = 0 # Reset counter

        found = extract_flag(last_out, flag_regex)
        if found:
            print(f"Validator found flag: {found}")
            store.save_flag(cfg["level"], found)
            sess.close()
            return found

        time.sleep(1) # Be nice to the server

    sess.close()
    print(f"Level {cfg['level']} max steps reached. Aborting.")
    return None

if __name__ == "__main__":
    try:
        with open(LEVELS_PATH, "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"FATAL: levels.yaml not found at {LEVELS_PATH}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"FATAL: Error parsing levels.yaml: {e}")
        sys.exit(1)

    research_config = config.get("research", {})
    store = Store(path=STATE_PATH)
    store.clear_flags()
    if store.state.get("flags"):
        print("Found existing flags in state.json:", store.state["flags"])

    prev_flag = None
    for entry in config["levels"]:
        level_num = entry['level']
        
        print(f"\n--- Loop Start (Level {level_num}) ---")
        print(f"Initial prev_flag: {prev_flag}")

        password = entry.get("password")
        if entry.get("password_from_prev"):
            stored_flag = store.get_flag(level_num - 1)
            print(f"Password from prev. Stored flag for level {level_num - 1}: {stored_flag}")
            password = stored_flag or prev_flag
        
        print(f"Password for level {level_num}: {password}")

        if not password:
            print(f"Skipping level {level_num} as password is missing.")
            continue

        flag = run_level(entry, research_config, store, prev_flag=password)

        if flag:
            print(f"[SUCCESS] [LEVEL {level_num} COMPLETE] FLAG = {flag}")
            prev_flag = flag
            store.save_flag(level_num, flag)
        else:
            print(f"[FAILED] [LEVEL {level_num} FAILED]")
        
        print(f"End of loop. prev_flag is now: {prev_flag}")
        time.sleep(5) # Add a 5-second delay to be nice to the server
            
    print("\n--- CTF Run Finished ---")
