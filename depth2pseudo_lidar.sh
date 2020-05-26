DATADIR=/home/jhuang/Downloads/apollo_test/
python ./preprocessing/generate_lidar.py  \
    --calib_dir $DATADIR/ \
    --save_dir $DATADIR/pseudo-lidar_velodyne_new/ \
    --disparity_dir $DATADIR/depth_maps/ \
    --max_high 3 --is_depth
