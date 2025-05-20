#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

# 连接数据库
with connection.cursor() as cursor:
    # 删除迁移记录
    cursor.execute("DELETE FROM django_migrations WHERE app = 'basedata' AND name = '0006_categorymaterialrule_categorymaterialparamrule'")
    cursor.execute("DELETE FROM django_migrations WHERE app = 'basedata' AND name = '0007_auto_20250519_1134'")
    
    print("已成功删除迁移记录。现在可以重新运行 python manage.py makemigrations") 