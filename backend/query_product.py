from basedata.models import Product

product = Product.objects.filter(id=105).first()
print("查询结果:", product)

if product:
    print(f"ID: {product.id}")
    print(f"代码: {product.code}")
    print(f"名称: {product.name}")
    print(f"价格: {product.price}")
else:
    print("未找到ID为105的产品")
