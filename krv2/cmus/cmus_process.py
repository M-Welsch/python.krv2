from subprocess import Popen, PIPE


class CmusProcess:
    def __init__(self):
        self._process = None

    def start(self):
        cmd = "cmus --listen /home/pi/.config/cmus/socket".split()
        self._process = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)

    def write(self, message):
        self._process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
        self._process.stdin.flush()

    # untested!
    def read(self) -> str:
        return self._process.stdout.readline().decode("utf-8").strip()

    def terminate(self):
        self._process.terminate()
