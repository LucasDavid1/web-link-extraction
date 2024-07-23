from django.urls import path
from scraper import views


urlpatterns = [
    path('', views.page_list, name='page_list'),
    path('page/<int:page_id>/', views.page_detail, name='page_detail'),
    path('add/', views.add_page, name='add_page'),
]
