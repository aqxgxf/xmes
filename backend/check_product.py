import os
import sys
import django

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from basedata.models import Product

# 查询ID为105的产品
product = Product.objects.filter(id=105).first()

if product:
    print(f'产品ID: {product.id}')
    print(f'产品代码: {product.code}')
    print(f'产品名称: {product.name}')
    print(f'产品价格: {product.price}')
    print(f'产品类别ID: {product.category_id}')

    # 查询参数值
    param_values = product.param_values.all()
    if param_values:
        print('\n产品参数值:')
        for pv in param_values:
            print(f'  - {pv.param.name}: {pv.value}')
    else:
        print('\n该产品没有参数值')
else:
    print('找不到ID为105的产品')
