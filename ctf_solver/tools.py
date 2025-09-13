import textwrap

def build_tool_context(level, goal, pwd, history, flag_regex):
    
    # Format history
    formatted_history = ""
    if history:
        formatted_history = "\n\n## Command History\n"
        for cmd, out in history:
            formatted_history += f"$ {cmd}\n{out}\n"
    
    # Truncate history if it's too long
    if len(formatted_history) > 2000:
        formatted_history = formatted_history[-2000:]

    return textwrap.dedent(f'''
    Context:
    - Current level: {level}
    - Goal: {goal}
    - Working directory (last known): {pwd}{formatted_history}
    - Allowed commands: ls, cd, cat, file, strings, find, grep, head, tail, wc, stat, xxd, du, pwd, echo
    - Flag regex: {flag_regex}

    Respond with ONE next command or FLAG_FOUND:<flag>
    ''').strip()