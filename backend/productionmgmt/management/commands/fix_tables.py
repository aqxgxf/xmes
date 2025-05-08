from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Creates missing tables in the productionmgmt app'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        
        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='productionmgmt_productionorder';"
        )
        if cursor.fetchone():
            self.stdout.write(self.style.SUCCESS('Table productionmgmt_productionorder already exists'))
            return
            
        self.stdout.write('Creating missing tables...')
        
        # Create ProductionOrder table
        cursor.execute('''
CREATE TABLE "productionmgmt_productionorder" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    "created_at" datetime NOT NULL, 
    "updated_at" datetime NOT NULL, 
    "is_deleted" bool NOT NULL, 
    "deleted_at" datetime NULL, 
    "order_number" varchar(30) NOT NULL UNIQUE, 
    "quantity" integer unsigned NOT NULL CHECK ("quantity" >= 0), 
    "delivery_date" date NOT NULL, 
    "status" varchar(20) NOT NULL, 
    "notes" text NULL, 
    "creator_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "customer_id" bigint NOT NULL REFERENCES "basedata_customer" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "product_id" bigint NOT NULL REFERENCES "basedata_product" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "updater_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
);
        ''')
        
        # Create ProductionMaterial table
        cursor.execute('''
CREATE TABLE "productionmgmt_productionmaterial" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    "created_at" datetime NOT NULL, 
    "updated_at" datetime NOT NULL, 
    "is_deleted" bool NOT NULL, 
    "deleted_at" datetime NULL, 
    "quantity" decimal NOT NULL, 
    "unit" varchar(20) NOT NULL, 
    "notes" text NULL, 
    "creator_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "material_id" bigint NOT NULL REFERENCES "basedata_product" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "updater_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "order_id" bigint NOT NULL REFERENCES "productionmgmt_productionorder" ("id") DEFERRABLE INITIALLY DEFERRED
);
        ''')
        
        # Create ProductionLog table
        cursor.execute('''
CREATE TABLE "productionmgmt_productionlog" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
    "created_at" datetime NOT NULL, 
    "updated_at" datetime NOT NULL, 
    "is_deleted" bool NOT NULL, 
    "deleted_at" datetime NULL, 
    "title" varchar(100) NOT NULL, 
    "content" text NOT NULL, 
    "log_type" varchar(20) NOT NULL, 
    "creator_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "operator_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "updater_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
    "order_id" bigint NOT NULL REFERENCES "productionmgmt_productionorder" ("id") DEFERRABLE INITIALLY DEFERRED
);
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX "productionmgmt_productionorder_creator_id_7ee85dde" ON "productionmgmt_productionorder" ("creator_id");')
        cursor.execute('CREATE INDEX "productionmgmt_productionorder_customer_id_8ad60e35" ON "productionmgmt_productionorder" ("customer_id");')
        cursor.execute('CREATE INDEX "productionmgmt_productionorder_product_id_e8bcfbd5" ON "productionmgmt_productionorder" ("product_id");')
        cursor.execute('CREATE INDEX "productionmgmt_productionorder_updater_id_f4d568cd" ON "productionmgmt_productionorder" ("updater_id");')
        
        # Update django_migrations table to mark migration as applied
        cursor.execute('''
INSERT INTO django_migrations (app, name, applied) 
VALUES ('productionmgmt', '0001_initial', datetime('now'));
        ''')
        
        self.stdout.write(self.style.SUCCESS('Successfully created missing tables')) 