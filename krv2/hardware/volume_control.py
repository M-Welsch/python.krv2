from spidev import SpiDev


class VolumeControl:
    def __init__(self) -> None:
        self._spi = SpiDev()
        self._spi.open(0, 0)

    def set(self, volume_percent: float) -> None:
        volume_8bit = int(volume_percent / 100 * 255)
        self._spi.writebytes([volume_8bit, volume_8bit])

    def close_bus(self) -> None:
        self._spi.close()
