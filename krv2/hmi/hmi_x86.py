import sys

from PIL import Image, ImageDraw
from PyQt5 import QtWidgets, uic
from signalslot import Signal

from krv2.hmi.hmi import Hmi
from krv2.common.buttons import Buttons


class HmiX86(Hmi):
    update_display = Signal(args=["index", "image"])

    def __init__(self):
        self._app = QtWidgets.QApplication(sys.argv)
        self._window = Ui()
        self.enc0 = self._window.enc0
        self.enc0_sw = self._window.enc0_sw
        self.enc1 = self._window.enc1
        self.enc1_sw = self._window.enc1_sw
        self.button = self._window.button
        self.connect_internal_signals()

    def connect_internal_signals(self):
        self.update_display.connect(self._window.update_dis)

    def start(self):
        self._app.exec_()

    def show_on_display(self, display_index: int, image: Image.Image):
        self.update_display.emit(index=display_index, image=image)


class Ui(QtWidgets.QMainWindow):
    enc0 = Signal(args=["amount"])
    enc0_sw = Signal()
    enc1 = Signal(args=["amount"])
    enc1_sw = Signal()
    button = Signal(args=["name"])

    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("krv2/mockups/frontplate_conf.ui", self)

        self.pb_Source = self.findChild(QtWidgets.QPushButton, "PB_Source")
        self.pb_PausePlay = self.findChild(QtWidgets.QPushButton, "PB_PausePlay")
        self.pb_Previous = self.findChild(QtWidgets.QPushButton, "PB_Previous")
        self.pb_randRep = self.findChild(QtWidgets.QPushButton, "PB_randRep")
        self.pb_Spare = self.findChild(QtWidgets.QPushButton, "PB_Spare")
        self.pb_Back = self.findChild(QtWidgets.QPushButton, "PB_Back")
        self.pb_Next = self.findChild(QtWidgets.QPushButton, "PB_Next")
        self.pb_enc0_down = self.findChild(QtWidgets.QPushButton, "PB_enc0_down")
        self.pb_enc0_up = self.findChild(QtWidgets.QPushButton, "PB_enc0_up")
        self.pb_enc0_sw = self.findChild(QtWidgets.QPushButton, "PB_enc0_sw")
        self.pb_enc1_up = self.findChild(QtWidgets.QPushButton, "PB_enc1_up")
        self.pb_enc1_down = self.findChild(QtWidgets.QPushButton, "PB_enc1_down")
        self.pb_enc1_sw = self.findChild(QtWidgets.QPushButton, "PB_enc1_sw")

        self.qV_dis0 = self.findChild(QtWidgets.QGraphicsView, "gV_dis0")
        self.qV_dis1 = self.findChild(QtWidgets.QGraphicsView, "gV_dis1")

        self.pb_Source.clicked.connect(self.slot_pb_Source)
        self.pb_PausePlay.clicked.connect(self.slot_pb_PausePlay)
        self.pb_Previous.clicked.connect(self.slot_pb_Previous)
        self.pb_randRep.clicked.connect(self.slot_pb_randRep)
        self.pb_Spare.clicked.connect(self.slot_pb_Spare)
        self.pb_Back.clicked.connect(self.slot_pb_Back)
        self.pb_Next.clicked.connect(self.slot_pb_Next)
        self.pb_enc0_down.clicked.connect(self.slot_pb_enc0_down)
        self.pb_enc0_up.clicked.connect(self.slot_pb_enc0_up)
        self.pb_enc0_sw.clicked.connect(self.slot_pb_enc0_sw)
        self.pb_enc1_up.clicked.connect(self.slot_pb_enc1_up)
        self.pb_enc1_down.clicked.connect(self.slot_pb_enc1_down)
        self.pb_enc1_sw.clicked.connect(self.slot_pb_enc1_sw)

        self.show()

    def update_dis(self, index, image, *args, **kwargs):  # type: ignore
        print("show")
        pix = image.toqpixmap()
        item = QtWidgets.QGraphicsPixmapItem(pix)
        scene = QtWidgets.QGraphicsScene(self)
        scene.addItem(item)
        if index == 0:
            self.qV_dis0.setScene(scene)
        elif index == 1:
            self.qV_dis1.setScene(scene)

    def slot_pb_Source(self):
        print("PB_Source pressed")
        self.button.emit(name=Buttons.next_source)

    def slot_pb_PausePlay(self):
        print("PB_PausePlay pressed")
        self.button.emit(name=Buttons.pause_play)

    def slot_pb_Previous(self):
        print("PB_Previous pressed")
        self.button.emit(name=Buttons.prev_song)

    def slot_pb_Next(self):
        print("PB_Next pressed")
        self.button.emit(name=Buttons.next_song)

    def slot_pb_randRep(self):
        print("PB_randRep pressed")
        self.button.emit(name=Buttons.shuffle_repeat)

    def slot_pb_Spare(self):
        print("PB_Spare pressed")
        self.button.emit(name=Buttons.spare)

    def slot_pb_Back(self):
        print("PB_Back pressed")
        self.button.emit(name=Buttons.back)

    def slot_pb_enc0_up(self):
        print("PB_enc0_up pressed")
        self.enc0.emit(amount=-1)

    def slot_pb_enc0_down(self):
        print("PB_enc0_down pressed")
        self.enc0.emit(amount=1)

    def slot_pb_enc0_sw(self):
        print("PB_enc0_sw pressed")
        self.button.emit(name=Buttons.enc0_sw)

    def slot_pb_enc1_up(self):
        print("PB_enc1_up pressed")
        self.enc1.emit(amount=-1)

    def slot_pb_enc1_down(self):
        print("PB_enc1_down pressed")
        self.enc1.emit(amount=1)

    def slot_pb_enc1_sw(self):
        print("PB_enc1_sw pressed")
        self.button.emit(name=Buttons.enc1_sw)
