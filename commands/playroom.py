# !/usr/bin/env python
# _*_ coding: utf-8 _*_

import cv2

import config
from utils import my_bot, curr_time


class PlayroomView:
    def __init__(self, use_yolo=False):
        self.camera_link = 'http://video.local.rfdyn.ru:10090/video10.mjpg'
        self.capture = cv2.VideoCapture(self.camera_link)

        self.use_yolo = use_yolo

        if self.use_yolo and False:
            import os, sys
            darknet_dir = os.path.join(os.path.dirname(__file__), 'yolo', 'darknet', 'python')
            sys.path.append(darknet_dir)
            import darknet as dn

            dn.set_gpu(0)
            self.dn_net = dn.load_net(
                b"/home/ramzan.bekbulatov/study/rfdlife_bot/commands/yolo/darknet/cfg/tiny-yolo-voc.cfg",
                b"/home/ramzan.bekbulatov/study/rfdlife_bot/commands/yolo/tiny-yolo-voc.weights", 0)

            self.dn_meta = dn.load_meta(b"/home/ramzan.bekbulatov/study/rfdlife_bot/commands/yolo/darknet/cfg/voc.data")

    @staticmethod
    def detect():
        # TODO: implement
        # r = dn.detect(net, meta, b"/home/ramzan.bekbulatov/study/rfdlife_bot/commands/yolo/darknet/data/eagle.jpg")
        # print(r)
        # r = dn.detect(net, meta, b"/home/ramzan.bekbulatov/study/rfdlife_bot/commands/yolo/darknet/data/giraffe.jpg")
        # print(r)
        # r = dn.detect(net, meta, b"/home/ramzan.bekbulatov/study/rfdlife_bot/commands/yolo/darknet/data/horses.jpg")
        # print(r)
        # r = dn.detect(net, meta, b"/home/ramzan.bekbulatov/study/rfdlife_bot/commands/yolo/darknet/data/person.jpg")
        # print(r)
        return [(b'person', 0.729792594909668, (224.68553161621094, 227.27330017089844,
                                                110.40947723388672, 268.6751403808594)),
                (b'sheep', 0.6032776236534119, (477.4401550292969, 251.57388305664062,
                                                128.32411193847656, 191.139404296875)),
                (b'dog', 0.5349644422531128, (126.95857238769531, 303.6556091308594,
                                              140.033203125, 77.02155303955078))]

    def show_camera(self):
        while True:
            ret, frame = self.capture.read()
            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) == 27:
                exit(0)

    def create_frame(self):
        ret, frame = self.capture.read()
        if ret:
            cv2.imwrite(config.FileLocation.last_frame_orig, frame)

    def get_image(self):
        self.create_frame()
        self.draw_info()
        return open(config.FileLocation.last_frame, 'rb')

    def draw_info(self):
        detections = []
        if self.use_yolo:
            detections = self.detect()

        frame = cv2.imread(config.FileLocation.last_frame_orig)
        for detection in detections:
            object_class = str(detection[0])[2:-1]
            coords = detection[2]
            x1 = int(coords[0] - coords[2] / 2)
            x2 = int(coords[0] + coords[2] / 2)
            y1 = int(coords[1] - coords[3] / 2)
            y2 = int(coords[1] + coords[3] / 2)
            color = (255, 0, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, object_class, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        text = curr_time()
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 255, 1)

        cv2.imwrite(config.FileLocation.last_frame, frame)


playroom_view = PlayroomView()


def playroom_show(message):
    my_bot.send_chat_action(message.chat.id, 'upload_photo')
    img = playroom_view.get_image()
    my_bot.send_photo(message.chat.id, img, caption=curr_time() + '')
    img.close()


if __name__ == '__main__':
    playroom_view.show_camera()
