class SMBus:
    def __init__(self, bus: int) -> None:
        print("SMBUS Mockup: pretending to open bus {}".format(bus))
        self._bus = bus

    def read_i2c_block_data(self, adress: int, bus: int) -> None:
        pass
