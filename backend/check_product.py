import os
import sys
import django

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from basedata.models import Product, ProductProcessCode

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

def fix_product_process_code_relations():
    logs = []
    for ppc in ProductProcessCode.objects.all():
        # 通过工艺流程关联的产品code查找正确的产品对象
        product_code = ppc.product.code if ppc.product else None
        if not product_code:
            logs.append(f"[跳过] ID={ppc.id} 没有关联产品")
            continue
        # 查找同code的产品
        correct_product = Product.objects.filter(code=product_code).first()
        if not correct_product:
            logs.append(f"[异常] ID={ppc.id} 产品code={product_code} 未找到产品")
            continue
        if ppc.product_id != correct_product.id:
            old_id = ppc.product_id
            ppc.product = correct_product
            ppc.save()
            logs.append(f"[修复] ID={ppc.id} 产品code={product_code} product_id: {old_id} => {correct_product.id}")
        else:
            logs.append(f"[正常] ID={ppc.id} 产品code={product_code} product_id: {ppc.product_id}")
    print("\n".join(logs))

if __name__ == '__main__':
    fix_product_process_code_relations()
