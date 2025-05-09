from django.core.management.base import BaseCommand
from usermgmt.models import Menu
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = '初始化系统菜单'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化系统菜单...')
        
        # 删除所有现有菜单以避免重复
        Menu.objects.all().delete()
        
        # 确保存在超级管理员组
        admin_group, _ = Group.objects.get_or_create(name='超级管理员')
        
        # 创建基础数据菜单
        base_data = Menu.objects.create(name='基础数据', path='')
        company = Menu.objects.create(name='公司管理', path='companies', parent=base_data)
        product_category = Menu.objects.create(name='产品类别', path='product-categories', parent=base_data)
        category_param = Menu.objects.create(name='类别参数', path='category-params', parent=base_data)
        product = Menu.objects.create(name='产品管理', path='products', parent=base_data)
        material = Menu.objects.create(name='物料管理', path='materials', parent=base_data)
        process = Menu.objects.create(name='工序管理', path='processes', parent=base_data)
        process_code = Menu.objects.create(name='工艺流程', path='process-codes', parent=base_data)
        product_process_code = Menu.objects.create(name='产品工艺关联', path='product-process-codes', parent=base_data)
        process_detail = Menu.objects.create(name='工艺流程明细', path='process-details', parent=base_data)
        bom = Menu.objects.create(name='BOM管理', path='boms', parent=base_data)
        bom_detail = Menu.objects.create(name='BOM明细', path='bom-details', parent=base_data)
        unit_mgmt = Menu.objects.create(name='单位管理', path='units', parent=base_data)
        
        # 创建系统管理菜单
        sys_mgmt = Menu.objects.create(name='系统管理', path='')
        user_mgmt = Menu.objects.create(name='用户管理', path='users', parent=sys_mgmt)
        group_mgmt = Menu.objects.create(name='用户组管理', path='groups', parent=sys_mgmt)
        menu_mgmt = Menu.objects.create(name='菜单管理', path='menus', parent=sys_mgmt)
        data_import = Menu.objects.create(name='数据导入', path='data-import', parent=sys_mgmt)
        
        # 创建销售管理菜单
        sales_mgmt = Menu.objects.create(name='销售管理', path='')
        order_mgmt = Menu.objects.create(name='订单管理', path='orders', parent=sales_mgmt)
        
        # 创建生产管理菜单
        production_mgmt = Menu.objects.create(name='生产管理', path='')
        workorder_mgmt = Menu.objects.create(name='工单管理', path='workorders', parent=production_mgmt)
        production_order = Menu.objects.create(name='生产订单管理', path='production-orders', parent=production_mgmt)
        
        # 将所有菜单赋予超级管理员组权限
        for menu in Menu.objects.all():
            menu.groups.add(admin_group)
        
        self.stdout.write(self.style.SUCCESS('系统菜单初始化完成！')) 