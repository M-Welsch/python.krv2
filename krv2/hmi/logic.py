from enum import Enum

from krv2.hmi.navigation import Navigation


class States(Enum):
    mode_selection = 0
    navigation = 1


class Logic:
    def __init__(self, hmi):
        self._hmi = hmi
        self._navigation = Navigation()
        self._state = States.navigation
        self.connect_signals()
        self._hmi.start()

    def connect_signals(self):
        self._hmi.enc0.connect(self.on_enc_movement)
        self._hmi.enc0_sw.connect(self.on_enc0_sw_pressed)
        self._hmi.button.connect(self.on_button_pressed)

    def on_enc_movement(self, amount, **kwargs):
        if self._state == States.navigation:
            if amount < 0:
                self._navigation.up()
            elif amount > 0:
                self._navigation.down()

    def on_enc0_sw_pressed(self, **kwargs):
        if self._state == States.navigation:
            self._navigation.into()

    def on_button_pressed(self, name, **kwargs):
        if self._state == States.navigation:
            if name == "button_back":
                self._navigation.out()
