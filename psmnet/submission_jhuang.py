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
import matplotlib.pyplot as plt
import numpy as np
import time
from utils import preprocess 
from models import *
import turbo_colormap_mpl # "turbo" colormap

# 2012 data /media/jiaren/ImageNet/data_scene_flow_2012/testing/

parser = argparse.ArgumentParser(description='PSMNet')
parser.add_argument('--KITTI', default='2015',
                    help='KITTI version')
parser.add_argument('--datapath', default='/scratch/',
                    help='select dir')
parser.add_argument('--leftdir', default='',
                    help='select dir')
parser.add_argument('--rightdir', default='',
                    help='select dir')
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
parser.add_argument('--save_both', action='store_true', help='if true, save both numpy file and png file')
parser.add_argument('--save_depth', action='store_true', help='if true, save both numpy file and png file')
parser.add_argument('--calibdir', default='', help='select dir')
args = parser.parse_args()
args.cuda = not args.no_cuda and torch.cuda.is_available()

torch.manual_seed(args.seed)
if args.cuda:
    torch.cuda.manual_seed(args.seed)

from dataloader import jhuang_submission_loader as DA

test_left_img, test_right_img = DA.dataloader(args.datapath, args.leftdir, args.rightdir)

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
    model.load_state_dict(state_dict['state_dict'], strict=False)

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

def get_bl_t_fl(filepath):
    data = {}
    with open(filepath, 'r') as f:
        for line in f.readlines():
            line = line.rstrip()
            if len(line) == 0: continue
            key, value = line.split(':', 1)
            # The only non-float values in these files are dates, which
            # we don't care about anyway
            try:
                data[key] = np.array([float(x) for x in value.split()])
            except ValueError:
                pass

    return data['P2'][0] * 0.54

def main():
   processed = preprocess.get_transform(augment=False)
   if not os.path.isdir(args.save_path):
       os.makedirs(args.save_path)

   for inx in range(len(test_left_img)):
       imgL_name = test_left_img[inx].split('/')[-1]
       print("Processing {}".format(imgL_name))

       imgL_o = (skimage.io.imread(test_left_img[inx]).astype('float32'))
       imgR_o = (skimage.io.imread(test_right_img[inx]).astype('float32'))
       if len(imgL_o.shape) == 2:
           # Convert grayscale into color
           imgL_o = np.stack((imgL_o,) * 3, axis=-1)
           imgR_o = np.stack((imgR_o,) * 3, axis=-1)
       orig_h, orig_w = imgL_o.shape[0:2]
       do_resize = False
       while orig_h * orig_w >= 2000000:
           # Must fit GPU memory
           do_resize = True
           imgL_o = skimage.transform.resize(imgL_o, (imgL_o.shape[0] // 2, imgL_o.shape[1] // 2),
                                             anti_aliasing=True)
           imgR_o = skimage.transform.resize(imgR_o, (imgR_o.shape[0] // 2, imgR_o.shape[1] // 2),
                                             anti_aliasing=True)
           orig_h, orig_w = imgL_o.shape[0:2]
       if do_resize:
           print("  Resized image to fit GPU memory!")
           if not os.path.isdir(args.datapath + '/resized_left'):
               os.makedirs(args.datapath + '/resized_left')
           skimage.io.imsave(args.datapath + '/resized_left/' + imgL_name,
                             imgL_o.astype('uint8'))

       new_h = int(np.floor(orig_h / 16.0) * 16 + 16)
       new_w = int(np.floor(orig_w / 16.0) * 16 + 16)
       imgL = processed(imgL_o).numpy()
       imgR = processed(imgR_o).numpy()
       # Reorder channels
       imgL = np.reshape(imgL,[1,3,imgL.shape[1],imgL.shape[2]])
       imgR = np.reshape(imgR,[1,3,imgR.shape[1],imgR.shape[2]])

       # pad to (new_h, new_w)
       top_pad = new_h-imgL.shape[2]
       left_pad = new_w-imgL.shape[3]
       imgL = np.lib.pad(imgL,((0,0),(0,0),(top_pad,0),(0,left_pad)),mode='constant',constant_values=0)
       imgR = np.lib.pad(imgR,((0,0),(0,0),(top_pad,0),(0,left_pad)),mode='constant',constant_values=0)

       start_time = time.time()
       pred_disp = test(imgL,imgR)
       print('  time = %.2f' %(time.time() - start_time))

       top_pad   = new_h-imgL_o.shape[0]
       left_pad  = new_w-imgL_o.shape[1]
       img = pred_disp[top_pad:,:-left_pad]

       if args.save_both:
           if not os.path.isdir(args.datapath + '/predict_disparity_img'):
               os.makedirs(args.datapath + '/predict_disparity_img')
           plt.imsave(args.datapath + '/predict_disparity_img/' + imgL_name, img / np.max(img), cmap='turbo', vmin=0,
                      vmax=1)
           np.save(args.save_path + '/' + imgL_name[:-4], img)
       elif args.save_figure:
           skimage.io.imsave(args.save_path+'/'+imgL_name,(img*256).astype('uint16'))
       elif args.save_depth:
           calibfile = os.path.join(args.calibdir, imgL_name.replace('.png', '.txt'))
           bl_t_fl = get_bl_t_fl(calibfile)
           depth_map = bl_t_fl / img
           depth_save_path = os.path.join(args.datapath, 'predict_depth')
           if not os.path.isdir(depth_save_path):
               os.makedirs(depth_save_path)
           skimage.io.imsave(os.path.join(depth_save_path, imgL_name), (depth_map * 256).astype('uint16'))
       else:
           np.save(args.save_path+'/'+imgL_name[:-4], img)



if __name__ == '__main__':
   main()





