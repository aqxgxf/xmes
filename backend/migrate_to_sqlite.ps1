# 1. 激活虚拟环境
. venv\Scripts\activate

# 2. 备份原 settings.py
Copy-Item .\settings.py .\settings_mysql.py -Force

# 3. 替换 settings.py 数据库配置为 SQLite
(Get-Content .\settings.py) -replace '(DATABASES\s*=\s*{)[\s\S]*?}', '$1
    ''default'': {
        ''ENGINE'': ''django.db.backends.sqlite3'',
        ''NAME'': BASE_DIR / ''db.sqlite3'',
    }
}' | Set-Content .\settings.py

# 4. 清理旧 SQLite 文件
if (Test-Path .\db.sqlite3) { Remove-Item .\db.sqlite3 -Force }

# 5. 重新生成迁移并迁移
python manage.py makemigrations
python manage.py migrate

# 6. 从 MySQL 导出数据为 JSON
python manage.py dumpdata --natural-foreign --natural-primary --exclude auth.permission --exclude contenttypes --output=all_data.json

# 7. 用 SQLite 配置导入数据
python manage.py loaddata all_data.json

Write-Host "ok!"
