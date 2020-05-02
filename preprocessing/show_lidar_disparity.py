import numpy as np
import matplotlib.pyplot as plt
import sys
img = np.load(sys.argv[1])
img[img<0] = 0
plt.imshow(np.sqrt(img/np.max(img)), cmap='gray', vmin=0, vmax=1); plt.show()
