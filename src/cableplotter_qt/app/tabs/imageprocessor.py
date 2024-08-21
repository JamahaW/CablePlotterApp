from enum import Enum
from enum import auto
from pathlib import Path

from PyQt6.QtWidgets import QBoxLayout
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QVBoxLayout
from numpy import ndarray

from cableplotter_qt.ui.comboboxes import EnumComboBox
from cableplotter_qt.ui.displays import ImageDisplay
from cableplotter_qt.ui.sliders import NamedSlider
from cableplotter_qt.ui.sliders import Slider
from cableplotter_qt.ui.tab import Tab
from util.image import makeContourImage
from util.image import readImageBGR


class ViewMode(Enum):
    SOURCE = auto()
    CONTOUR = auto()


class ImageSettings(QGroupBox):
    def __init__(self, filepath: Path, image_display: ImageDisplay) -> None:
        super().__init__("Параметры")
        self.image_display = image_display
        self.low_value_slider = NamedSlider("Low", Slider(255, 0, self._onSliderMoved))
        self.high_value_slider = NamedSlider("High", Slider(255, 0, self._onSliderMoved))
        self.view_mode_combo_box = EnumComboBox(ViewMode, self._onComboBoxChange)

        self.source_image = readImageBGR(filepath)
        self.contour_image = self.makeContourImage()

        self.setLayout(self.makeLayout())

    def makeContourImage(self) -> ndarray:
        return makeContourImage(self.source_image, self.low_value_slider.value(), self.high_value_slider.value())

    def _onSliderMoved(self, _) -> None:
        self.updateImageDisplay(ViewMode.CONTOUR)
        self.contour_image = self.makeContourImage()

    def _onComboBoxChange(self, mode: ViewMode) -> None:
        self.updateImageDisplay(mode)

    def getImage(self, mode: ViewMode) -> ndarray:
        match mode:
            case ViewMode.SOURCE:
                return self.source_image

            case ViewMode.CONTOUR:
                return self.contour_image

    def updateImageDisplay(self, mode: ViewMode) -> None:
        self.view_mode_combo_box.setCurrent(mode)
        self.image_display.setImage(self.getImage(mode))

    def makeLayout(self) -> QBoxLayout:
        L = QVBoxLayout()
        L.addWidget(self.low_value_slider)
        L.addWidget(self.high_value_slider)
        L.addStretch()
        L.addWidget(self.view_mode_combo_box)
        return L


class ImageProcessorTab(Tab):

    def __init__(self, filepath: Path):
        super().__init__(filepath.stem, True)
        self.setLayout(self.makeLayout(filepath))

    def makeLayout(self, filepath: Path) -> QBoxLayout:
        L = QHBoxLayout()
        image_display = ImageDisplay()
        L.addWidget(image_display, 1)
        L.addWidget(ImageSettings(filepath, image_display))

        return L
