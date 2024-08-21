from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage
from PyQt6.QtGui import QPixmap
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QLabel
from numpy import ndarray


class ImageDisplay(QLabel):

    def __init__(self, align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter):
        super().__init__("Image")
        self.setScaledContents(True),
        self.setMinimumSize(600, 600),
        self.setAlignment(align)
        self.setStyleSheet("image-position:right center;")

    def setImage(self, image: Optional[ndarray]):
        if image is None:
            return

        width, height, *args = image.shape
        fmt = QImage.Format.Format_BGR888 if len(args) else QImage.Format.Format_Grayscale8
        pixmap = QPixmap.fromImage(QImage(image.data, width, height, fmt))
        self.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def resizeEvent(self, e: QResizeEvent) -> None:
        self.setPixmap(self.pixmap().scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation))
        super().resizeEvent(e)


class Label(QLabel):

    def __init__(self):
        super().__init__()
        self.pixmap_width: int = 1
        self.pixmap_height: int = 1

    def setPixmap(self, pm: QPixmap) -> None:
        self.pixmap_width = pm.width()
        self.pixmap_height = pm.height()

        self.updateMargins()
        super().setPixmap(pm)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.updateMargins()
        super().resizeEvent(a0)

    def updateMargins(self):
        if self.pixmap() is None:
            return

        pixmap_width = self.pixmap().width()
        pixmap_height = self.pixmap().height()

        if pixmap_width <= 0 or pixmap_height <= 0:
            return

        w, h = self.width(), self.height()

        if w <= 0 or h <= 0:
            return

        if w * pixmap_height > h * pixmap_width:
            m = int((w - (pixmap_width * h / pixmap_height)) / 2)
            self.setContentsMargins(m, 0, m, 0)

        else:
            m = int((h - (pixmap_height * w / pixmap_width)) / 2)
            self.setContentsMargins(0, m, 0, m)


class ImageLabel(QLabel):
    def __init__(self, imagePath):
        super().__init__()
        self.pixmap = QPixmap(imagePath)

    def resizeEvent(self, e: QResizeEvent) -> None:
        self.setPixmap(self.pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio))
        super().resizeEvent(e)


class ValueDisplay(QLabel):

    def updateValue(self, value: int) -> None:
        self.setText(f"{self.title}: {value}")

    def __init__(self, title: str, value: int) -> None:
        super().__init__()
        self.title = title
        self.updateValue(value)
