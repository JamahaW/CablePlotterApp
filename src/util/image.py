from os import PathLike

import cv2
from numpy import ndarray


def readImageBGR(filename: PathLike | str, /) -> ndarray:
    return cv2.imread(filename, cv2.IMREAD_COLOR)


def saveImageBGR(filename: PathLike | str, image: ndarray, /) -> None:
    cv2.imwrite(filename, image)


def makeContourImage(image: ndarray, low: int, high: int, /) -> ndarray:
    return cv2.Canny(image, low, high, L2gradient=False)
