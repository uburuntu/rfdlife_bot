import os

import cv2
from telebot.types import InlineKeyboardButton as Button, InlineKeyboardMarkup, InputMediaPhoto

import config
from utils.common_utils import code, curr_time, my_bot


class CameraView:
    def __init__(self, camera_num):
        self.camera_num = camera_num

    def get_stream_link(self):
        return 'http://video.local.rfdyn.ru:10090/video{}.mjpg'.format(str(self.camera_num))

    def get_file_name(self):
        return os.path.join(config.FileLocation.camera_dir, 'camera_' + str(self.camera_num) + '.jpg')

    def get_file_name_orig(self):
        return os.path.join(config.FileLocation.camera_dir, 'camera_' + str(self.camera_num) + '_orig.jpg')

    def create_frame(self):
        capture = cv2.VideoCapture(self.get_stream_link())
        ret, frame = capture.read()
        if ret:
            cv2.imwrite(self.get_file_name_orig(), frame)
        capture.release()
        return ret

    def draw_info(self):
        frame = cv2.imread(self.get_file_name_orig())
        cv2.putText(frame, curr_time(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 255, 1)
        cv2.imwrite(self.get_file_name(), frame)

    def get_image(self):
        ret = self.create_frame()
        if ret:
            self.draw_info()
            return self.get_file_name()
        return config.FileLocation.camera_error


def camera_keyboard(camera_num):
    def border(num):
        return 12 if num < 4 else 4 if num > 12 else num

    keyboard = InlineKeyboardMarkup()
    keyboard.add(Button(text='⬅️', callback_data='camera_{}'.format(border(camera_num - 1))),
                 Button(text='🔄', callback_data='camera_{}'.format(camera_num)),
                 Button(text='➡️', callback_data='camera_{}'.format(border(camera_num + 1))))
    return keyboard


def camera_show(message, camera_num):
    my_bot.send_chat_action(message.chat.id, 'upload_photo')
    with open(CameraView(camera_num).get_image(), 'rb') as img:
        my_bot.send_photo(message.chat.id, img, caption=f'Камера #{camera_num}',
                          reply_markup=camera_keyboard(camera_num), reply_to_message_id=message.message_id)


def playroom_show(message):
    camera_show(message, 10)


def kitchen_show(message):
    camera_show(message, 8)


def camera_n_show(message):
    split = message.text.split()
    if len(split) == 2 and split[1].isdigit():
        camera_show(message, int(split[1]))
    else:
        my_bot.reply_to(message, ('Использование: {}, N=4..12').format(code('/camera [N]')))


def update_camera(call):
    message = call.message
    camera_num = int(call.data.replace('camera_', ''))

    with open(CameraView(camera_num).get_image(), 'rb') as img:
        my_bot.edit_message_media(chat_id=message.chat.id, message_id=message.message_id,
                                  media=InputMediaPhoto(img, caption=f'Камера #{camera_num}'),
                                  reply_markup=camera_keyboard(camera_num))
        my_bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text='✅  Обновлено')
