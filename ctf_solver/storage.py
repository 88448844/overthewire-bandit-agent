import json, os

class Store:
    def __init__(self, path="state.json"):
        self.path = path
        self.state = {"flags": {}}
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    self.state = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {path}. Starting with empty state.")
                self.state = {"flags": {}}

    def save_flag(self, level, flag):
        if "flags" not in self.state:
            self.state["flags"] = {}
        self.state["flags"][str(level)] = flag
        with open(self.path, "w") as f:
            json.dump(self.state, f, indent=2)

    def get_flag(self, level):
        return self.state.get("flags", {}).get(str(level))

    def clear_flags(self):
        self.state["flags"] = {}
        with open(self.path, "w") as f:
            json.dump(self.state, f, indent=2)
