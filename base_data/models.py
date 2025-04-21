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
