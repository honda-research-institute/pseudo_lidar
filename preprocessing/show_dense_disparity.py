import numpy as np
import matplotlib.pyplot as plt
import sys
img = np.load(sys.argv[1])
img[img<0] = 0
plt.imshow(img/np.max(img), vmin=0, vmax=1); plt.show()
