#DATADIR=/home/jhuang/Downloads/apollo_test/ #bl==0.7
#DATADIR=/media/jhuang/14e3e381-f8fe-43ea-b8bb-2e21cfe226dd/home/jhuang/U16/sunny_dataset #bl=0.54
DATADIR=/home/jhuang/Downloads/CCSAD/1 #bl==0.504

python ./preprocessing/generate_lidar.py  \
    --calib_dir $DATADIR/ \
    --save_dir $DATADIR/pseudo-lidar_velodyne/ \
    --disparity_dir $DATADIR/predict_disparity \
    --baseline 0.54 --max_high 3