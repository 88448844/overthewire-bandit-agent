import paramiko, time

class SSHSession:
    def __init__(self, host, port, user, password, prompt_timeout=1.0):
        self.host, self.port, self.user, self.password = host, port, user, password
        self.prompt_timeout = prompt_timeout
        self.client = None
        self.chan = None
        self.buffer = ""

    def connect(self):
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(self.host, port=self.port, username=self.user, password=self.password, look_for_keys=False, allow_agent=False, timeout=10)
        self.client = c
        self.chan = c.invoke_shell(term='xterm', width=200, height=50)
        self.chan.settimeout(0.3)
        time.sleep(self.prompt_timeout)
        self._drain()

    def _drain(self):
        out = ""
        while True:
            try:
                chunk = self.chan.recv(65535).decode('utf-8', errors='ignore')
                if not chunk: break
                out += chunk
            except Exception:
                break
        self.buffer += out
        return out

    def send(self, cmd: str):
        self.chan.send(cmd.strip() + "\n")
        time.sleep(self.prompt_timeout)
        return self.read()

    def read(self):
        return self._drain()

    def pwd(self):
        out = self.send("pwd")
        return out

    def close(self):
        try:
            if self.chan: self.chan.close()
        finally:
            if self.client: self.client.close()
