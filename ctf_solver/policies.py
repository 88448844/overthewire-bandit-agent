import re

ALLOWED = {"ls","cd","cat","file","strings","find","grep","head","tail","wc","stat","xxd","du","pwd","echo", "sort", "uniq"}

def is_safe(cmd: str) -> bool:
    if not cmd.strip(): return False
    if "\n" in cmd or ";" in cmd or "&&" in cmd or "|" in cmd: return False
    tok = cmd.strip().split()[0]
    if tok not in ALLOWED: return False
    banned = ("sudo","rm ","chmod ","scp","ssh ","curl","wget","apt","yum","nc ","ncat","tar","unzip","zip","vi","nano","ed","python","perl","bash")
    return not any(b in cmd for b in banned)

def extract_flag(text: str, regex: str):
    m = re.search(regex, text.strip())
    return m.group(0) if m else None
