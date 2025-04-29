from django.db import models
import os
from django.core.files.storage import default_storage
from utils.tools import convert_image_to_pdf
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
import time

def safe_delete_file(file_path, max_retries=3):
    for _ in range(max_retries):
        try:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
            return
        except PermissionError:
            time.sleep(0.1)
    # 最后一次尝试
    try:
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
    except Exception as e:
        print(f"删除文件失败: {file_path}, 错误: {e}")
class Company(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="公司名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="公司代码")
    address = models.CharField(max_length=100, blank=True, verbose_name="地址")
    contact = models.CharField(max_length=50, blank=True, verbose_name="联系人")
    phone = models.CharField(max_length=30, blank=True, verbose_name="联系电话")

    def __str__(self):
        return self.name

def category_pdf_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    name = instance.name.replace('/', '_')
    company = instance.company.name.replace('/', '_')
    return f'drawings/{name}-{company}.{ext}'

def category_process_pdf_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    name = instance.name.replace('/', '_')
    company = instance.company.name.replace('/', '_')
    return f'drawings/{name}-{company}-process.{ext}'

class ProductCategory(models.Model):
    name = models.CharField(max_length=10, verbose_name="产品类名称")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="公司")
    drawing_pdf = models.FileField(upload_to=category_pdf_upload_to, null=True, blank=True, verbose_name="图纸PDF")
    process_pdf = models.FileField(upload_to=category_process_pdf_upload_to, null=True, blank=True, verbose_name="工艺PDF")  # 修正upload_to

    def get_drawing_pdf(self):
        if self.drawing_pdf and hasattr(self.drawing_pdf, 'url'):
            return self.drawing_pdf.url
        return None

    def get_process_pdf(self):
        if self.process_pdf and hasattr(self.process_pdf, 'url'):
            return self.process_pdf.url
        return None

    def save(self, *args, **kwargs):
        # 只在有新上传文件时处理drawing_pdf
        if self.drawing_pdf and hasattr(self.drawing_pdf, 'file') and isinstance(self.drawing_pdf.file, (InMemoryUploadedFile, TemporaryUploadedFile)):
            file_ext = self.drawing_pdf.name.split('.')[-1].lower()
            pdf_name = f"{self.name.replace('/', '_')}-{self.company.name.replace('/', '_')}.pdf"
            content, new_name = convert_image_to_pdf(self.drawing_pdf, pdf_name)
            if content:
                file_path = category_pdf_upload_to(self, pdf_name)
                # 只删除不是当前文件的旧文件
                if self.drawing_pdf.name != file_path:
                    safe_delete_file(file_path)
                self.drawing_pdf.save(new_name, content, save=False)
                self.drawing_pdf.name = file_path
            else:
                if file_ext == 'pdf' and self.drawing_pdf.name != pdf_name:
                    file_path = category_pdf_upload_to(self, pdf_name)
                    if self.drawing_pdf.name != file_path:
                        safe_delete_file(file_path)
                    self.drawing_pdf.name = file_path
        # 只在有新上传文件时处理process_pdf
        if self.process_pdf and hasattr(self.process_pdf, 'file') and isinstance(self.process_pdf.file, (InMemoryUploadedFile, TemporaryUploadedFile)):
            file_ext = self.process_pdf.name.split('.')[-1].lower()
            pdf_name = f"{self.name.replace('/', '_')}-{self.company.name.replace('/', '_')}-process.pdf"
            content, new_name = convert_image_to_pdf(self.process_pdf, pdf_name)
            if content:
                file_path = category_process_pdf_upload_to(self, pdf_name)
                if self.process_pdf.name != file_path:
                    safe_delete_file(file_path)
                self.process_pdf.save(new_name, content, save=False)
                self.process_pdf.name = file_path
            else:
                if file_ext == 'pdf' and self.process_pdf.name != pdf_name:
                    file_path = category_process_pdf_upload_to(self, pdf_name)
                    if self.process_pdf.name != file_path:
                        safe_delete_file(file_path)
                    self.process_pdf.name = file_path
        super().save(*args, **kwargs)


class CategoryParam(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='params')
    name = models.CharField(max_length=100, verbose_name="参数项名称")

    class Meta:
        unique_together = ('category', 'name')
        verbose_name = '参数项'
        verbose_name_plural = '参数项'

    def __str__(self):
        return f"{self.category.name} - {self.name}"

def product_pdf_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    code = instance.code.replace('/', '_')
    return f'drawings/{code}.{ext}'


class Product(models.Model):
    code = models.CharField(max_length=100, unique=True, verbose_name="产品代码")
    name = models.CharField(max_length=40, verbose_name="产品名称")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, verbose_name="所属产品类")
    drawing_pdf = models.FileField(upload_to=product_pdf_upload_to, null=True, blank=True, verbose_name="图纸PDF")

    def get_drawing_pdf(self):
        return self.drawing_pdf.url if self.drawing_pdf else (self.category.drawing_pdf.url if self.category and self.category.drawing_pdf else None)

    def save(self, *args, **kwargs):
        # 只要没有真实文件内容，强制清空，防止Django写入数据库
        if not self.drawing_pdf or not hasattr(self.drawing_pdf, 'file') or not getattr(self.drawing_pdf, 'name', None):
            self.drawing_pdf = None
        else:
            try:
                if hasattr(self.drawing_pdf, 'size') and self.drawing_pdf.size == 0:
                    self.drawing_pdf = None
            except Exception:
                self.drawing_pdf = None
        # 移除物理文件不存在时设为None的逻辑
        if self.drawing_pdf and getattr(self.drawing_pdf, 'name', None):
            file_ext = self.drawing_pdf.name.split('.')[-1].lower()
            pdf_name = f"{self.code.replace('/', '_')}.pdf"
            content, new_name = convert_image_to_pdf(self.drawing_pdf, pdf_name)
            if content:
                file_path = product_pdf_upload_to(self, pdf_name)
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                self.drawing_pdf.save(new_name, content, save=False)
            else:
                if file_ext == 'pdf' and self.drawing_pdf.name != pdf_name:
                    file_path = product_pdf_upload_to(self, pdf_name)
                    if default_storage.exists(file_path):
                        default_storage.delete(file_path)
                    self.drawing_pdf.name = pdf_name
        else:
            self.drawing_pdf = None
        # print("class product\def save\drawing_pdf值为", self.drawing_pdf)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name

class ProductParamValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='param_values')
    param = models.ForeignKey(CategoryParam, on_delete=models.CASCADE)
    value = models.CharField(max_length=200, verbose_name="参数值")

    def __str__(self):
        return f"{self.product.name} - {self.param.name}: {self.value}"

class Process(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="工序名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="工序代码")
    description = models.TextField(blank=True, verbose_name="工序描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = '工序'
        verbose_name_plural = '工序'

    def __str__(self):
        return self.name

def process_pdf_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    code = instance.code.replace('/', '_')
    version = instance.version.replace('/', '_')
    return f'process_pdfs/{code}-{version}.{ext}'


class ProcessCode(models.Model):
    code = models.CharField(max_length=100, verbose_name="工艺流程代码")  # 放宽长度限制
    description = models.CharField(max_length=200, blank=True, verbose_name="说明")
    version = models.CharField(max_length=20, verbose_name="版本")
    process_pdf = models.FileField(upload_to=process_pdf_upload_to, null=True, blank=True, verbose_name="工艺PDF")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def save(self, *args, **kwargs):
        if self.process_pdf:
            file_ext = self.process_pdf.name.split('.')[-1].lower()
            pdf_name = f"{self.code.replace('/', '_')}-{self.version.replace('/', '_')}.pdf"
            content, new_name = convert_image_to_pdf(self.process_pdf, pdf_name)
            if content:
                # 删除旧文件（如果存在）
                file_path = process_pdf_upload_to(self, pdf_name)
                if default_storage.exists(file_path):
                    default_storage.delete(file_path)
                self.process_pdf.save(new_name, content, save=False)
            else:
                # 如果是PDF，重命名为规范名
                if file_ext == 'pdf' and self.process_pdf.name != pdf_name:
                    file_path = process_pdf_upload_to(self, pdf_name)
                    if default_storage.exists(file_path):
                        default_storage.delete(file_path)
                    self.process_pdf.name = pdf_name
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("code", "version")
        verbose_name = '工艺流程代码'
        verbose_name_plural = '工艺流程代码'

    def __str__(self):
        return f"{self.code} (v{self.version})"

class ProductProcessCode(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="产品")
    process_code = models.ForeignKey(ProcessCode, on_delete=models.CASCADE, verbose_name="工艺流程代码")
    is_default = models.BooleanField(default=False, verbose_name="是否默认")

    class Meta:
        unique_together = ("product", "process_code")
        verbose_name = '产品-工艺流程代码关系'
        verbose_name_plural = '产品-工艺流程代码关系'

    def __str__(self):
        return f"{self.product} - {self.process_code}{' (默认)' if self.is_default else ''}"

class ProcessDetail(models.Model):
    process_code = models.ForeignKey(ProcessCode, on_delete=models.CASCADE, verbose_name="工艺流程代码", related_name="details")
    step_no = models.PositiveIntegerField(verbose_name="工序号")
    step = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name="工序名")
    machine_time = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="设备时间(分钟)")
    labor_time = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="人工时间(分钟)")
    program_file = models.FileField(upload_to='programs/', null=True, blank=True, verbose_name="程序文件")

    class Meta:
        unique_together = ("process_code", "step_no")
        verbose_name = '工艺流程明细'
        verbose_name_plural = '工艺流程明细'

    def __str__(self):
        return f"{self.process_code} - 工序{self.step_no}: {self.step.name}"

class BOM(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='boms', verbose_name="所属产品")
    name = models.CharField(max_length=100, verbose_name="BOM名称")
    version = models.CharField(max_length=20, verbose_name="版本", default="1.0")
    description = models.TextField(blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        unique_together = ("product", "name", "version")
        verbose_name = 'BOM'
        verbose_name_plural = 'BOM'

    def __str__(self):
        return f"{self.product.name} - {self.name} (v{self.version})"

class BOMItem(models.Model):
    bom = models.ForeignKey(BOM, on_delete=models.CASCADE, related_name='items', verbose_name="所属BOM")
    material = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='as_material_in_bom', verbose_name="物料")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="用量")
    remark = models.CharField(max_length=200, blank=True, verbose_name="备注")

    class Meta:
        unique_together = ("bom", "material")
        verbose_name = 'BOM明细'
        verbose_name_plural = 'BOM明细'

    def __str__(self):
        return f"{self.bom} - {self.material.name} x {self.quantity}"
