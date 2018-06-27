# _*_ coding: utf-8 _*_


# Пути к папкам и файлам
class FileLocation:
    data_dir = 'data/'
    text_dir = data_dir

    cmd_start = text_dir + 'cmd_start.html'
    cmd_help = text_dir + 'cmd_help.html'
    cmd_help_admin = text_dir + 'cmd_help_admin.html'
    acs_answer = text_dir + 'acs_answer.html'
    acs_state_answer = text_dir + 'acs_state_answer.html'

    camera_error = data_dir + 'camera_error.jpg'

    gen_dir = 'gen/'
    dump_dir = gen_dir + 'dump/'

    bot_logs = gen_dir + 'bot_logs.txt'
    bot_killed = gen_dir + 'they_killed_me.txt'
    user_data = gen_dir + 'user_data.json'


chai_subscribers = [28006241,  # rmbk
                    155094831,  # mix
                    78179118,  # tester
                    173546332,  # ryba
                    122090167,  # isk
                    100610568,  # nazar
                    49705579,  # krab
                    211145131]  # kobz

admin_ids = [28006241, 155094831]  # , 173546332, 100610568]
