from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from .models import Cart, CartItem, Collection, Customer, Order, OrderItem, Product, Review

class productSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','unit_price','inventory','description','slug','collection']
       # fields ='__all__'
    
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    # unit_price = serializers.DecimalField(max_digits=6 , decimal_places=2)
    # price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self,product:Product):
        return product.unit_price * Decimal(1.1)

    # def create(self, validated_data):
    #     product =Product(**validated_data)
    #     product.other = 1
    #     product.save()
    #     return product
    
    # def update(self, instance, validated_data):
    #     instance.unit_price = validated_data.get('unit_price')
    #     instance.save
    #     return instance
    
class collectionSerializer (serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'
        
        
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id' , 'date' , 'name' , 'description']
        
    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id,**validated_data)
    
    
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product 
        fields = ['id','title','unit_price']  
         
class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self,cart_item:CartItem):
        return cart_item.quantity * cart_item.product.unit_price
        
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price']
    
class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self,cart):
       return sum ([item.quantity * item.product.unit_price for item in cart.items.all()])
            
    class Meta: 
        model = Cart
        fields = ['id','items','total_price']
        

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    
    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the same value.')
        return value
    
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
       
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id,product_id =product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id,**self.validated_data)
            
        return self.instance
    class Meta:
        model = CartItem
        fields =['id','product_id','quantity']
    
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
        
        
class CustomerSerializer(serializers.ModelSerializer):
    
    user_id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id','user_id','phone','birth_date','membership']
        
 
class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem 
        fields = ['id','product','quantity','unit_price']
            
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id','customer','payment_status','placed_at','items']
        
        
class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields =   ['payment_status']       

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    
    
    def validate_cart_id(self,cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('Cart with given id not found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            customer=Customer.objects.get(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)
            
            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order = order,
                    product = item.product,
                    unit_price = item.product.unit_price,
                    quantity = item.quantity
                            
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=cart_id).delete()
            
            return order