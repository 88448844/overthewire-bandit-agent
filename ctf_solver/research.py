import json, os

CACHE = "C:\\Users\\Mfutso Bengo\\Desktop\\mb_projects\\CTF\\ctf_solver\\research_cache.json"

def get_research_plan(level: int) -> dict:
    """
    Loads a pre-computed research plan from the cache for a given level.
    """
    if not os.path.exists(CACHE):
        return None # No cache file found

    with open(CACHE, "r") as f:
        try:
            cache = json.load(f)
        except json.JSONDecodeError:
            return None # Cache is corrupted

    key = f"level_{level}"
    plan = cache.get(key)
    
    if plan:
        print(f"[Research] Found plan for level {level} in cache.")
    else:
        print(f"[Research] No plan found for level {level} in cache.")

    return plan