from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.db import transaction
import re
import os
from basedata.models import ProductCategory, ProcessCode, Product
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = '彻底清理所有带随机后缀的PDF文件，并确保数据库引用使用正确的文件路径'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-all-duplicates',
            action='store_true',
            dest='delete_all_duplicates',
            help='删除所有重复文件，只保留标准命名的文件',
        )
        parser.add_argument(
            '--fix-database',
            action='store_true',
            dest='fix_database',
            help='修复数据库记录以使用标准命名文件',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始清理带随机后缀的PDF文件...'))
        self.stdout.write('操作模式:')
        if options['delete_all_duplicates']:
            self.stdout.write(' - 删除所有重复文件')
        if options['fix_database']:
            self.stdout.write(' - 修复数据库记录')
        if not options['delete_all_duplicates'] and not options['fix_database']:
            self.stdout.write(' - 仅分析文件情况(不进行实际清理)')

        # 检查drawings目录
        self.stdout.write('\n--- 处理drawings目录 ---')
        self.clean_directory('drawings', options['delete_all_duplicates'])

        # 检查process_pdfs目录
        self.stdout.write('\n--- 处理process_pdfs目录 ---')
        self.clean_directory('process_pdfs', options['delete_all_duplicates'])

        # 修复数据库记录
        if options['fix_database']:
            self.stdout.write('\n--- 修复数据库记录 ---')
            self.fix_database_records()

        self.stdout.write(self.style.SUCCESS('\n清理完成！'))

    def clean_directory(self, directory, delete_duplicates=False):
        """清理指定目录中的带随机后缀文件"""
        try:
            # 获取目录下的所有文件
            try:
                all_files = default_storage.listdir(directory)[1]
                self.stdout.write(f'{directory}目录中共有 {len(all_files)} 个文件')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'无法列出{directory}目录下的文件: {str(e)}'))
                return

            # 检测文件命名模式
            suffix_pattern = re.compile(r'^(.+?)_[a-zA-Z0-9]{5,}\.pdf$')
            standard_files = {}  # 标准命名的文件 {基础名称: 文件名}
            suffixed_files = {}  # 带随机后缀的文件 {基础名称: [文件名...]}

            # 分类所有文件
            for file_name in all_files:
                if not file_name.lower().endswith('.pdf'):
                    continue

                match = suffix_pattern.match(file_name)
                if match:
                    # 带随机后缀的文件
                    base_name = match.group(1)
                    if base_name not in suffixed_files:
                        suffixed_files[base_name] = []
                    suffixed_files[base_name].append(file_name)
                elif '-' in file_name and ('.pdf' in file_name or '.PDF' in file_name):
                    # 标准命名的文件
                    # 提取基础名称 (不包括扩展名)
                    base_name = file_name.rsplit('.', 1)[0]
                    standard_files[base_name] = file_name

            self.stdout.write(f'发现 {len(standard_files)} 个标准命名文件和 {sum(len(files) for files in suffixed_files.values())} 个带随机后缀的文件')

            # 处理带随机后缀的文件
            deleted_count = 0
            warning_count = 0
            kept_suffixed_files = []

            for base_name, suffix_files in suffixed_files.items():
                # 检查是否存在标准命名的文件
                if base_name in standard_files:
                    self.stdout.write(f'基础名称 "{base_name}" 已有标准命名文件: {standard_files[base_name]}')

                    # 删除所有带随机后缀的文件
                    if delete_duplicates:
                        for suffix_file in suffix_files:
                            try:
                                file_path = f'{directory}/{suffix_file}'
                                default_storage.delete(file_path)
                                self.stdout.write(f'已删除带随机后缀的文件: {file_path}')
                                deleted_count += 1
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'删除文件失败: {file_path}, 错误: {e}'))
                                warning_count += 1
                    else:
                        self.stdout.write(f' - 模拟模式: 将删除 {len(suffix_files)} 个带随机后缀的文件')
                else:
                    # 没有标准命名的文件，需要保留一个作为标准命名
                    self.stdout.write(f'基础名称 "{base_name}" 没有标准命名文件')

                    if delete_duplicates:
                        # 选择最新的文件作为标准命名文件
                        suffix_files.sort(key=lambda x: default_storage.get_modified_time(f'{directory}/{x}'), reverse=True)
                        newest_file = suffix_files[0]
                        self.stdout.write(f' - 选择 {newest_file} 作为标准命名文件')

                        # 读取文件内容
                        try:
                            newest_file_path = f'{directory}/{newest_file}'
                            with default_storage.open(newest_file_path, 'rb') as f:
                                file_content = f.read()

                            # 创建标准命名文件
                            standard_file_name = f'{base_name}.pdf'
                            standard_file_path = f'{directory}/{standard_file_name}'

                            default_storage.save(standard_file_path, ContentFile(file_content))
                            self.stdout.write(f' - 已创建标准命名文件: {standard_file_path}')

                            # 删除所有带随机后缀的文件
                            for suffix_file in suffix_files:
                                try:
                                    file_path = f'{directory}/{suffix_file}'
                                    default_storage.delete(file_path)
                                    self.stdout.write(f' - 已删除带随机后缀的文件: {file_path}')
                                    deleted_count += 1
                                except Exception as e:
                                    self.stdout.write(self.style.ERROR(f' - 删除文件失败: {file_path}, 错误: {e}'))
                                    warning_count += 1
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f' - 处理文件失败: {e}'))
                            kept_suffixed_files.extend(suffix_files)
                            warning_count += 1
                    else:
                        self.stdout.write(f' - 模拟模式: 将创建标准命名文件并删除 {len(suffix_files)} 个带随机后缀的文件')
                        kept_suffixed_files.extend(suffix_files)

            self.stdout.write(self.style.SUCCESS(f'\n{directory}目录清理结果:'))
            self.stdout.write(f' - 删除了 {deleted_count} 个带随机后缀的文件')
            self.stdout.write(f' - 有 {warning_count} 个警告')
            self.stdout.write(f' - 保留了 {len(kept_suffixed_files)} 个带随机后缀的文件')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'处理{directory}目录时出错: {e}'))

    def fix_database_records(self):
        """修复数据库中的文件路径引用"""
        try:
            with transaction.atomic():
                # 修复ProductCategory
                categories = ProductCategory.objects.all()
                fixed_drawing_count = 0
                fixed_process_count = 0

                self.stdout.write(f'扫描 {categories.count()} 个产品类...')

                for category in categories:
                    # 1. 修复图纸PDF
                    if category.drawing_pdf:
                        drawing_path = category.drawing_pdf.name
                        if '_' in os.path.basename(drawing_path) and drawing_path.endswith('.pdf'):
                            # 包含随机后缀，需要修复
                            code = category.code.replace('/', '_')
                            company_name = category.company.name.replace('/', '_')
                            standard_path = f"drawings/{code}-{company_name}-图纸.pdf"

                            # 检查标准文件是否存在
                            if default_storage.exists(standard_path):
                                category.drawing_pdf.name = standard_path
                                category.save(update_fields=['drawing_pdf'])
                                fixed_drawing_count += 1
                                self.stdout.write(f'已修复 {category.code} 的图纸PDF路径')

                    # 2. 修复工艺PDF
                    if category.process_pdf:
                        process_path = category.process_pdf.name
                        if '_' in os.path.basename(process_path) and process_path.endswith('.pdf'):
                            # 包含随机后缀，需要修复
                            code = category.code.replace('/', '_')
                            company_name = category.company.name.replace('/', '_')
                            standard_path = f"drawings/{code}-{company_name}-工艺.pdf"

                            # 检查标准文件是否存在
                            if default_storage.exists(standard_path):
                                category.process_pdf.name = standard_path
                                category.save(update_fields=['process_pdf'])
                                fixed_process_count += 1
                                self.stdout.write(f'已修复 {category.code} 的工艺PDF路径')

                self.stdout.write(self.style.SUCCESS(f'已修复 {fixed_drawing_count} 个产品类的图纸PDF路径和 {fixed_process_count} 个产品类的工艺PDF路径'))

                # 修复ProcessCode
                process_codes = ProcessCode.objects.all()
                fixed_pdf_count = 0

                self.stdout.write(f'扫描 {process_codes.count()} 个工艺流程代码...')

                for process_code in process_codes:
                    if process_code.process_pdf:
                        pdf_path = process_code.process_pdf.name
                        if '_' in os.path.basename(pdf_path) and pdf_path.endswith('.pdf'):
                            # 包含随机后缀，需要修复
                            code = process_code.code.replace('/', '_')
                            version = process_code.version.replace('/', '_')
                            standard_path = f"process_pdfs/{code}-{version}.pdf"

                            # 检查标准文件是否存在
                            if default_storage.exists(standard_path):
                                process_code.process_pdf.name = standard_path
                                process_code.save(update_fields=['process_pdf'])
                                fixed_pdf_count += 1
                                self.stdout.write(f'已修复工艺流程 {process_code.code} (v{process_code.version}) 的PDF路径')

                self.stdout.write(self.style.SUCCESS(f'已修复 {fixed_pdf_count} 个工艺流程代码的PDF路径'))

                # 修复Product
                products = Product.objects.all()
                fixed_product_count = 0

                self.stdout.write(f'扫描 {products.count()} 个产品...')

                for product in products:
                    if product.drawing_pdf:
                        pdf_path = product.drawing_pdf.name
                        if '_' in os.path.basename(pdf_path) and pdf_path.endswith('.pdf'):
                            # 包含随机后缀，需要修复
                            code = product.code.replace('/', '_')
                            standard_path = f"drawings/{code}.pdf"

                            # 检查标准文件是否存在
                            if default_storage.exists(standard_path):
                                product.drawing_pdf.name = standard_path
                                product.save(update_fields=['drawing_pdf'])
                                fixed_product_count += 1
                                self.stdout.write(f'已修复产品 {product.code} 的PDF路径')

                self.stdout.write(self.style.SUCCESS(f'已修复 {fixed_product_count} 个产品的PDF路径'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'修复数据库记录时出错: {e}'))
