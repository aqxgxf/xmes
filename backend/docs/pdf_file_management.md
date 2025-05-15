# PDF文件管理说明文档

## 问题概述

在系统中上传PDF文件（图纸和工艺文档）时，可能会遇到以下问题：

1. **随机后缀问题**：系统默认使用Django的存储机制，当上传同名文件时会自动添加随机后缀，导致多个相同文件的副本存在。
2. **文件锁定问题**：尝试删除或覆盖正在被查看的PDF文件时，会遇到"文件被占用"的错误。
3. **文件路径引用问题**：数据库中可能引用了带随机后缀的文件路径，而实际文件可能已经不存在。

## 修复方案

我们已经实现了以下修复方案：

1. **自定义存储处理**：修改了文件上传逻辑，使用固定命名规则，避免生成随机后缀。
2. **文件内容保存**：先保存数据库记录，再手动处理文件写入，避免Django自动生成随机后缀。
3. **清理工具**：提供了多个命令行工具，用于清理带随机后缀的文件和修复数据库引用。

## 工具使用说明

### 1. 强制清理重复PDF文件

此命令用于清理带随机后缀的PDF文件，并处理文件锁定问题：

```bash
python manage.py force_remove_duplicate_files
```

参数说明：
- `--directory=drawings`：指定要清理的目录（默认：drawings）
- `--delay=2`：文件删除重试之间的等待时间（秒）
- `--max-retries=5`：删除文件的最大重试次数
- `--kill-explorer`：尝试重启Windows资源管理器以释放文件锁（谨慎使用）

示例：
```bash
# 基本使用
python manage.py force_remove_duplicate_files

# 使用高级选项
python manage.py force_remove_duplicate_files --directory=process_pdfs --delay=3 --max-retries=10
```

### 2. 定期清理重复PDF文件（计划任务）

此命令用于设置为计划任务，定期清理可能出现的带随机后缀的文件：

```bash
python manage.py cleanup_duplicate_pdfs
```

参数说明：
- `--directory=drawings`：指定要清理的目录（默认：drawings）
- `--max-retries=3`：删除文件的最大重试次数
- `--log-only`：只记录要删除的文件，不实际删除（用于测试）

设置计划任务：

在Windows上：
1. 打开任务计划程序（Win+R 输入 taskschd.msc）
2. 创建任务，设置为每天运行
3. 操作 -> 新建，程序/脚本设置为Python解释器路径（例如：`F:\xmes\backend\venv\Scripts\python.exe`）
4. 添加参数：`manage.py cleanup_duplicate_pdfs`
5. 起始于：设置Django项目目录路径（例如：`F:\xmes\backend`）

在Linux上：
```bash
# 编辑crontab
crontab -e

# 添加以下行（每天凌晨2点运行）
0 2 * * * cd /path/to/django/project && /path/to/python manage.py cleanup_duplicate_pdfs
```

### 3. 修复数据库引用

如果数据库中的引用仍然指向带随机后缀的文件，可以使用以下命令修复：

```bash
python manage.py fix_pdf_paths
```

此命令会：
1. 扫描所有产品类别、工艺流程代码和产品记录
2. 检查它们引用的PDF文件路径是否包含随机后缀
3. 更新数据库记录，使它们引用标准命名的文件

## 最佳实践

为避免未来出现类似问题，请遵循以下最佳实践：

1. **定期运行清理命令**：设置计划任务，定期运行`cleanup_duplicate_pdfs`命令。
2. **避免并发操作**：尽量避免在同一时间多人同时上传/修改同一个文件。
3. **关闭文件后操作**：在尝试删除或更新PDF文件之前，确保关闭所有可能占用该文件的程序（PDF查看器、浏览器等）。
4. **定期检查**：定期检查`drawings`和`process_pdfs`目录，确保没有累积大量带随机后缀的文件。

## 常见问题解决

### 1. "另一个程序正在使用此文件"错误

如果遇到此错误，可能是PDF文件正在被查看。请：
- 关闭所有PDF查看器和浏览器窗口
- 使用`force_remove_duplicate_files`命令尝试再次删除
- 如果仍然失败，可以尝试使用`--kill-explorer`参数（谨慎使用）或重启服务器

### 2. 上传文件后无法查看

可能原因：
- 文件上传后路径未正确保存
- 文件名中包含随机后缀，导致前端无法正确引用

解决方法：
1. 检查数据库中保存的文件路径是否正确
2. 运行`fix_pdf_paths`命令修复数据库引用
3. 确认文件实际存在于指定位置

### 3. 文件仍然生成随机后缀

如果文件上传后仍然生成随机后缀，请：
1. 确认最新的代码已正确部署
2. 检查`OverwriteStorage`类是否正常工作
3. 暂时关闭所有上传，运行清理命令，然后再恢复上传功能

## 技术说明

本修复方案涉及以下技术点：

1. **自定义Storage类**：通过继承`FileSystemStorage`并覆盖`get_available_name`方法，阻止自动添加随机后缀。
2. **安全删除机制**：实现带重试的文件删除流程，处理文件锁定情况。
3. **事务处理**：确保数据库更新和文件系统操作的一致性。

详细的实现代码可以查看：
- `basedata/models.py`中的`ProductCategory.save`方法
- `basedata/management/commands/`目录中的清理命令实现
