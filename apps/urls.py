from .views import OrderCreationView, OrderlistingView, InventoryListingView, SearchAutoCompleteView, ProductSearchView
from django.urls import path

urlpatterns = [
    path('orders/', OrderCreationView.as_view(), name='order-creation'),
    path('stores/<int:store_id>/orders/',OrderlistingView.as_view(), name='order-listing'),
    path('stores/<int:store_id>/inventory/',InventoryListingView.as_view(), name='inventory-listing'),
    path('api/search/products/', ProductSearchView.as_view(), name='product-search'),
    path('api/search/suggest/',SearchAutoCompleteView.as_view(), name='product-search-autocomplete'),
    
]