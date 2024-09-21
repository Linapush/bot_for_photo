#!/usr/bin/env bash
# запуск через webhook


if [[ $WEBHOOK_URL != "" ]];
  then
    exec uvicorn src.main:create_app --host=$BIND_IP --port=$BIND_PORT
  else
    exec python src/main_polling.py
fi;
