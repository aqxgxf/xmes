from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
import re
import os
import time
import logging

# 配置日志
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '定期清理带随机后缀的PDF文件，可以作为计划任务运行'

    def add_arguments(self, parser):
        parser.add_argument(
            '--directory',
            dest='directory',
            default='drawings',
            help='要清理的目录（默认：drawings）',
        )
        parser.add_argument(
            '--max-retries',
            dest='max_retries',
            type=int,
            default=3,
            help='删除文件时的最大重试次数（默认：3）',
        )
        parser.add_argument(
            '--log-only',
            action='store_true',
            dest='log_only',
            help='只记录要删除的文件，不实际删除',
        )

    def handle(self, *args, **options):
        directory = options['directory']
        max_retries = options['max_retries']
        log_only = options['log_only']

        self.stdout.write(f'开始定期清理{directory}目录中的重复PDF文件...')
        logger.info(f'开始定期清理{directory}目录中的重复PDF文件...')

        try:
            all_files = default_storage.listdir(directory)[1]
            self.stdout.write(f'在{directory}目录中找到{len(all_files)}个文件')
            logger.info(f'在{directory}目录中找到{len(all_files)}个文件')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'无法列出{directory}目录中的文件: {e}'))
            logger.error(f'无法列出{directory}目录中的文件: {e}')
            return

        # 按基础名称分组文件
        suffix_pattern = re.compile(r'^(.+?)_[a-zA-Z0-9]{5,}\.pdf$')
        suffixed_files = []

        # 查找带随机后缀的文件
        for file_name in all_files:
            if not file_name.lower().endswith('.pdf'):
                continue

            suffix_match = suffix_pattern.match(file_name)
            if suffix_match:
                suffixed_files.append(file_name)

        if not suffixed_files:
            self.stdout.write('没有发现带随机后缀的PDF文件，无需清理')
            logger.info('没有发现带随机后缀的PDF文件，无需清理')
            return

        # 删除带随机后缀的文件
        deleted_count = 0
        self.stdout.write(f'发现{len(suffixed_files)}个带随机后缀的PDF文件')
        logger.info(f'发现{len(suffixed_files)}个带随机后缀的PDF文件')

        for file_name in suffixed_files:
            file_path = f"{directory}/{file_name}"

            if log_only:
                self.stdout.write(f'将删除文件(仅记录): {file_path}')
                logger.info(f'将删除文件(仅记录): {file_path}')
                continue

            # 尝试删除文件，带重试
            for retry in range(max_retries):
                try:
                    if default_storage.exists(file_path):
                        default_storage.delete(file_path)
                        self.stdout.write(f'成功删除: {file_path}')
                        logger.info(f'成功删除: {file_path}')
                        deleted_count += 1
                        break
                    else:
                        self.stdout.write(f'文件不存在: {file_path}')
                        logger.warning(f'文件不存在: {file_path}')
                        break
                except PermissionError as e:
                    if retry < max_retries - 1:
                        self.stdout.write(f'文件被锁定，等待后重试 ({retry+1}/{max_retries}): {file_path}')
                        logger.warning(f'文件被锁定，等待后重试 ({retry+1}/{max_retries}): {file_path}')
                        time.sleep(1)  # 等待1秒
                    else:
                        self.stdout.write(self.style.ERROR(f'无法删除文件(已达最大重试次数): {file_path}'))
                        logger.error(f'无法删除文件(已达最大重试次数): {file_path}')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'删除失败: {file_path}, 错误: {e}'))
                    logger.error(f'删除失败: {file_path}, 错误: {e}')
                    break

        self.stdout.write(self.style.SUCCESS(f'清理完成! 共删除了{deleted_count}个带随机后缀的重复文件'))
        logger.info(f'清理完成! 共删除了{deleted_count}个带随机后缀的重复文件')

# 设置定时任务的方法：
#
# 在Windows上:
# 1. 打开任务计划程序 (Win+R 输入 taskschd.msc)
# 2. 创建任务，设置为每天运行
# 3. 操作 -> 新建，程序/脚本设置为Python解释器路径
# 4. 添加参数: manage.py cleanup_duplicate_pdfs
# 5. 起始于: 设置Django项目目录路径
#
# 在Linux上:
# 1. 编辑crontab: crontab -e
# 2. 添加一行: 0 2 * * * cd /path/to/django/project && /path/to/python manage.py cleanup_duplicate_pdfs
#    (每天凌晨2点运行)
