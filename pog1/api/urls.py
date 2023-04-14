from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginViewDef),
    path('signup/', SingupViewDef),
    path('product/', ProductView),
    path('products/<int:pk>', ProductDetailView),
    path('products/', ProductAddView),
    path('carts/<int:pk>', CartAddView),
    path('cart/<int:pk>', cartDelView),
    path('cart/', CartListView),
    path('orders/<int:pk>', orderAddView),
    path('order/', OrderView),
    path('order/<int:pk>', orderRemoveView),
    path('logout/', Logout.as_view()),
    path('user/', userListView),
]
