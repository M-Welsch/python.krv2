from krv2.hardware.pin_interface import Pins

try:
    from Encoder import Encoder
except RuntimeError:
    print("RPi.GPIO is not available. Switching to mockup mode")
    # from krv2.mockups.mockupgpio import GPIO


class DrehDrueck:
    def __init__(self) -> None:
        pins = Pins()
        self._enc0 = Encoder(pins.enc0["a"], pins.enc0["b"])
        self._enc1 = Encoder(pins.enc1["a"], pins.enc1["b"])

    def read(self) -> tuple:
        val_enc0 = self._enc0.read()
        val_enc1 = self._enc1.read()
        return val_enc0, val_enc1
