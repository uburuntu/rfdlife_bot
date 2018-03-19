#!/usr/bin/env bash

# Download weights
wget https://pjreddie.com/media/files/tiny-yolo-voc.weights

# Compile *.so
git clone https://github.com/pjreddie/darknet
cd darknet
make -j8
cp libdarknet.so python
