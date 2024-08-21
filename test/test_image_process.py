import cv2

from matplotlib import pyplot

ARDUINO_PNG = "../res/images/v.png"
img = cv2.imread(ARDUINO_PNG, cv2.IMREAD_GRAYSCALE)

thresh = 200

canny = cv2.Canny(img, 255, 0)

canny_bw = cv2.threshold(canny, thresh, 255, cv2.THRESH_BINARY)[1]

f, axes = pyplot.subplots(1, 3)

axes[0].imshow(img)
axes[1].imshow(canny)
axes[2].imshow(canny_bw)

pyplot.show()
