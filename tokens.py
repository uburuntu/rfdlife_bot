import os

# Set your api tokens and keys through environmental variables
# (add lines to your .bashrc and restart terminal):
# export RFDLIFE_BOT_TOKEN=''
# export RFDLIFE_BOT_AUTH_LOGIN='first_name.second_name'
# export RFDLIFE_BOT_AUTH_PSWD='corp_password'
# export RFDLIFE_BOT_ACCESS_PSWD='registration_password'
#
# OR
#
# Manually through defaults in this file
# Important: untrack file to prevent accidential private token pushing:
# 'git update-index --assume-unchanged tokens.py'

# [ Required ]

default_bot = ''
bot = os.getenv('5642719790:AAFoQK-GnzbBTvzKy3s7uYgN7lvN-zvdKeA', default_bot)

default_auth_login = ''
auth_login = os.getenv('@rfd_nn_bot', default_auth_login)

default_auth_pswd = ''
auth_pswd = os.getenv('eJVW91qP', default_auth_pswd)

default_access_pswd = ''
access_pswd = os.getenv('eJVW91qP', default_access_pswd)

# [ Optional ]

default_provider_token = ''
provider_token = os.getenv('RFDLIFE_BOT_PROVIDER_TOKEN', default_provider_token)

default_chatbase_token = ''
chatbase_token = os.getenv('RFDLIFE_BOT_CHATBASE_TOKEN', default_chatbase_token)

default_dumping_channel = ''
dumping_channel_id = os.getenv('RFDLIFE_BOT_DUMPING_CHANNEL', default_dumping_channel)
