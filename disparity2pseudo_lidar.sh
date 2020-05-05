DATADIR=/home/jhuang/Downloads/apollo_test/
python ./preprocessing/generate_lidar.py  \
    --calib_dir $DATADIR/ \
    --save_dir $DATADIR/pseudo-lidar_velodyne/ \
    --disparity_dir $DATADIR/predict_disparity \
    --max_high 1
