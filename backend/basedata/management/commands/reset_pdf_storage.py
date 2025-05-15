from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.db import transaction
from django.conf import settings
import re
import os
import time
import shutil
from basedata.models import ProductCategory, Product, ProcessCode

class Command(BaseCommand):
    help = '彻底重置PDF存储，删除所有随机后缀文件并重新创建标准命名文件'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='强制执行，不提示确认',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=5,
            help='文件处理的超时时间(秒)',
        )

    def handle(self, *args, **options):
        force = options['force']
        timeout = options['timeout']

        if not force:
            self.stdout.write(self.style.WARNING("警告：此命令将删除所有PDF文件并重新生成。"))
            confirm = input("确定要继续吗? [y/N]: ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.ERROR("操作已取消"))
                return

        self.stdout.write(self.style.SUCCESS("开始重置PDF存储..."))

        # 1. 备份现有数据库记录
        self.backup_database_records()

        # 2. 彻底清空drawings目录
        self.reset_directory('drawings', timeout)

        # 3. 彻底清空process_pdfs目录
        self.reset_directory('process_pdfs', timeout)

        # 4. 重新生成所有文件
        self.regenerate_files()

        self.stdout.write(self.style.SUCCESS("PDF存储重置完成!"))

    def backup_database_records(self):
        """备份关键数据库记录"""
        self.stdout.write("备份数据库记录...")

        # 产品类PDF记录
        categories = ProductCategory.objects.filter(drawing_pdf__isnull=False) | ProductCategory.objects.filter(process_pdf__isnull=False)
        self.stdout.write(f"找到 {categories.count()} 个有PDF的产品类")

        # 产品PDF记录
        products = Product.objects.filter(drawing_pdf__isnull=False)
        self.stdout.write(f"找到 {products.count()} 个有PDF的产品")

        # 工艺流程代码PDF记录
        processes = ProcessCode.objects.filter(process_pdf__isnull=False)
        self.stdout.write(f"找到 {processes.count()} 个有PDF的工艺流程代码")

        # 可以将这些记录写入到一个临时文件中以备后用
        with open('pdf_backup.txt', 'w', encoding='utf-8') as f:
            f.write("=== 产品类PDF ===\n")
            for c in categories:
                if c.drawing_pdf:
                    f.write(f"{c.code}|{c.company.name}|图纸|{c.drawing_pdf.name}\n")
                if c.process_pdf:
                    f.write(f"{c.code}|{c.company.name}|工艺|{c.process_pdf.name}\n")

            f.write("\n=== 产品PDF ===\n")
            for p in products:
                if p.drawing_pdf:
                    f.write(f"{p.code}|{p.drawing_pdf.name}\n")

            f.write("\n=== 工艺流程代码PDF ===\n")
            for pc in processes:
                if pc.process_pdf:
                    f.write(f"{pc.code}|{pc.version}|{pc.process_pdf.name}\n")

        self.stdout.write(self.style.SUCCESS("数据库记录备份完成"))

    def reset_directory(self, directory_name, timeout):
        """彻底重置指定目录"""
        self.stdout.write(f"重置 {directory_name} 目录...")

        try:
            # 确保目录存在
            if not default_storage.exists(directory_name):
                default_storage.makedirs(directory_name)
                self.stdout.write(f"已创建 {directory_name} 目录")
                return

            # 列出目录中的所有文件
            files = default_storage.listdir(directory_name)[1]
            self.stdout.write(f"在 {directory_name} 目录中找到 {len(files)} 个文件")

            # 通过创建一个临时目录来绕过文件锁定问题
            temp_dir = f"{directory_name}_temp"
            if default_storage.exists(temp_dir):
                try:
                    files_to_delete = default_storage.listdir(temp_dir)[1]
                    for f in files_to_delete:
                        try:
                            default_storage.delete(f"{temp_dir}/{f}")
                        except:
                            pass
                    default_storage.delete(temp_dir)
                except:
                    pass

            default_storage.makedirs(temp_dir)
            self.stdout.write(f"已创建临时目录 {temp_dir}")

            # 尝试重命名原目录(可能会失败，但值得一试)
            old_dir = f"{directory_name}_old"
            if default_storage.exists(old_dir):
                try:
                    files_to_delete = default_storage.listdir(old_dir)[1]
                    for f in files_to_delete:
                        try:
                            default_storage.delete(f"{old_dir}/{f}")
                        except:
                            pass
                    default_storage.delete(old_dir)
                except:
                    pass

            # 删除文件
            for f in files:
                try:
                    file_path = f"{directory_name}/{f}"
                    default_storage.delete(file_path)
                    self.stdout.write(f"已删除文件: {file_path}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"无法删除文件 {f}: {e}"))

                    # 尝试通过系统命令强制删除
                    try:
                        media_root = settings.MEDIA_ROOT
                        full_path = os.path.join(media_root, file_path)
                        if os.path.exists(full_path):
                            os.chmod(full_path, 0o777)  # 更改权限
                            os.remove(full_path)
                            self.stdout.write(f"已通过系统命令删除文件: {full_path}")
                    except Exception as e2:
                        self.stdout.write(self.style.ERROR(f"强制删除也失败: {e2}"))

                # 暂停一下，避免系统过载
                time.sleep(0.1)

            self.stdout.write(self.style.SUCCESS(f"{directory_name} 目录重置完成"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"重置 {directory_name} 目录时出错: {e}"))

            # 如果是关键目录，尝试更强力的方法重置
            try:
                media_root = settings.MEDIA_ROOT
                dir_path = os.path.join(media_root, directory_name)

                if os.path.exists(dir_path):
                    # 尝试递归删除目录及其内容
                    shutil.rmtree(dir_path, ignore_errors=True)
                    time.sleep(1)  # 等待文件系统更新

                    # 重新创建目录
                    os.makedirs(dir_path, exist_ok=True)
                    self.stdout.write(self.style.SUCCESS(f"已强制重置 {directory_name} 目录"))
            except Exception as e2:
                self.stdout.write(self.style.ERROR(f"强制重置也失败: {e2}"))

    def regenerate_files(self):
        """重新生成所有PDF文件"""
        self.stdout.write("开始重新生成PDF文件...")

        # 使用事务确保数据库操作的一致性
        with transaction.atomic():
            # 处理产品类PDF
            self.regenerate_category_pdfs()

            # 处理产品PDF
            self.regenerate_product_pdfs()

            # 处理工艺流程代码PDF
            self.regenerate_process_pdfs()

        self.stdout.write(self.style.SUCCESS("所有PDF文件重新生成完成"))

    def regenerate_category_pdfs(self):
        """重新生成产品类图纸和工艺PDF"""
        categories = ProductCategory.objects.filter(drawing_pdf__isnull=False) | ProductCategory.objects.filter(process_pdf__isnull=False)
        count = categories.count()
        self.stdout.write(f"处理 {count} 个产品类PDF...")

        for i, category in enumerate(categories, 1):
            self.stdout.write(f"处理产品类 [{i}/{count}]: {category.code}")

            # 保存会触发文件处理逻辑
            try:
                if category.drawing_pdf or category.process_pdf:
                    # 直接保存以触发save方法中的文件处理逻辑
                    category.save()
                    self.stdout.write(f"已重新生成 {category.code} 的PDF文件")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"处理 {category.code} 的PDF文件时出错: {e}"))

    def regenerate_product_pdfs(self):
        """重新生成产品图纸PDF"""
        products = Product.objects.filter(drawing_pdf__isnull=False)
        count = products.count()
        self.stdout.write(f"处理 {count} 个产品PDF...")

        for i, product in enumerate(products, 1):
            self.stdout.write(f"处理产品 [{i}/{count}]: {product.code}")

            try:
                if product.drawing_pdf:
                    # 直接保存以触发save方法中的文件处理逻辑
                    product.save()
                    self.stdout.write(f"已重新生成 {product.code} 的PDF文件")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"处理 {product.code} 的PDF文件时出错: {e}"))

    def regenerate_process_pdfs(self):
        """重新生成工艺流程代码PDF"""
        processes = ProcessCode.objects.filter(process_pdf__isnull=False)
        count = processes.count()
        self.stdout.write(f"处理 {count} 个工艺流程代码PDF...")

        for i, process in enumerate(processes, 1):
            self.stdout.write(f"处理工艺流程代码 [{i}/{count}]: {process.code} (v{process.version})")

            try:
                if process.process_pdf:
                    # 直接保存以触发save方法中的文件处理逻辑
                    process.save()
                    self.stdout.write(f"已重新生成 {process.code} (v{process.version}) 的PDF文件")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"处理 {process.code} (v{process.version}) 的PDF文件时出错: {e}"))
