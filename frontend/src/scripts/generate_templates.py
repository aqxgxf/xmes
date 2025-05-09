import os
import pandas as pd

# Define template directory
template_dir = '../../public/templates'
os.makedirs(template_dir, exist_ok=True)

# 1. Product Categories Template
product_categories_template = pd.DataFrame({
    'name': ['产品类别1', '产品类别2'],
    'company': ['公司1', '公司2'],
})
product_categories_template.to_excel(os.path.join(template_dir, 'product_categories_template.xlsx'), index=False)

# 2. Category Parameters Template
category_params_template = pd.DataFrame({
    'category': ['产品类别1', '产品类别1', '产品类别2'],
    'name': ['参数1', '参数2', '参数3'],
})
category_params_template.to_excel(os.path.join(template_dir, 'category_params_template.xlsx'), index=False)

# 3. Products Template
products_template = pd.DataFrame({
    'code': ['P001', 'P002'],
    'name': ['产品1', '产品2'],
    'price': [100.00, 200.00],
    'category': ['产品类别1', '产品类别2'],
})
products_template.to_excel(os.path.join(template_dir, 'products_template.xlsx'), index=False)

# 4. Materials Template
materials_template = pd.DataFrame({
    'code': ['M001', 'M002'],
    'name': ['物料1', '物料2'],
    'price': [50.00, 75.00],
    'category': ['产品类别1', '产品类别2'],
})
materials_template.to_excel(os.path.join(template_dir, 'materials_template.xlsx'), index=False)

# 5. Processes Template
processes_template = pd.DataFrame({
    'code': ['PR001', 'PR002'],
    'name': ['工序1', '工序2'],
    'description': ['工序1描述', '工序2描述'],
})
processes_template.to_excel(os.path.join(template_dir, 'processes_template.xlsx'), index=False)

# 6. Process Codes Template
process_codes_template = pd.DataFrame({
    'code': ['PC001', 'PC002'],
    'version': ['1.0', '2.0'],
    'description': ['工艺流程1', '工艺流程2'],
})
process_codes_template.to_excel(os.path.join(template_dir, 'process_codes_template.xlsx'), index=False)

# 7. BOMs Template
boms_template = pd.DataFrame({
    'product_code': ['P001', 'P001'],
    'name': ['主BOM', '主BOM'],
    'version': ['1.0', '1.0'],
    'material_code': ['M001', 'M002'],
    'quantity': [2, 3],
    'remark': ['备注1', '备注2'],
})
boms_template.to_excel(os.path.join(template_dir, 'boms_template.xlsx'), index=False)

print(f"Template files have been generated in {os.path.abspath(template_dir)}") 