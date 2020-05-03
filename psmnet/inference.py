from __future__ import print_function
import argparse
import os
import random
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim as optim
import torch.utils.data
from torch.autograd import Variable
import torch.nn.functional as F
import skimage
import skimage.io
import skimage.transform
import numpy as np
import time
import math
from utils import preprocess 
from models import *
import matplotlib.pyplot as plt

# 2012 data /media/jiaren/ImageNet/data_scene_flow_2012/testing/

parser = argparse.ArgumentParser(description='PSMNet')
parser.add_argument('--KITTI', default='2015',
                    help='KITTI version')
parser.add_argument('--datapath', default='/scratch/datasets/kitti2015/testing/',
                    help='select model')
parser.add_argument('--loadmodel', default=None,
                    help='loading model')
parser.add_argument('--model', default='stackhourglass',
                    help='select model')
parser.add_argument('--maxdisp', type=int, default=192,
                    help='maxium disparity')
parser.add_argument('--no-cuda', action='store_true', default=False,
                    help='enables CUDA training')
parser.add_argument('--seed', type=int, default=1, metavar='S',
                    help='random seed (default: 1)')
parser.add_argument('--save_path', type=str, default='finetune_1000', metavar='S',
                    help='path to save the predict')
parser.add_argument('--save_figure', action='store_true', help='if true, save the numpy file, not the png file')
args = parser.parse_args()
args.cuda = not args.no_cuda and torch.cuda.is_available()

torch.manual_seed(args.seed)
if args.cuda:
    torch.cuda.manual_seed(args.seed)

if args.KITTI == '2015':
   from dataloader import KITTI_submission_loader as DA
else:
   from dataloader import KITTI_submission_loader2012 as DA  


if args.model == 'stackhourglass':
    model = stackhourglass(args.maxdisp)
elif args.model == 'basic':
    model = basic(args.maxdisp)
else:
    print('no model')

model = nn.DataParallel(model, device_ids=[0])
model.cuda()

if args.loadmodel is not None:
    state_dict = torch.load(args.loadmodel)
    model.load_state_dict(state_dict['state_dict'])

print('Number of model parameters: {}'.format(sum([p.data.nelement() for p in model.parameters()])))

def test(imgL,imgR):
        model.eval()

        if args.cuda:
           imgL = torch.FloatTensor(imgL).cuda()
           imgR = torch.FloatTensor(imgR).cuda()     

        imgL, imgR= Variable(imgL), Variable(imgR)

        with torch.no_grad():
            output = model(imgL,imgR)
        output = torch.squeeze(output)
        pred_disp = output.data.cpu().numpy()

        return pred_disp


def main():
   processed = preprocess.get_transform(augment=False)
   if not os.path.isdir(args.save_path):
       os.makedirs(args.save_path)

   img_dir = "/home/jhuang/docker/pseudo_lidar/psmnet/flickr"
   l_fnames = [f for f in os.listdir(img_dir) if f.endswith("_L.png")]
   do_resize = False
   for l_fname in l_fnames:
       print("Processing {} ...".format(l_fname))
       r_fname = l_fname.replace("_L.png", "_R.png")
       imgL_o = (skimage.io.imread(os.path.join(img_dir, l_fname)).astype('float32'))
       imgR_o = (skimage.io.imread(os.path.join(img_dir, r_fname)).astype('float32'))
       if do_resize:
           imgL_o = skimage.transform.resize(imgL_o, (384, 1248), anti_aliasing = True)
           imgR_o = skimage.transform.resize(imgR_o, (384, 1248), anti_aliasing=True)
       else:
           orig_h, orig_w = imgL_o.shape[0:2]
           if orig_h*orig_w>=2000000:
               print("Skipping due to large image size!")
               continue # out of memory
           new_h = int(np.floor(orig_h / 16.0) * 16 + 16)
           new_w = int(np.floor(orig_w / 16.0) * 16 + 16)
           print(new_h)
           print(new_w)
       imgL = processed(imgL_o).numpy()
       imgR = processed(imgR_o).numpy()
       imgL = np.reshape(imgL,[1,3,imgL.shape[1],imgL.shape[2]])
       imgR = np.reshape(imgR,[1,3,imgR.shape[1],imgR.shape[2]])

       # pad to (384, 1248)
       if do_resize:
           top_pad = 384-imgL.shape[2]
           left_pad = 1248-imgL.shape[3]
           imgL = np.lib.pad(imgL,((0,0),(0,0),(top_pad,0),(0,left_pad)),mode='constant',constant_values=0)
           imgR = np.lib.pad(imgR,((0,0),(0,0),(top_pad,0),(0,left_pad)),mode='constant',constant_values=0)
       else:
           top_pad = new_h - imgL.shape[2]
           left_pad = new_w - imgL.shape[3]
           imgL = np.lib.pad(imgL, ((0, 0), (0, 0), (top_pad, 0), (0, left_pad)), mode='constant', constant_values=0)
           imgR = np.lib.pad(imgR, ((0, 0), (0, 0), (top_pad, 0), (0, left_pad)), mode='constant', constant_values=0)

       start_time = time.time()
       pred_disp = test(imgL,imgR)
       print('time = %.2f' %(time.time() - start_time))

       if do_resize:
           top_pad   = 384-imgL_o.shape[0]
           left_pad  = 1248-imgL_o.shape[1]
           img = pred_disp[top_pad:,:-left_pad]
       else:
           top_pad = new_h - imgL_o.shape[0]
           left_pad = new_w - imgL_o.shape[1]
           img = pred_disp[top_pad:, :-left_pad]
       #skimage.io.imshow(img.astype('uint8'))
       #skimage.io.show()
       save_name = l_fname.replace("_L.png", ".png")
       if args.save_figure:
           #skimage.io.imsave(args.save_path+'/'+save_name,(img*256).astype('uint16'))
           plt.imsave(args.save_path+'/'+save_name, img / np.max(img), cmap='inferno', vmin=0, vmax=1)
       else:
           pass
           #np.save(args.save_path+'/'+test_left_img[inx].split('/')[-1][:-4], img)

if __name__ == '__main__':
   main()






