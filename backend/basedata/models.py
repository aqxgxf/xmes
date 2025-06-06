from django.db import models
import os
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.utils import timezone
from django.db.models import Max

class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name="公司名称")
    code = models.CharField(max_length=50, null=True, blank=True, verbose_name="公司代码")
    address = models.CharField(max_length=200, null=True, blank=True, verbose_name="地址")
    contact = models.CharField(max_length=50, null=True, blank=True, verbose_name="联系人")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="联系电话")
    def __str__(self):
        return self.name

class Unit(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="单位编码")
    name = models.CharField(max_length=50, verbose_name="单位名称")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    class Meta:
        verbose_name = '单位'
        verbose_name_plural = '单位'
    def __str__(self):
        return f"{self.name} ({self.code})"

class MaterialType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="材质名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="材质代码", blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name="描述")

    def __str__(self):
        return self.name

class ProductCategory(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="公司")
    code = models.CharField(max_length=20, verbose_name="产品类代码")
    display_name = models.CharField(max_length=40, verbose_name="产品类名称")
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="默认单位")
    drawing_pdf = models.FileField(upload_to='drawings/', null=True, blank=True, verbose_name="图纸PDF")
    process_pdf = models.FileField(upload_to='drawings/', null=True, blank=True, verbose_name="工艺PDF")
    material_type = models.ForeignKey(MaterialType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="材质")  # 新增
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        unique_together = ('code', 'company')
        verbose_name = '产品类'
        verbose_name_plural = '产品类'

    def __str__(self):
        return f"{self.code}-{self.display_name}"

class CategoryParam(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='params')
    name = models.CharField(max_length=100, verbose_name="参数项名称")
    display_order = models.IntegerField(default=0, help_text="参数在此产品类中的显示顺序")

    class Meta:
        unique_together = ('category', 'name')
        verbose_name = '参数项'
        verbose_name_plural = '参数项'
        ordering = ['display_order', 'id']

    def __str__(self):
        return f"{self.category.code} - {self.name} (Order: {self.display_order})"

    def save(self, *args, **kwargs):
        if not self.pk and self.display_order == 0:
            max_order = CategoryParam.objects.filter(category=self.category).aggregate(Max('display_order'))['display_order__max']
            self.display_order = (max_order or 0) + 1
        super().save(*args, **kwargs)

class Product(models.Model):
    code = models.CharField(max_length=100, unique=True, verbose_name="产品代码")
    name = models.CharField(max_length=100, verbose_name="产品名称")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, verbose_name="所属产品类")
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="单位")
    drawing_pdf = models.FileField(upload_to='drawings/', null=True, blank=True, verbose_name="图纸PDF")
    is_material = models.BooleanField(default=False, verbose_name="是否物料")
    material_type = models.ForeignKey(MaterialType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="材质")  # 新增
    def __str__(self):
        return self.name

class ProductParamValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='param_values')
    param = models.ForeignKey(CategoryParam, on_delete=models.CASCADE)
    value = models.CharField(max_length=200, verbose_name="参数值")

    class Meta:
        unique_together = ('product', 'param')
        verbose_name = '产品参数值'
        verbose_name_plural = '产品参数值'

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

class ProcessCode(models.Model):
    code = models.CharField(max_length=100, verbose_name="工艺流程代码")
    description = models.CharField(max_length=200, blank=True, verbose_name="说明")
    version = models.CharField(max_length=20, verbose_name="版本")
    process_pdf = models.FileField(upload_to='process_pdfs/', null=True, blank=True, verbose_name="工艺PDF")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
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

class ProductCategoryProcessCode(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, verbose_name="产品类")
    process_code = models.ForeignKey(ProcessCode, on_delete=models.CASCADE, verbose_name="工艺流程代码")
    is_default = models.BooleanField(default=False, verbose_name="是否默认")
    class Meta:
        unique_together = ("category", "process_code")
        verbose_name = '产品类-工艺流程代码关系'
        verbose_name_plural = '产品类-工艺流程代码关系'
    def __str__(self):
        return f"{self.category} - {self.process_code}{' (默认)' if self.is_default else ''}"

class ProcessDetail(models.Model):
    process_code = models.ForeignKey(ProcessCode, on_delete=models.CASCADE, verbose_name="工艺流程代码", related_name="details")
    step_no = models.PositiveIntegerField(verbose_name="工序号")
    step = models.ForeignKey(Process, on_delete=models.CASCADE, verbose_name="工序名")
    machine_time = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="设备时间(分钟)")
    labor_time = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="人工时间(分钟)")
    process_content = models.CharField(max_length=500, null=True, blank=True, verbose_name="工序内容")
    program_file = models.FileField(upload_to='programs/', null=True, blank=True, verbose_name="程序文件")
    required_equipment = models.CharField(max_length=200, null=True, blank=True, verbose_name="所需设备")
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
    material = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='as_material_in_bom', verbose_name="物料", limit_choices_to={'is_material': True})
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="用量")
    remark = models.CharField(max_length=200, blank=True, verbose_name="备注")
    class Meta:
        unique_together = ("bom", "material")
        verbose_name = 'BOM明细'
        verbose_name_plural = 'BOM明细'
    def __str__(self):
        return f"{self.bom} - {self.material.name} x {self.quantity}"

class Customer(Company):
    class Meta:
        proxy = True
        verbose_name = '客户'
        verbose_name_plural = '客户'

class Material(Product):
    class Meta:
        proxy = True
        verbose_name = '物料'
        verbose_name_plural = '物料'
    # 物料的材质直接复用Product的material_type字段

class CategoryMaterialRule(models.Model):
    """产品类BOM物料规则，定义产品类A的BOM物料所属产品类B"""
    source_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='material_rules', verbose_name="来源产品类")
    target_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='as_material_in_rules', verbose_name="目标物料产品类")
    created_at = models.DateTimeField(verbose_name="创建时间", default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        unique_together = ("source_category", "target_category")
        verbose_name = '产品类BOM物料规则'
        verbose_name_plural = '产品类BOM物料规则'

    def __str__(self):
        return f"{self.source_category} → {self.target_category}"

class CategoryMaterialRuleParam(models.Model):
    """物料规则参数表达式，如外径设置为${D2+3}"""
    rule = models.ForeignKey(CategoryMaterialRule, on_delete=models.CASCADE, related_name='param_expressions', verbose_name="所属规则")
    target_param = models.ForeignKey(CategoryParam, on_delete=models.CASCADE, verbose_name="目标参数")
    expression = models.CharField(max_length=200, verbose_name="表达式")
    
    class Meta:
        unique_together = ("rule", "target_param")
        verbose_name = '物料规则参数表达式'
        verbose_name_plural = '物料规则参数表达式'
        
    def __str__(self):
        return f"{self.target_param.name}: {self.expression}"


class ProductAttachment(models.Model):
    product = models.ForeignKey(Product, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='product_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '产品附件'
        verbose_name_plural = '产品附件'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.filename} for {self.product.name}' 