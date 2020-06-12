# KITTI train
DATADIR=/home/jhuang/KITTI/object/training
LEFTDIR=$DATADIR/image_2
RIGHTDIR=$DATADIR/image_3
CALIBDIR=$DATADIR/calib

# sunny
#DATADIR=/media/jhuang/14e3e381-f8fe-43ea-b8bb-2e21cfe226dd/home/jhuang/U16/sunny_dataset
#LEFTDIR=$DATADIR/left-image-half-size
#RIGHTDIR=$DATADIR/right-image-half-size

# KITTI test
#DATADIR=/media/jhuang/14e3e381-f8fe-43ea-b8bb-2e21cfe226dd/home/jhuang/U16/KITTI/object/testing
#LEFTDIR=$DATADIR/image_2_mini
#RIGHTDIR=$DATADIR/image_3_mini

#DATADIR=/home/jhuang/Downloads/CCSAD/20140527_151946
#LEFTDIR=$DATADIR/left_sub2
#RIGHTDIR=$DATADIR/right_sub2

#DATADIR=/home/jhuang/Downloads/CCSAD/20140604_144706
#LEFTDIR=$DATADIR/left_sub2
#RIGHTDIR=$DATADIR/right_sub2


#python ./psmnet/submission_jhuang.py --loadmodel ./psmnet/pretrained/finetune_300.tar  \
#--datapath $DATADIR/ --leftdir $LEFTDIR --rightdir $RIGHTDIR \
#--save_path $DATADIR/predict_disparity_300 --save_both

python ./psmnet/submission_jhuang.py --loadmodel ./psmnet/pretrained/pretrained_model_KITTI2015.tar   \
--datapath $DATADIR/ --leftdir $LEFTDIR --rightdir $RIGHTDIR \
--save_path $DATADIR/predict_disparity --save_depth --calibdir $CALIBDIR