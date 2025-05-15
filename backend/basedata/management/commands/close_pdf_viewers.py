from django.core.management.base import BaseCommand
import os
import subprocess
import time
import signal
import platform

class Command(BaseCommand):
    help = '尝试关闭所有可能正在查看PDF文件的进程，解决文件锁定问题'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='强制执行，不提示确认',
        )
        parser.add_argument(
            '--kill-browsers',
            action='store_true',
            dest='kill_browsers',
            help='同时关闭浏览器进程（可能导致用户数据丢失，谨慎使用）',
        )

    def handle(self, *args, **options):
        force = options['force']
        kill_browsers = options['kill_browsers']

        if not force:
            if kill_browsers:
                self.stdout.write(self.style.WARNING("警告：此命令将关闭所有PDF查看器和浏览器进程。这可能导致未保存的数据丢失!"))
            else:
                self.stdout.write(self.style.WARNING("警告：此命令将关闭所有PDF查看器进程。"))
            confirm = input("确定要继续吗? [y/N]: ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.ERROR("操作已取消"))
                return

        # 检查操作系统类型
        is_windows = platform.system() == 'Windows'

        if not is_windows:
            self.stdout.write(self.style.ERROR("此命令仅适用于Windows操作系统"))
            return

        self.stdout.write("开始关闭PDF查看器进程...")

        # PDF查看器进程列表
        pdf_viewers = ['AcroRd32.exe', 'Acrobat.exe', 'SumatraPDF.exe', 'foxitreader.exe',
                      'PdfXEdit.exe', 'msedge.exe', 'chrome.exe', 'firefox.exe']

        # 如果不关闭浏览器，从列表中移除
        if not kill_browsers:
            pdf_viewers = [p for p in pdf_viewers if not p in ['msedge.exe', 'chrome.exe', 'firefox.exe']]

        closed_count = 0

        for viewer in pdf_viewers:
            try:
                # 使用taskkill命令关闭进程
                result = subprocess.run(['taskkill', '/f', '/im', viewer],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)

                if "SUCCESS" in result.stdout:
                    self.stdout.write(self.style.SUCCESS(f"已关闭 {viewer} 进程"))
                    closed_count += 1
                elif "没有运行的任务" in result.stderr:
                    self.stdout.write(f"{viewer} 进程未运行")
                else:
                    self.stdout.write(self.style.WARNING(f"关闭 {viewer} 进程时出现问题: {result.stderr}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"尝试关闭 {viewer} 时出错: {e}"))

        # 尝试重启Windows资源管理器以释放文件句柄
        try:
            self.stdout.write("尝试重启Windows资源管理器...")
            subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
            time.sleep(1)
            subprocess.Popen('explorer.exe')
            self.stdout.write(self.style.SUCCESS("Windows资源管理器已重启"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"重启Windows资源管理器失败: {e}"))

        self.stdout.write(self.style.SUCCESS(f"已关闭 {closed_count} 个PDF查看器进程"))
        self.stdout.write("PDF文件现在应该不再被锁定，可以进行删除或覆盖操作")
