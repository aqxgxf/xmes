# PDF文件命名问题解决方案

## 问题描述

在XMES系统中，上传PDF文件（如产品图纸和工艺文档）后出现以下问题：

1. **随机后缀问题**：系统自动添加随机后缀到文件名，如`BB01-ATG-图纸_8BuMn1P.pdf`而不是预期的`BB01-ATG-图纸.pdf`。
2. **文件锁定问题**：尝试删除被查看中的PDF文件时出现"另一个程序正在使用此文件"错误。
3. **查看失败问题**：由于随机后缀的存在，前端查看PDF文件时提示"无法加载PDF文件:文件可能不存在或地址无效"。

## 根本原因分析

1. **Django自动添加随机后缀**：Django的`FileSystemStorage`类在保存同名文件时会自动添加随机后缀，以避免覆盖已存在的文件。这是Django的默认行为。

2. **文件锁定机制**：Windows系统中，当PDF文件被其他程序（如浏览器或PDF查看器）打开时，文件被锁定，无法删除或修改。

3. **前端引用固定路径**：前端代码引用的是不带随机后缀的文件路径，而实际保存的文件带有随机后缀，导致无法找到文件。

## 全面解决方案

### 1. 自定义存储类

创建了`OverwriteStorage`类继承自`FileSystemStorage`，覆盖`get_available_name`方法，使其总是返回原始文件名而不添加随机后缀：

```python
class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        """返回给定的文件名，如果该名称的文件已存在，则删除它"""
        if self.exists(name):
            try:
                self.delete(name)
                print(f"已删除同名文件: {name}")
            except Exception as e:
                print(f"删除同名文件 {name} 时出错: {e}")
        return name

# 使用自定义存储
pdf_storage = OverwriteStorage(location=os.path.join(settings.MEDIA_ROOT))
```

### 2. 改进模型的save方法

修改了`ProductCategory.save`方法，实现了更可靠的文件处理逻辑：

1. 先读取文件内容到内存
2. 保存数据库记录（更新文件路径字段）
3. 手动保存文件内容，避免Django自动处理
4. 添加清理相关文件的功能

```python
def save(self, *args, **kwargs):
    # 处理文件的状态变量
    drawing_changed = False
    process_changed = False

    # 准备工作：保存文件的临时变量
    drawing_file_content = None
    process_file_content = None
    drawing_file_name = None
    process_file_name = None

    # ... 文件处理逻辑 ...

    # 保存数据库记录
    result = super().save(*args, **kwargs)

    # 保存文件内容 - 在数据库更新后进行
    if drawing_changed and drawing_file_content:
        # 构建完整文件路径
        drawing_file_path = f"drawings/{drawing_file_name}"
        # 尝试删除旧文件和随机后缀文件
        self._cleanup_related_files_safe("图纸")
        # 保存新文件 - 直接写入，避免自动生成随机后缀
        default_storage.save(drawing_file_path, ContentFile(drawing_file_content))

    # ... 工艺文件保存 ...

    return result
```

### 3. 安全清理相关文件

添加了`_cleanup_related_files_safe`方法，安全地清理相关的文件，处理文件锁定问题：

```python
def _cleanup_related_files_safe(self, file_type):
    """更安全地清理相关的文件，处理文件锁定问题"""
    try:
        # 列出drawings目录下的所有文件
        files = default_storage.listdir('drawings')[1]
        code = self.code.replace('/', '_')
        company_name = self.company.name.replace('/', '_')

        # 要保留的标准文件名
        standard_filename = f'{code}-{company_name}-{file_type}.pdf'

        # 处理随机后缀文件
        prefix = f"{code}-{company_name}-{file_type}"
        for f in files:
            if f.startswith(prefix) and f != standard_filename and f.endswith('.pdf'):
                try:
                    full_path = f'drawings/{f}'
                    if default_storage.exists(full_path):
                        # 带重试的删除逻辑
                        # ...
                except Exception as e:
                    print(f"删除文件失败: {full_path}, 错误: {e}")
    except Exception as e:
        print(f"清理{file_type}相关文件时出错: {e}")
```

### 4. 专用上传API

创建了专门的API端点用于文件上传，避免使用常规更新操作：

```python
@action(detail=True, methods=['post'])
def upload_drawing(self, request, pk=None):
    """上传图纸PDF的专用端点，避免使用常规更新生成随机后缀"""
    try:
        category = self.get_object()
        file = request.FILES.get('file')

        # ... 文件验证 ...

        # 设置文件名
        code = category.code.replace('/', '_')
        company_name = category.company.name.replace('/', '_')
        filename = f"{code}-{company_name}-图纸.pdf"
        file_path = f"drawings/{filename}"

        # 删除旧文件（如果存在）
        category._cleanup_related_files_safe("图纸")

        # 使用OverwriteStorage手动保存文件
        content = file.read()
        pdf_storage.save(file_path, ContentFile(content))

        # 更新模型字段
        category.drawing_pdf.name = file_path
        category.save(update_fields=['drawing_pdf'])

        return Response({'success': True, 'path': category.drawing_pdf.url})
    except Exception as e:
        return Response({'error': str(e)}, status=500)
```

### 5. 实用管理命令

创建了多个管理命令，用于处理文件锁定问题和清理随机后缀文件：

1. **close_pdf_viewers**: 关闭所有正在查看PDF的进程，解决文件锁定问题
2. **force_remove_duplicate_files**: 强制删除带随机后缀的重复文件
3. **cleanup_duplicate_pdfs**: 用于计划任务，定期清理随机后缀文件
4. **reset_pdf_storage**: 完全重置PDF存储，删除所有文件并重新生成

### 6. 改进前端查看器

改进了前端PDF查看器组件，添加时间戳参数避免缓存问题：

```javascript
// 添加时间戳参数以避免浏览器缓存
pdfUrl.value = decodedUrl.includes('?')
  ? `${decodedUrl}&_t=${Date.now()}`
  : `${decodedUrl}?_t=${Date.now()}`
```

## 使用方法

### 上传新文件

使用`ProductCategorySerializer`中的标准字段或通过专用API端点`/api/product-categories/{id}/upload_drawing/`上传文件，现在文件将使用固定名称而不会添加随机后缀。

### 清理现有问题文件

如果系统中已有带随机后缀的文件，可以使用以下命令之一：

```bash
# 关闭PDF查看器
python manage.py close_pdf_viewers --force

# 强制删除带随机后缀的文件
python manage.py force_remove_duplicate_files

# 完全重置PDF存储
python manage.py reset_pdf_storage --force
```

### 定期维护

设置定期任务运行清理命令：

```bash
# Windows任务计划程序
# 每天凌晨2点运行
python manage.py cleanup_duplicate_pdfs
```

## 总结

通过以上解决方案，我们彻底解决了PDF文件命名问题：

1. **防止生成随机后缀**：自定义存储类阻止Django添加随机后缀
2. **安全删除冗余文件**：提供多种工具和方法安全地删除带随机后缀的冗余文件
3. **处理文件锁定**：提供解决Windows文件锁定问题的工具
4. **优化上传体验**：提供专用API端点确保文件上传的一致性和可靠性

这些改进确保系统中的PDF文件命名一致、可预测且易于管理。
