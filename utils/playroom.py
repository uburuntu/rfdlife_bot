# !/usr/bin/env python
# _*_ coding: utf-8 _*_

import cv2

import config
from utils.common_utils import curr_time, my_bot


class CamerasView:
    def get_stream_link(self):
        return NotImplemented

    def get_file_name(self):
        return config.FileLocation.gen_dir + self.__class__.__name__ + '.jpg'

    def get_file_name_orig(self):
        return config.FileLocation.gen_dir + self.__class__.__name__ + '_orig.jpg'

    def show_camera(self):
        capture = cv2.VideoCapture(self.get_stream_link())
        while True:
            ret, frame = capture.read()
            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) == 27:
                exit(0)

    def create_frame(self):
        capture = cv2.VideoCapture(self.get_stream_link())
        ret, frame = capture.read()
        if ret:
            cv2.imwrite(self.get_file_name_orig(), frame)
        capture.release()
        return ret

    def get_image(self):
        ret = self.create_frame()
        if ret:
            self.draw_info()
            return self.get_file_name()
        return config.FileLocation.camera_error

    def draw_info(self):
        frame = cv2.imread(self.get_file_name_orig())
        text = curr_time()
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 255, 1)
        cv2.imwrite(self.get_file_name(), frame)


class PlayroomView(CamerasView):
    def get_stream_link(self):
        return 'http://video.local.rfdyn.ru:10090/video10.mjpg'


class KitchenView(CamerasView):
    def get_stream_link(self):
        return 'http://video.local.rfdyn.ru:10090/video8.mjpg'


class CameraNView(CamerasView):
    def __init__(self, n='10'):
        super().__init__()
        if n.isdigit():
            self.n = n
        else:
            self.n = 10

    def get_stream_link(self):
        return f'http://video.local.rfdyn.ru:10090/video{self.n}.mjpg'


def playroom_show(message):
    my_bot.send_chat_action(message.chat.id, 'upload_photo')
    with open(PlayroomView().get_image(), 'rb') as img:
        my_bot.send_photo(message.chat.id, img, caption='', reply_to_message_id=message.message_id)


def kitchen_show(message):
    my_bot.send_chat_action(message.chat.id, 'upload_photo')
    with open(KitchenView().get_image(), 'rb') as img:
        my_bot.send_photo(message.chat.id, img, caption='', reply_to_message_id=message.message_id)


def camera_n_show(message):
    my_bot.send_chat_action(message.chat.id, 'upload_photo')
    with open(CameraNView(message.text.split()[-1]).get_image(), 'rb') as img:
        my_bot.send_photo(message.chat.id, img, caption='', reply_to_message_id=message.message_id)


if __name__ == '__main__':
    PlayroomView().show_camera()
