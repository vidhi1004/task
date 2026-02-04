from django.shortcuts import render
from apps.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Category, Store, Inventory, Order, OrderItem
from django.db import transaction
from django.db.models import Q , Case, When, Value, IntegerField
from django.core.cache import cache
from .tasks import send_conformation

class OrderCreationView(APIView):
    def post(self, request):
        data = request.data
        store_id = data.get('store_id')
        items = data.get('items', [])
        if not items:
            return Response({'error': 'No items provided in order'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({'error': 'Store not found'}, status=status.HTTP_404_NOT_FOUND)
        with transaction.atomic():
            order = Order.objects.create(store=store, status='PENDING')
            can_fulfill = True
            orders_items_to_create = []

            for item in items:
                product_id = item.get('product_id')
                quantity_requested = item.get('quantity_requested')
                inventory = Inventory.objects.select_for_update().filter(
                    store=store, product_id=product_id).first()

                if not inventory or inventory.quantity < quantity_requested:
                    can_fulfill = False
                    break
                else:
                    inventory.quantity -= quantity_requested
                    inventory.save()
                    orders_items_to_create.append(OrderItem(
                        order=order,
                        product_id=product_id,
                        quantity_requested=quantity_requested
                    ))
            if can_fulfill:
                OrderItem.objects.bulk_create(orders_items_to_create)
                order.status = 'CONFIRMED'
                order.save()
                order.refresh_from_db()
                serializer=OrderSerializer(order)
                transaction.on_commit(lambda: send_conformation.delay(order.id))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                order.status = 'REJECTED'
                order.save()
                if product_id not in store.inventories.values_list('product_id', flat=True):
                    return Response({'order_id': order.id, 'status': order.status,'message': 'Order cannot be fulfilled because product not available in store inventory.'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'order_id': order.id, 'status': order.status,'message': 'Order cannot be fulfilled due to insufficient inventory.'}, status=status.HTTP_400_BAD_REQUEST)
                
            

class OrderlistingView(APIView):
    def get(self, request,store_id):
        if not store_id:
            return Response({'error': 'store_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        order = Order.objects.filter(store=store_id).select_related(
            'store').prefetch_related('order_items__product')
        order = order.order_by('-created_at')
        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InventoryListingView(APIView):
    def get(self, request, store_id):
        if not store_id:
            return Response({'error': 'store_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        inventory = Inventory.objects.filter(
            store=store_id).select_related('product', 'store')
        inventory = inventory.order_by('product__title')
        serializer = InventorySerializer(inventory, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductSearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        products = Product.objects.all()
        cache_key = f"search_{request.get_full_path()}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)
        if query:
            products = products.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)).annotate(
                relevance=Case(
                    When(title__icontains=query, then=Value(3)),
                    When(description__icontains=query, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            
        category_name=request.query_params.get('category')
        if category_name:
            products = products.filter(category__name__iexact=category_name)
            
        price_range = request.query_params.get('price_range')
        if price_range:
            try:
                min_price, max_price = map(float, price_range.split('-'))
                products = products.filter(
                    price__gte=min_price, price__lte=max_price)
            except ValueError:
                return Response({'error': 'Invalid price_range format. Use min-max'}, status=status.HTTP_400_BAD_REQUEST)
        
        store_id = request.query_params.get('store_id')
        in_stock = request.query_params.get('in_stock')
        if store_id:
            products = products.filter(inventories__store__id=store_id)
            if in_stock is not None:
                in_stock = in_stock.lower() == 'true'
                if in_stock:
                    products = products.filter(inventories__store_id=store_id, inventories__quantity__gt=0)
                else:
                    products = products.filter(inventories__store_id=store_id, inventories__quantity=0)
        
        elif in_stock is not None:
            in_stock = in_stock.lower() == 'true'
            if in_stock:
                products = products.filter(inventories__quantity__gt=0)
            else:
                products = products.filter(inventories__quantity=0)
        sort_by =request.query_params.get('sort','relevance')
        if sort_by == 'price_asc':
            products = products.order_by('price','id')
        elif sort_by == 'price_desc':
            products = products.order_by('-price','id')
        elif sort_by == 'newest':
            products = products.order_by('-id')
        elif sort_by == 'relevance' and query:
            products = products.order_by('-relevance','title','id')
        else:
            products = products.order_by('id')
        
        products = products.distinct()
        serializer = ProductSerializer(products, many=True)
        cache.set(cache_key, serializer.data, timeout=300)  
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SearchAutoCompleteView(APIView):
    def get(self, request):
        query=request.query_params.get('q')
        if query is None or len(query) < 2:
            return Response([],status=status.HTTP_200_OK)
        suggestions=Product.objects.filter(title__icontains=query).values_list('title', flat=True).order_by('title')[:10]
        return Response(suggestions,status=status.HTTP_200_OK)
    
    
