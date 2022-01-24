from signalslot import Signal

from krv2.hmi.hmi import Hmi


class HmiArm(Hmi):
    enc0 = Signal(args=['amount'])
    enc0_sw = Signal()
    enc1 = Signal(args=['amount'])
    enc1_sw = Signal()
    button = Signal(args=['name'])

    def __init__(self):
        pass

    def connect_signals(self):
        pass

    def start(self):
        pass
