#!/bin/bash

FILENAME_KILL="gen/they_killed_me.txt"  # Переменная для убитого бота (из config.py)
FILENAME_LOG="gen/bot_logs.txt"         # Переменная для ведения логов (из config.py)
NOTIFIED_KILL=0

while true; do
    # Eсли бот лежит и не убит нами, или если не запущен вовсе, то воскрешаем его
    if [ -e ${FILENAME} ] && [ ! -e ${FILENAME_KILL} ] || [ $(ps -ef | grep "main.py" | grep -v "grep" | wc -l) -eq "0" ] && [ ! -e ${FILENAME_KILL} ]; then
        printf "Bot is down. Resurrecting it.\n-----------------------------\n\n"
        NOTIFIED_KILL=0
        python3 -u main.py 2>&1 | tee -a -i $FILENAME_LOG
        # Что-то снова упало, уже после воскрешения бота
        printf "\n---------------------------\nBot has been stopped again.\n\n"
        sleep 3s;

    # Если бота убили мы
    elif [ -e ${FILENAME_KILL} ]; then
        if [ ${NOTIFIED_KILL} -eq "0" ]; then
            # Исправляем наши проблемы, меняем кодовое слово и удаляем алёрт файл
            printf "Bot has been killed off.\nPlease restart it manually once you fixed everything or remove $FILENAME_KILL.\n\n"
            NOTIFIED_KILL=1;
        else
            sleep 10s;
        fi
    fi
done
