import os
import django
from django.db import connection

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
try:
    django.setup()
except Exception as e:
    print(f"Django设置错误: {e}")
    exit(1)

# 执行原始SQL查询
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, code, name, price FROM basedata_product WHERE id = 105")
        product = cursor.fetchone()

        if product:
            print(f"产品ID: {product[0]}")
            print(f"产品代码: {product[1]}")
            print(f"产品名称: {product[2]}")
            print(f"产品价格: {product[3]}")

            # 查询参数值
            cursor.execute("""
                SELECT cp.name, ppv.value
                FROM basedata_productparamvalue ppv
                JOIN basedata_categoryparam cp ON ppv.param_id = cp.id
                WHERE ppv.product_id = %s
            """, [product[0]])

            param_values = cursor.fetchall()
            if param_values:
                print("\n产品参数值:")
                for param in param_values:
                    print(f"  - {param[0]}: {param[1]}")
            else:
                print("\n该产品没有参数值")
        else:
            print("找不到ID为105的产品")
except Exception as e:
    print(f"查询错误: {e}")
