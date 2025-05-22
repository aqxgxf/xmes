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

        # 先创建所有菜单（不带parent）
        menu_objs = {}
        menu_data = [
            {"id": 1, "name": "基础数据", "path": "", "parent_id": None},
            {"id": 2, "name": "产品数据", "path": "", "parent_id": 1},
            {"id": 3, "name": "BOM数据", "path": "", "parent_id": 1},
            {"id": 4, "name": "工艺数据", "path": "", "parent_id": 1},
            {"id": 5, "name": "其他数据", "path": "", "parent_id": 1},
            {"id": 6, "name": "公司管理", "path": "companies", "parent_id": 5},
            {"id": 7, "name": "产品类别", "path": "product-categories", "parent_id": 2},
            {"id": 8, "name": "类别参数", "path": "category-params", "parent_id": 2},
            {"id": 9, "name": "产品管理", "path": "products", "parent_id": 2},
            {"id": 10, "name": "物料管理", "path": "materials", "parent_id": 3},
            {"id": 11, "name": "工序管理", "path": "processes", "parent_id": 4},
            {"id": 12, "name": "工艺流程", "path": "process-codes", "parent_id": 4},
            {"id": 14, "name": "工艺流程明细", "path": "process-details", "parent_id": 4},
            {"id": 15, "name": "BOM管理", "path": "boms", "parent_id": 3},
            {"id": 16, "name": "BOM明细", "path": "bom-details", "parent_id": 3},
            {"id": 17, "name": "单位管理", "path": "units", "parent_id": 5},
            {"id": 18, "name": "系统管理", "path": "", "parent_id": None},
            {"id": 19, "name": "用户管理", "path": "users", "parent_id": 18},
            {"id": 20, "name": "用户组管理", "path": "groups", "parent_id": 18},
            {"id": 21, "name": "菜单管理", "path": "menus", "parent_id": 18},
            {"id": 22, "name": "数据导入", "path": "data-import", "parent_id": 18},
            {"id": 23, "name": "销售管理", "path": "", "parent_id": None},
            {"id": 24, "name": "订单管理", "path": "orders", "parent_id": 23},
            {"id": 25, "name": "生产管理", "path": "", "parent_id": None},
            {"id": 26, "name": "工单管理", "path": "workorders", "parent_id": 25},
            {"id": 27, "name": "产品类工艺关联", "path": "category-process-codes", "parent_id": 4},
            {"id": 28, "name": "工单回冲", "path": "workorder-feedback", "parent_id": 25},
            {"id": 29, "name": "回冲明细查询", "path": "workorder-feedback-list", "parent_id": 25},
            {"id": 30, "name": "产品类BOM物料规则", "path": "category-material-rule", "parent_id": 3},
            {"id": 31, "name": "产品工艺关联", "path": "product-process-codes", "parent_id": 4},
        ]
        # 先创建所有菜单对象（不带parent）
        for m in menu_data:
            menu_objs[m["id"]] = Menu.objects.create(name=m["name"], path=m["path"])
        # 再设置parent
        for m in menu_data:
            if m["parent_id"]:
                menu_objs[m["id"]].parent = menu_objs[m["parent_id"]]
                menu_objs[m["id"]].save()
        # 赋权
        for menu in Menu.objects.all():
            menu.groups.add(admin_group)
        self.stdout.write(self.style.SUCCESS('系统菜单初始化完成！'))
