from django.contrib import admin
from django.db.models import Count

from store.models import Cart, CartItem, Collection, Order, OrderItem, Product ,Customer

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','unit_price','inventory_status','collection']
    list_editable = ['unit_price']
    list_per_page = 10
    search_fields = ['title']
    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory < 10:
            return 'low'
        else:
            return 'ok'
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','membership']
    list_editable = ['membership']
    ordering =['user__first_name','user__last_name']
    list_per_page = 10
    list_select_related = ['user'] 

admin.site.register(Cart)
admin.site.register(CartItem)

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_disply = ['title']
    def products_count (self,collection):
        return collection.products_count
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count = Count('product'))
    
