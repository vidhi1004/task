import random
from faker import Faker
from django.core.management.base import BaseCommand
from apps.models import Category, Product, Store, Inventory 

class Command(BaseCommand):
    help = 'Seed database with Categories, Products, Stores, and Inventories'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        # 1. Create Categories
        categories = []
        for _ in range(15):
            category = Category.objects.create(name=fake.word().title())
            categories.append(category)
        self.stdout.write(self.style.SUCCESS('Successfully created 15 categories.'))

        # 2. Create Products
        products = []
        for _ in range(1050):
            product = Product.objects.create(
                title=fake.sentence(nb_words=3).rstrip('.'),
                price=round(random.uniform(5.0, 500.0), 2),
                description=fake.text(max_nb_chars=200),
                category=random.choice(categories)
            )
            products.append(product)
        self.stdout.write(self.style.SUCCESS('Successfully created 1050 products.'))

        # 3. Create Stores
        stores = []
        for _ in range(25):
            store = Store.objects.create(
                name=fake.company(),
                location=fake.address()
            )
            stores.append(store)
        self.stdout.write(self.style.SUCCESS('Successfully created 25 stores.'))

        # 4. Create Inventories 
        inventory_list = []
        for store in stores:
            sampled_products = random.sample(products, random.randint(200, 500))
            for product in sampled_products:
                inventory_list.append(
                    Inventory(
                        product=product,
                        store=store,
                        quantity=random.randint(10, 100)
                    )
                )
        
        Inventory.objects.bulk_create(inventory_list)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(inventory_list)} inventory records.'))
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully.'))