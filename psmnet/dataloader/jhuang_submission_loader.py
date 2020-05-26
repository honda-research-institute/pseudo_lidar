import torch.utils.data as data

from PIL import Image
import os
import os.path
import numpy as np

IMG_EXTENSIONS = [
    '.jpg', '.JPG', '.jpeg', '.JPEG',
    '.png', '.PNG', '.ppm', '.PPM', '.bmp', '.BMP',
]


def is_image_file(filename):
    return any(filename.endswith(extension) for extension in IMG_EXTENSIONS)

def dataloader(filepath, leftdir, rightdir):

  left_fold  = leftdir
  right_fold = rightdir

  image = [img for img in os.listdir(os.path.join(filepath, left_fold))]
  image = sorted(image)


  left_test  = [os.path.join(filepath, left_fold, img) for img in image]
  right_test = [os.path.join(filepath, right_fold, img) for img in image]

  return left_test, right_test
