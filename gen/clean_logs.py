import re

logs_file = 'bot_logs.txt'

regexp = '\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2}[^\n]*\n[^\n]*'

with open(logs_file) as file:
    text = file.read()

with open(logs_file, 'w') as file:
    for chunk in re.finditer(regexp, text):
        file.write(chunk.group() + '\n\n')
