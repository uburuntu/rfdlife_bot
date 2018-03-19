import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'yolo/darknet/python'))

import darknet as dn

if __name__ == '__main__':
    dn.set_gpu(0)
    net = dn.load_net("yolo/darknet/cfg/yolo-thor.cfg", "yolo/tiny-yolo-voc.weights", 0)
    meta = dn.load_meta("yolo/darknet/cfg/thor.data")
    r = dn.detect(net, meta, "yolo/darknet/data/bedroom.jpg")
    print(r)

    # And then down here you could detect a lot more images like:
    r = dn.detect(net, meta, "yolo/darknet/data/eagle.jpg")
    print(r)
    r = dn.detect(net, meta, "yolo/darknet/data/giraffe.jpg")
    print(r)
    r = dn.detect(net, meta, "yolo/darknet/data/horses.jpg")
    print(r)
    r = dn.detect(net, meta, "yolo/darknet/data/person.jpg")
    print(r)
