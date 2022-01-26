import sys

from PIL import ImageDraw
from PIL.Image import Image
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap
from signalslot import Signal

from krv2.hmi.hmi import Hmi


class HmiX86(Hmi):
    def __init__(self):
        self._app = QtWidgets.QApplication(sys.argv)
        self._window = Ui()
        self.enc0 = self._window.enc0
        self.enc0_sw = self._window.enc0_sw
        self.enc1 = self._window.enc1
        self.enc1_sw = self._window.enc1_sw
        self.button = self._window.button

    @property
    def dis0(self) -> ImageDraw.Draw:
        im = Image()
        return ImageDraw.Draw(im)

    @property
    def dis1(self) -> ImageDraw.Draw:
        im = Image()
        return ImageDraw.Draw(im)

    def start(self):
        self._app.exec_()


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

    def update_dis0(self):
        pix = QPixmap("pil.png")
        item = QtWidgets.QGraphicsPixmapItem(pix)
        scene = QtWidgets.QGraphicsScene(self)
        scene.addItem(item)
        self.qV_dis0.setScene(scene)

    def update_dis1(self):
        pix = QPixmap("pil.png")
        item = QtWidgets.QGraphicsPixmapItem(pix)
        scene = QtWidgets.QGraphicsScene(self)
        scene.addItem(item)
        self.qV_dis1.setScene(scene)

    def slot_pb_Source(self):
        print("PB_Source pressed")

    def slot_pb_PausePlay(self):
        print("PB_PausePlay pressed")
        self.update_dis0()
        self.update_dis1()

    def slot_pb_Previous(self):
        print("PB_Previous pressed")

    def slot_pb_Next(self):
        print("PB_Next pressed")

    def slot_pb_randRep(self):
        print("PB_randRep pressed")

    def slot_pb_Spare(self):
        print("PB_Spare pressed")

    def slot_pb_Back(self):
        print("PB_Back pressed")
        self.button.emit(name="button_back")

    def slot_pb_enc0_up(self):
        print("PB_enc0_up pressed")
        self.enc0.emit(amount=-1)

    def slot_pb_enc0_down(self):
        print("PB_enc0_down pressed")
        self.enc0.emit(amount=1)

    def slot_pb_enc0_sw(self):
        print("PB_enc0_sw pressed")
        self.enc0_sw.emit()

    def slot_pb_enc1_up(self):
        print("PB_enc1_up pressed")
        self.enc1.emit(amount=-1)

    def slot_pb_enc1_down(self):
        print("PB_enc1_down pressed")
        self.enc1.emit(amount=1)

    def slot_pb_enc1_sw(self):
        print("PB_enc1_sw pressed")
        self.enc1_sw.emit()
