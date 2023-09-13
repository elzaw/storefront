from django.urls import path
from .views import CartItemViewSet, CartViewSet, CustomerViewSet, OrderViewSet, ProductViewSet , CollectionViewSet, ReviewViewSet
from rest_framework_nested import routers



router = routers.DefaultRouter()
router.register('product',ProductViewSet, basename ='products')
router.register('collection',CollectionViewSet)
router.register('cart',CartViewSet)
router.register('customer',CustomerViewSet)
router.register('order',OrderViewSet, basename ='order')

products_router = routers.NestedDefaultRouter(router,'product',lookup='product')
products_router.register('reviews',ReviewViewSet,basename='product_review')


items_router = routers.NestedDefaultRouter(router,'cart',lookup='cart')
items_router.register('items',CartItemViewSet,basename='cart_items')




urlpatterns = router.urls + products_router.urls + items_router.urls
