from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
class Product(models.Model):
    title = models.CharField(max_length=100,db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    def __str__(self):
        return self.title
class Store(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name
class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventories')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventories')
    quantity = models.PositiveIntegerField()
    class Meta:
        unique_together = ('product', 'store')
    def __str__(self):
        return f"{self.product.title} at {self.store.name}: {self.quantity}"
    
class Order(models.Model):
    status_option=(
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('REJECTED', 'Rejected'),
    )
    store=models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    status=models.CharField(max_length=10, choices=status_option)
    created_at=models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order=models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_requested=models.PositiveIntegerField()