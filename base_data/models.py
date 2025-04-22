from django.db import models

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="公司名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="公司代码")
    address = models.CharField(max_length=100, blank=True, verbose_name="地址")
    contact = models.CharField(max_length=50, blank=True, verbose_name="联系人")
    phone = models.CharField(max_length=30, blank=True, verbose_name="联系电话")

    def __str__(self):
        return self.name

class ProductCategory(models.Model):
    name = models.CharField(max_length=10, verbose_name="产品类名称")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="公司")
    drawing_pdf = models.FileField(upload_to='drawings/', null=True, blank=True, verbose_name="图纸PDF")  # 新增字段

    def __str__(self):
        return self.name

class CategoryParam(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='params')
    name = models.CharField(max_length=100, verbose_name="参数项名称")

    class Meta:
        unique_together = ('category', 'name')
        verbose_name = '参数项'
        verbose_name_plural = '参数项'

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Product(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="产品代码")
    name = models.CharField(max_length=40, verbose_name="产品名称")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, verbose_name="所属产品类")
    drawing_pdf = models.FileField(upload_to='drawings/', null=True, blank=True, verbose_name="图纸PDF")  # 新增字段

    def get_drawing_pdf(self):
        return self.drawing_pdf.url if self.drawing_pdf else (self.category.drawing_pdf.url if self.category and self.category.drawing_pdf else None)

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

class ProcessCode(models.Model):
    code = models.CharField(max_length=30, verbose_name="工艺流程代码")
    description = models.CharField(max_length=200, blank=True, verbose_name="说明")
    version = models.CharField(max_length=20, verbose_name="版本")
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
