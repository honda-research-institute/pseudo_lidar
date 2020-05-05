DATADIR=/home/jhuang/Downloads/apollo_test
python ./psmnet/submission_jhuang.py --loadmodel ./psmnet/pretrained_model_KITTI2015.tar \
--datapath $DATADIR/ --save_path $DATADIR/predict_disparity
