from django.urls import path
from scraper import views


urlpatterns = [
    path('', views.page_list, name='page_list'),
    path('page/<int:page_id>/', views.page_detail, name='page_detail'),
    path('add/', views.add_page, name='add_page'),
    path('page-detail/<uuid:page_id>/', views.page_detail, name='page_detail'),
    path('get_link_count/<uuid:page_id>/', views.get_link_count, name='get_link_count'),
    path('delete_page/<uuid:page_id>/', views.delete_page, name='delete_page'),
]
