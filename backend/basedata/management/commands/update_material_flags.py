from django.core.management.base import BaseCommand
from basedata.models import Product, Material

class Command(BaseCommand):
    help = '更新产品和物料标识，确保物料的is_material设为True，产品的is_material设为False'

    def handle(self, *args, **options):
        # 获取所有被标记为物料的ID
        self.stdout.write("开始更新产品和物料标识...")
        
        # 获取所有通过Material查询集查询到的ID
        material_pks = set(Material.objects.values_list('pk', flat=True))
        material_count = len(material_pks)
        self.stdout.write(f"找到 {material_count} 个物料记录")
        
        # 更新所有物料记录的is_material标志
        updated_materials = Product.objects.filter(pk__in=material_pks, is_material=False).update(is_material=True)
        self.stdout.write(f"更新了 {updated_materials} 个物料记录的标识")
        
        # 更新所有产品记录的is_material标志
        updated_products = Product.objects.exclude(pk__in=material_pks).filter(is_material=True).update(is_material=False)  
        self.stdout.write(f"更新了 {updated_products} 个产品记录的标识")
        
        self.stdout.write(self.style.SUCCESS('更新完成!')) 