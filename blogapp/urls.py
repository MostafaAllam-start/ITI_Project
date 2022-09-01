from django.urls import path, include
from .feeds import LatestPostsFeed
from . import views
from django.contrib.auth import views as auth_views

app_name = 'blogapp'
urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('', include('django.contrib.auth.urls')),
    path('search/', views.post_search, name='post_search'),
    path('create/', views.create_post, name='create_post'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name="register"),
]
