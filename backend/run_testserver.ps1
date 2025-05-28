# PowerShell 脚本：run_testserver.ps1
# 用于本地测试环境启动Django，使用测试数据库 db_test.sqlite3

$env:DJANGO_ENV = "testing"
cd $PSScriptRoot
.\venv\Scripts\activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8001 