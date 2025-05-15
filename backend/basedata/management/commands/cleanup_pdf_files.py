from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
import re
import os
from basedata.models import ProductCategory

class Command(BaseCommand):
    help = '清理drawings目录中冗余的PDF文件，特别是带有随机后缀的文件'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('开始清理冗余PDF文件...'))

        # 获取所有有效的文件路径
        valid_files = set()
        categories = list(ProductCategory.objects.all())
        self.stdout.write(f'发现 {len(categories)} 个产品类')

        # 收集所有产品类正在使用的文件路径
        for category in categories:
            if category.drawing_pdf:
                valid_files.add(category.drawing_pdf.name)
                self.stdout.write(f'有效图纸文件: {category.drawing_pdf.name}')
            if category.process_pdf:
                valid_files.add(category.process_pdf.name)
                self.stdout.write(f'有效工艺文件: {category.process_pdf.name}')

        self.stdout.write(f'共找到 {len(valid_files)} 个有效文件')

        # 列出drawings目录下的所有文件
        try:
            all_files = default_storage.listdir('drawings')[1]
            self.stdout.write(f'drawings目录中共有 {len(all_files)} 个文件')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'无法列出drawings目录下的文件: {str(e)}'))
            return

        # 找出所有正在使用的文件并保留最新备份文件
        deleted_files = []
        retained_files = []

        # 使用正则表达式识别文件模式
        random_suffix_pattern = re.compile(r'^(.+)_[a-zA-Z0-9]{5,}\.pdf$')  # 匹配Django自动添加的随机后缀
        backup_pattern = re.compile(r'^(.+)-(图纸|工艺)-(\d+)\.pdf$')  # 匹配带时间戳的备份文件
        standard_pattern = re.compile(r'^(.+)-(图纸|工艺)\.pdf$')  # 匹配标准格式文件

        # 收集所有标准格式的基础文件名和类型
        base_filenames = {}  # 存储 {基础名称: {类型: 文件名}}
        for filepath in valid_files:
            if filepath and filepath.startswith('drawings/'):
                filename = os.path.basename(filepath)
                match = standard_pattern.match(filename)
                if match:
                    base_name = match.group(1)  # 产品类代码-公司代码
                    file_type = match.group(2)  # 图纸 或 工艺

                    if base_name not in base_filenames:
                        base_filenames[base_name] = {}

                    base_filenames[base_name][file_type] = filename

        self.stdout.write(f'找到 {len(base_filenames)} 个不同的产品类基础文件名')

        # 收集所有备份文件，按基础名称和类型分组
        backup_files = {}  # 存储 {基础名称: {类型: [备份文件列表]}}
        for file in all_files:
            backup_match = backup_pattern.match(file)
            if backup_match:
                base_name = backup_match.group(1)  # 产品类代码-公司代码
                file_type = backup_match.group(2)  # 图纸 或 工艺

                if base_name not in backup_files:
                    backup_files[base_name] = {}

                if file_type not in backup_files[base_name]:
                    backup_files[base_name][file_type] = []

                backup_files[base_name][file_type].append(file)

        # 处理所有文件
        for file in all_files:
            full_path = f'drawings/{file}'

            # 1. 保留当前正在使用的文件
            if full_path in valid_files:
                retained_files.append(file)
                self.stdout.write(f'保留有效文件: {file}')
                continue

            # 2. 检查是否是带有随机后缀的文件，这些文件通常是Django自动创建的
            random_match = random_suffix_pattern.match(file)
            if random_match:
                try:
                    default_storage.delete(full_path)
                    deleted_files.append(file)
                    self.stdout.write(self.style.WARNING(f'已删除带随机后缀的文件: {file}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'删除文件失败: {file}, 错误: {e}'))
                continue

            # 3. 检查是否是备份文件
            backup_match = backup_pattern.match(file)
            if backup_match:
                base_name = backup_match.group(1)  # 产品类代码-公司代码
                file_type = backup_match.group(2)  # 图纸 或 工艺

                # 如果基础名称在有效文件中，且已经有多个备份，则只保留最新的一个
                if base_name in backup_files and file_type in backup_files[base_name]:
                    same_type_backups = backup_files[base_name][file_type]

                    if len(same_type_backups) > 1:
                        # 排序并只保留最新的一个
                        same_type_backups.sort(reverse=True)
                        if file != same_type_backups[0]:  # 不是最新的备份
                            try:
                                default_storage.delete(full_path)
                                deleted_files.append(file)
                                self.stdout.write(self.style.WARNING(f'已删除旧备份文件: {file}'))
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'删除文件失败: {file}, 错误: {e}'))
                        else:
                            retained_files.append(file)
                            self.stdout.write(f'保留最新备份文件: {file}')
                    else:
                        # 只有一个备份，保留它
                        retained_files.append(file)
                        self.stdout.write(f'保留唯一备份文件: {file}')
                else:
                    # 如果基础名称不是有效文件中的一个，可能是孤立的备份文件
                    # 检查是否有对应的标准格式文件存在
                    standard_filename = f"{base_name}-{file_type}.pdf"
                    if standard_filename in all_files:
                        # 有对应的标准文件，保留此备份
                        retained_files.append(file)
                        self.stdout.write(f'保留有对应标准文件的备份: {file}')
                    else:
                        # 无对应标准文件，删除此孤立备份
                        try:
                            default_storage.delete(full_path)
                            deleted_files.append(file)
                            self.stdout.write(self.style.WARNING(f'已删除孤立备份文件: {file}'))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'删除文件失败: {file}, 错误: {e}'))
                continue

            # 4. 检查无法识别的文件，可能需要手动评估
            self.stdout.write(self.style.WARNING(f'无法识别的文件格式: {file}，保留此文件'))
            retained_files.append(file)

        # 总结处理结果
        self.stdout.write(self.style.SUCCESS(f'''
清理完成！
- 删除文件数: {len(deleted_files)}
- 保留文件数: {len(retained_files)}
- 删除的文件: {", ".join(deleted_files[:10]) + ("..." if len(deleted_files) > 10 else "")}
        '''))
