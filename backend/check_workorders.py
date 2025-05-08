#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Import the WorkOrder model
from productionmgmt.models import WorkOrder

# Count and print all work orders
work_orders = WorkOrder.objects.all()
print(f"Total work orders: {work_orders.count()}")

# Print details of each work order
if work_orders.count() > 0:
    print("\nWork Order Details:")
    for wo in work_orders:
        print(f"ID: {wo.id}, No: {wo.workorder_no}, Status: {wo.status}, Product: {wo.product}")
else:
    print("\nNo work orders found in the database.")
    
    # Provide sample data to insert
    print("\nTo create a sample work order, you can run the following code:")
    print("""
from productionmgmt.models import WorkOrder
from basedata.models import Product
from django.utils import timezone

# Get a product from the database (adjust the query if needed)
product = Product.objects.first()

if product:
    # Create a sample work order
    WorkOrder.objects.create(
        workorder_no='WO-TEST-001',
        product=product,
        quantity=100,
        plan_start=timezone.now(),
        plan_end=timezone.now() + timezone.timedelta(days=7),
        status='draft',
        remark='Sample work order'
    )
    print('Sample work order created successfully')
else:
    print('No products found in the database')
    """) 