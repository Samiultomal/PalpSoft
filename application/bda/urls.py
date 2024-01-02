from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    
    path('', views.home_page, name='home_page'),
    path('shop/', views.shop_page, name='shop_page'),
    
    path('register/', views.register, name='register'),
    path('waiting-for-approval/', views.waiting_for_approval, name='waiting_for_approval'),
    path('login/', views.custom_login, name='login'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('subscribe/', views.subscribe, name='subscribe'),
    
    
    path('categories/', views.product_category_list, name='product_category_list'),
    path('categories/<int:pk>/', views.product_category_detail, name='product_category_detail'),
    path('categories/create/', views.product_category_create, name='product_category_create'),
    path('categories/update/<int:pk>/', views.product_category_update, name='product_category_update'),
    path('categories/delete/<int:pk>/', views.product_category_delete, name='product_category_delete'),
    path('export-categories/', views.export_categories, name='export_categories'),
    
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/update/<int:pk>/', views.product_update, name='product_update'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),

    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/update/<int:pk>/', views.supplier_update, name='supplier_update'),
    path('suppliers/delete/<int:pk>/', views.supplier_delete, name='supplier_delete'),

    path('logout/', views.user_logout, name='logout'),
    
    
    path('tsp/', views.tsp_view, name='tsp_view'),
    
    path('branches/', views.city_bank_branch_list, name='city_bank_branch_list'),
    path('branch/<int:pk>/', views.city_bank_branch_detail, name='city_bank_branch_detail'),
    path('branch/new/', views.city_bank_branch_create, name='city_bank_branch_create'),
    path('branch/<int:pk>/edit/', views.city_bank_branch_update, name='city_bank_branch_update'),
    path('branch/<int:pk>/delete/', views.city_bank_branch_delete, name='city_bank_branch_delete'),
    
    





]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)