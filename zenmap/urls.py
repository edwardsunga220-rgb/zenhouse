from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),  
    path('qr/home/', views.qr_home, name='qr_home'),

    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path("pricing/", views.pricing, name="pricing"),
    path('properties/', views.property_list, name='property_list'),
    path('category/<slug:slug>/', views.maps_by_category, name='maps_by_category'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('maps/<int:pk>/', views.map_detail, name='map_detail'),
    path('maps/create/', views.main_map_create, name='main_map_create'),
    path('maps/<int:pk>/edit/', views.main_map_edit, name='main_map_edit'),
    path('maps/<int:pk>/delete/', views.main_map_delete, name='main_map_delete'),
    path('search/', views.search_maps, name='search'),
    path('dashboard/messages/', views.message_inbox, name='message_inbox'),
    path('dashboard/messages/<int:id>/process/', views.mark_message_processed, name='mark_message_processed'),
    path('dashboard/messages/<int:id>/delete/', views.delete_message, name='delete_message'),
    path('dashboard/messages/api/reply/', views.send_reply_email, name='api_send_reply'),
]
