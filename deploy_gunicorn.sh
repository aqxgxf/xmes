#!/bin/bash
# 启动Django后端的Gunicorn服务

cd "$(dirname "$0")/backend"

# 激活虚拟环境（自动判断平台）
if [ -f venv/Scripts/activate ]; then
  source venv/Scripts/activate
else
  source venv/bin/activate
fi

export PYTHONPATH=$(pwd)

# Gunicorn启动参数
GUNICORN_CMD="nohup gunicorn wsgi:application \
  --bind 127.0.0.1:8900 \
  --workers 4 \
  --timeout 120 \
  --log-level info \
  --access-logfile ../logs/gunicorn.log \
  --error-logfile ../logs/gunicorn.log \
  > ../logs/gunicorn_stdout.log 2>&1 &"

echo "启动Gunicorn: $GUNICORN_CMD"
eval $GUNICORN_CMD 