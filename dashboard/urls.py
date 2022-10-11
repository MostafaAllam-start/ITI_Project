from django.urls import path
from .views import (    
                        list_posts, detail_post, delete_post, update_post, create_post,
                        list_users, detail_user, delete_user, update_user, create_user, restrict_user,
                    )
urlpatterns = [
    # posts routes
    path('posts/', list_posts, name="list_posts"),
    path('posts/create/', create_post, name="create_post"),
    path('posts/<int:pk>', detail_post, name="detail_post"),
    path('posts/update/<int:pk>', update_post, name="update_post"),
    path('posts/delete/<int:pk>', delete_post, name="delete_post"),

    # user routes
    path('users/', list_users, name="list_users"),
    path('users/create/', create_user, name="create_user"),
    path('users/<int:pk>', detail_user, name="detail_user"),
    path('users/update/<int:pk>', update_user, name="update_user"),
    path('users/delete/<int:pk>', delete_user, name="delete_user"),
    path('users/restrict/<int:pk>', restrict_user, name="restrict_user"),
]