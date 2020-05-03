# Install
```bash
workon psmnet
# pip install torch==0.4.0 torchvision==0.2.0
# ip install skikit-image
pip install -r psmnet/requirements.txt
```

# Use PSMNet to predict dense disparity
```bash
python ./psmnet/submission.py \
    --loadmodel ./psmnet/pretrained_model_KITTI2015.tar \
    --datapath ./KITTI/object/training/ \
    --save_path ./KITTI/object/training/predict_disparity

python ./psmnet/inference.py \
    --loadmodel ./psmnet/pretrained_model_KITTI2015.tar \
    --save_path ./psmnet/predict_disparity \
    --save_figure
```

# Dense disparity => Psuedo-point cloud
```bash
python ./preprocessing/generate_lidar.py  \
    --calib_dir ./KITTI/object/training/calib/ \
    --save_dir ./KITTI/object/training/pseudo-lidar_velodyne/ \
    --disparity_dir ./KITTI/object/training/predict_disparity \
    --max_high 1
```