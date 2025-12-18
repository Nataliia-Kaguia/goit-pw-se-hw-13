from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('author/<int:pk>/', views.author_detail, name='author_detail'),
    path('tag/<str:tag_name>/', views.tag_detail, name='tag_detail'),
    path('add_author/', views.add_author, name='add_author'),
    path('add_quote/', views.add_quote, name='add_quote'),
    path('scrape/', views.scrape_quotes, name='scrape_quotes'),
]
