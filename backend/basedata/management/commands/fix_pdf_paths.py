from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import re
import os
from basedata.models import ProductCategory, ProcessCode

class Command(BaseCommand):
    help = '修复数据库中的PDF文件路径，将带随机后缀的文件路径修正为标准格式的路径'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始修复PDF文件路径...'))

        # 1. 修复产品类图纸和工艺PDF路径
        self.fix_product_categories()

        # 2. 修复工艺流程代码PDF路径
        self.fix_process_codes()

        self.stdout.write(self.style.SUCCESS('修复完成！'))

    def fix_product_categories(self):
        """修复ProductCategory模型的PDF文件路径"""
        categories = ProductCategory.objects.all()
        categories_count = categories.count()
        self.stdout.write(f'共找到 {categories_count} 个产品类')

        fixed_drawing_count = 0
        fixed_process_count = 0

        # 正则表达式，用于匹配随机后缀格式的文件名
        suffix_pattern = re.compile(r'^(.*?)_[a-zA-Z0-9]{5,}\.(pdf|PDF)$')

        for category in categories:
            try:
                # 1. 修复图纸PDF路径
                if category.drawing_pdf:
                    drawing_path = category.drawing_pdf.name
                    file_name = os.path.basename(drawing_path)

                    # 检查是否包含随机后缀
                    match = suffix_pattern.match(file_name)
                    if match:
                        # 标准文件名应该是：产品类代码-公司代码-图纸.pdf
                        code = category.code.replace('/', '_')
                        company_name = category.company.name.replace('/', '_')
                        standard_file_name = f"{code}-{company_name}-图纸.pdf"
                        standard_path = f"drawings/{standard_file_name}"

                        try:
                            # 检查文件是否实际存在
                            if default_storage.exists(drawing_path):
                                try:
                                    # 读取原始文件内容
                                    with default_storage.open(drawing_path, 'rb') as f:
                                        file_content = f.read()

                                    # 删除原始文件
                                    default_storage.delete(drawing_path)
                                    self.stdout.write(f'已删除带随机后缀的图纸文件: {drawing_path}')

                                    # 保存为标准名称文件
                                    default_storage.save(standard_path, ContentFile(file_content))
                                    self.stdout.write(f'已保存为标准名称的图纸文件: {standard_path}')
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING(f'读取/写入文件时出错: {e}，尝试直接更新路径'))

                            # 无论文件操作是否成功，都更新数据库记录
                            category.drawing_pdf.name = standard_path
                            category.save(update_fields=['drawing_pdf'])
                            fixed_drawing_count += 1
                            self.stdout.write(f'已修复 {category.code} 的图纸PDF路径')
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'修复 {category.code} 的图纸PDF路径失败: {e}'))

                # 2. 修复工艺PDF路径
                if category.process_pdf:
                    process_path = category.process_pdf.name
                    file_name = os.path.basename(process_path)

                    # 检查是否包含随机后缀
                    match = suffix_pattern.match(file_name)
                    if match:
                        # 标准文件名应该是：产品类代码-公司代码-工艺.pdf
                        code = category.code.replace('/', '_')
                        company_name = category.company.name.replace('/', '_')
                        standard_file_name = f"{code}-{company_name}-工艺.pdf"
                        standard_path = f"drawings/{standard_file_name}"

                        try:
                            # 检查文件是否实际存在
                            if default_storage.exists(process_path):
                                try:
                                    # 读取原始文件内容
                                    with default_storage.open(process_path, 'rb') as f:
                                        file_content = f.read()

                                    # 删除原始文件
                                    default_storage.delete(process_path)
                                    self.stdout.write(f'已删除带随机后缀的工艺文件: {process_path}')

                                    # 保存为标准名称文件
                                    default_storage.save(standard_path, ContentFile(file_content))
                                    self.stdout.write(f'已保存为标准名称的工艺文件: {standard_path}')
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING(f'读取/写入文件时出错: {e}，尝试直接更新路径'))

                            # 无论文件操作是否成功，都更新数据库记录
                            category.process_pdf.name = standard_path
                            category.save(update_fields=['process_pdf'])
                            fixed_process_count += 1
                            self.stdout.write(f'已修复 {category.code} 的工艺PDF路径')
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'修复 {category.code} 的工艺PDF路径失败: {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'处理产品类 {category.id} 时出错: {e}'))

        self.stdout.write(self.style.SUCCESS(f'已修复 {fixed_drawing_count} 个产品类的图纸PDF路径和 {fixed_process_count} 个产品类的工艺PDF路径'))

    def fix_process_codes(self):
        """修复ProcessCode模型的PDF文件路径"""
        process_codes = ProcessCode.objects.all()
        process_codes_count = process_codes.count()
        self.stdout.write(f'共找到 {process_codes_count} 个工艺流程代码')

        fixed_count = 0

        # 正则表达式，用于匹配随机后缀格式的文件名
        suffix_pattern = re.compile(r'^(.*?)_[a-zA-Z0-9]{5,}\.(pdf|PDF)$')

        for process_code in process_codes:
            try:
                if process_code.process_pdf:
                    pdf_path = process_code.process_pdf.name
                    file_name = os.path.basename(pdf_path)

                    # 检查是否包含随机后缀
                    match = suffix_pattern.match(file_name)
                    if match:
                        # 标准文件名应该是：工艺流程代码-版本.pdf
                        code = process_code.code.replace('/', '_')
                        version = process_code.version.replace('/', '_')
                        standard_file_name = f"{code}-{version}.pdf"
                        standard_path = f"process_pdfs/{standard_file_name}"

                        try:
                            # 检查文件是否实际存在
                            if default_storage.exists(pdf_path):
                                try:
                                    # 读取原始文件内容
                                    with default_storage.open(pdf_path, 'rb') as f:
                                        file_content = f.read()

                                    # 删除原始文件
                                    default_storage.delete(pdf_path)
                                    self.stdout.write(f'已删除带随机后缀的工艺流程PDF文件: {pdf_path}')

                                    # 保存为标准名称文件
                                    default_storage.save(standard_path, ContentFile(file_content))
                                    self.stdout.write(f'已保存为标准名称的工艺流程PDF文件: {standard_path}')
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING(f'读取/写入文件时出错: {e}，尝试直接更新路径'))

                            # 无论文件操作是否成功，都更新数据库记录
                            process_code.process_pdf.name = standard_path
                            process_code.save(update_fields=['process_pdf'])
                            fixed_count += 1
                            self.stdout.write(f'已修复工艺流程 {process_code.code} (v{process_code.version}) 的PDF路径')
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'修复工艺流程 {process_code.code} (v{process_code.version}) 的PDF路径失败: {e}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'处理工艺流程代码 {process_code.id} 时出错: {e}'))

        self.stdout.write(self.style.SUCCESS(f'已修复 {fixed_count} 个工艺流程代码的PDF路径'))
