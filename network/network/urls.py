
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("user/<str:user>", views.user, name="user"),
    path("posts/", views.posts, name="posts"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("follow/<str:username>", views.toggle_follow, name="toggle_follow"),
    path("following/", views.following, name="following"),
    path("users/<str:username>/posts", views.user_posts_api, name="user_posts_api"),
    path("posts/<int:post_id>", views.edit_post, name="edit_post"),
    path("posts/<int:post_id>/like", views.toggle_like, name="toggle_like"),
    path("register", views.register, name="register")
]
