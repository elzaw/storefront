
from multiprocessing import context
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import SearchFilter,OrderingFilter
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly, ViewCustomerHistoryPermission 
from .filter import ProductFilter
from .models import Cart, CartItem, Collection, Customer, Order, Product, Review
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ReviewSerializer, UpdateCartItemSerializer, UpdateOrderSerializer, collectionSerializer, productSerializer 
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , IsAdminUser
# Create your views here.



class ProductViewSet(ModelViewSet):
     
        queryset = Product.objects.all()
        serializer_class = productSerializer
        filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
        filter_class = ProductFilter
        pagination_class = DefaultPagination
        search_fields = ['title','description']
        ordering_fields = ['unit_price','last_update']
        permission_classes = [IsAdminOrReadOnly]
    
        def get_serializer_context(self):
            return {'request':self.request}

        def delete(self,request,pk):
            product = get_object_or_404(Product,pk=pk)
            product.delete()
            
class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = collectionSerializer
    permission_classes = [IsAdminOrReadOnly]
        
    def get_serializer_context(self):
        return {'request':self.request}

    def delete(self,request,pk):
        collection = get_object_or_404(Collection,pk=pk)
        collection.delete()
    
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        return Review.objects.filter(product_id = self.kwargs['product_pk'])
        
    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}
    
class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
    def delete(self,request,pk):
        cart = get_object_or_404(Cart,pk=pk)
        cart.delete()
        
class CartItemViewSet(ModelViewSet):
    
    http_method_names = ['get','post','patch','delete']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
    
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])
    
class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]
    
    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAuthenticated()]
    
    @action(detail=True,permission_classes = [ViewCustomerHistoryPermission])
    def history(self,request,pk):
        return Response('ok')
    
    
    @action(detail=False, methods=['GET','PUT'],permission_classes = [IsAuthenticated])
    def me(self,request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET': 
            serializer = CustomerSerializer(customer)
            return  Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
               
class OrderViewSet(ModelViewSet):
    http_method_names = ['get','patch','delete','options','head']    
    
    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data,context={'user_id':self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
    
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        
        customer_id  = Customer.objects.get(user_id=self.request.user.id)
        return Order.objects.filter(customer_id = customer_id)
        