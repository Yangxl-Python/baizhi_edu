from django.urls import path

from cart import views

urlpatterns = [
    path('option/', views.CartViewSet.as_view({
        'get': 'cart_list',
        'post': 'add_cart',
        'put': 'change_expire',
        'patch': 'change_select',
        'delete': 'delete_cart'
    })),
    path('order/', views.CartViewSet.as_view({
        'get': 'get_select_course'
    })),
    path('order/<id>/', views.CartViewSet.as_view({
        'get': 'get_course_by_id'
    })),
]
