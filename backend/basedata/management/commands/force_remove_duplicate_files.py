from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
import re
import os
import time

class Command(BaseCommand):
    help = '强制清理所有带随机后缀的重复PDF文件，处理文件锁定问题'

    def add_arguments(self, parser):
        parser.add_argument(
            '--directory',
            dest='directory',
            default='drawings',
            help='要清理的目录（默认：drawings）',
        )
        parser.add_argument(
            '--delay',
            dest='delay',
            type=int,
            default=2,
            help='文件删除尝试之间的等待时间（秒，默认：2）',
        )
        parser.add_argument(
            '--max-retries',
            dest='max_retries',
            type=int,
            default=5,
            help='删除文件时的最大重试次数（默认：5）',
        )
        parser.add_argument(
            '--kill-explorer',
            action='store_true',
            dest='kill_explorer',
            help='尝试重启Windows资源管理器以释放文件锁（需小心使用）',
        )

    def handle(self, *args, **options):
        directory = options['directory']
        delay = options['delay']
        max_retries = options['max_retries']
        kill_explorer = options['kill_explorer']

        self.stdout.write(self.style.SUCCESS(f'开始强制清理{directory}目录中的重复PDF文件...'))

        # 如果选择了kill_explorer选项，尝试重启资源管理器
        if kill_explorer:
            self.stdout.write('尝试重启Windows资源管理器以释放文件锁...')
            try:
                import subprocess
                subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(1)
                subprocess.Popen('explorer.exe')
                self.stdout.write('Windows资源管理器已重启')
                time.sleep(2)  # 给资源管理器时间重启
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'重启Windows资源管理器失败: {e}'))

        # 分析目录中的文件
        try:
            all_files = default_storage.listdir(directory)[1]
            self.stdout.write(f'在{directory}目录中找到{len(all_files)}个文件')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'无法列出{directory}目录中的文件: {e}'))
            return

        # 按基础名称分组文件
        file_groups = {}
        suffix_pattern = re.compile(r'^(.+?)_[a-zA-Z0-9]{5,}\.pdf$')
        standard_pattern = re.compile(r'^(.+?)-(图纸|工艺)\.pdf$')

        for file_name in all_files:
            if not file_name.lower().endswith('.pdf'):
                continue

            # 检查是否是带随机后缀的文件
            suffix_match = suffix_pattern.match(file_name)
            standard_match = standard_pattern.match(file_name)

            if suffix_match:
                # 带随机后缀的文件
                base_name = suffix_match.group(1)
                if base_name not in file_groups:
                    file_groups[base_name] = {'standard': None, 'suffixed': []}
                file_groups[base_name]['suffixed'].append(file_name)
            elif standard_match or ('-' in file_name and not '_' in file_name):
                # 标准命名文件 (不含随机后缀)
                base_name = file_name.rsplit('.', 1)[0]
                if base_name not in file_groups:
                    file_groups[base_name] = {'standard': file_name, 'suffixed': []}
                else:
                    file_groups[base_name]['standard'] = file_name
            elif '-' in file_name and '_' in file_name:
                # 特殊情况: 既有连字符又有下划线的文件
                # 尝试提取基础名并按产品代码-公司名称分组
                parts = file_name.split('_')[0].split('-')
                if len(parts) >= 2:  # 至少有产品代码和公司名称
                    code_company = '-'.join(parts[:2])  # 产品代码-公司名称
                    if file_name.find('图纸') > -1:
                        base_name = f"{code_company}-图纸"
                    elif file_name.find('工艺') > -1:
                        base_name = f"{code_company}-工艺"
                    else:
                        base_name = code_company

                    if base_name not in file_groups:
                        file_groups[base_name] = {'standard': None, 'suffixed': []}
                    file_groups[base_name]['suffixed'].append(file_name)

        # 处理每组文件
        deleted_count = 0
        groups_processed = 0
        groups_count = len(file_groups)

        for base_name, files in file_groups.items():
            groups_processed += 1
            self.stdout.write(f'处理文件组 [{groups_processed}/{groups_count}]: {base_name}')

            # 如果没有标准命名文件，但有带后缀的文件，取第一个作为标准
            if not files['standard'] and files['suffixed']:
                # 创建标准文件名
                standard_name = f"{base_name}.pdf"

                # 从第一个带后缀文件复制内容到标准文件
                try:
                    first_suffixed = files['suffixed'][0]
                    suffixed_path = f"{directory}/{first_suffixed}"
                    standard_path = f"{directory}/{standard_name}"

                    if not default_storage.exists(standard_path):
                        with default_storage.open(suffixed_path, 'rb') as src_file:
                            default_storage.save(standard_path, src_file)
                            self.stdout.write(f"已创建标准文件: {standard_path}")
                            files['standard'] = standard_name
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"创建标准文件失败: {e}"))

            # 删除带随机后缀的文件
            if files['standard'] and files['suffixed']:
                self.stdout.write(f"    标准文件: {files['standard']}")
                self.stdout.write(f"    需删除的文件: {len(files['suffixed'])}个")

                for suffixed_file in files['suffixed']:
                    self.stdout.write(f"    尝试删除: {suffixed_file}")
                    file_path = f"{directory}/{suffixed_file}"

                    # 尝试删除文件，带重试
                    for retry in range(max_retries):
                        try:
                            if default_storage.exists(file_path):
                                default_storage.delete(file_path)
                                self.stdout.write(f"    √ 成功删除: {file_path}")
                                deleted_count += 1
                                break
                            else:
                                self.stdout.write(f"    - 文件不存在: {file_path}")
                                break
                        except PermissionError as e:
                            if retry < max_retries - 1:
                                self.stdout.write(f"    ! 文件被锁定，等待{delay}秒后重试 ({retry+1}/{max_retries}): {e}")
                                time.sleep(delay)
                            else:
                                self.stdout.write(self.style.ERROR(f"    × 无法删除文件(已达最大重试次数): {e}"))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"    × 删除失败: {e}"))
                            break

            # 如果处理完成，暂停一下以减轻系统负担
            time.sleep(0.2)

        self.stdout.write(self.style.SUCCESS(f'\n清理完成! 共删除了{deleted_count}个带随机后缀的重复文件'))
