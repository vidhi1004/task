from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Category, Product, Store, Inventory

class BaiscTests(APITestCase):
    def setUp(self):
        cat = Category.objects.create(name="Tech")
        self.store = Store.objects.create(name="Test Store")
        self.prod = Product.objects.create(title="Laptop", price=100, category=cat)
        Inventory.objects.create(store=self.store, product=self.prod, quantity=10)

    def test_search(self):
        res = self.client.get(reverse('product-search'), {'q': 'Laptop'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data[0]['title'], "Laptop")

    def test_suggest(self):
        res = self.client.get(reverse('product-search-autocomplete'), {'q': 'La'})
        self.assertIn("Laptop", res.data)

    def test_order_fail(self):
        data = {"store_id": self.store.id, "items": [{"product_id": self.prod.id, "quantity_requested": 999}]}
        res = self.client.post(reverse('order-creation'), data, format='json')
        self.assertEqual(res.data['status'], 'REJECTED')
