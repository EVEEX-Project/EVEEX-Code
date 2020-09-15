from PIL import Image
import matplotlib.pyplot as plt
from color_utils import *

im = Image.open("source.jpg")

pixels = np.asarray(im)
pixels_ycbcr = np.zeros(pixels.shape, dtype=np.uint8)

for i in range(pixels.shape[0]):
    for j in range(pixels.shape[1]):
        pixels_ycbcr[i, j] = rgb2ycbcr(*pixels[i, j])

print(np.min(pixels_ycbcr), np.max(pixels_ycbcr))

#plt.imshow(pixels_ycbcr.astype(np.int64))
plt.imshow(pixels_ycbcr)
plt.show()

plt.imsave("dest.jpg", pixels_ycbcr)