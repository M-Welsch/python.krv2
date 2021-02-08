from Encoder import Encoder


class DrehDrueck:
    def __init__(self):
        self._enc = Encoder(12,13)

    def read(self):
        self._enc.read()