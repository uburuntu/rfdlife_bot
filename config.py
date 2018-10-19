from os.path import join


# Пути к папкам и файлам
class FileLocation:
    data_dir = 'data/'
    text_dir = data_dir

    cmd_start = join(text_dir, 'cmd_start.html')
    cmd_help = join(text_dir, 'cmd_help.html')
    cmd_help_admin = join(text_dir, 'cmd_help_admin.html')
    acs_answer = join(text_dir, 'acs_answer.html')
    acs_state_answer = join(text_dir, 'acs_state_answer.html')

    camera_error = join(data_dir, 'camera_error.jpg')

    gen_dir = 'gen/'
    camera_dir = join(gen_dir, 'cameras/')

    bot_logs = join(gen_dir, 'bot_logs.txt')
    bot_killed = join(gen_dir, 'they_killed_me.txt')
    user_data = join(gen_dir, 'user_data.json')


chai_subscribers = [
    28006241,  # rmbk
    155094831,  # mix
    78179118,  # tester
    173546332,  # ryba
    122090167,  # isk
    100610568,  # nazar
    49705579,  # krab
    211145131,  # kobz
]

banned_ids = [
    155094831,
    28006241,
]

admin_ids = [
    28006241,
    100610568,
]
