from django.urls import path

from . import views

app_name = "encyclopedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>/", views.entry_page, name="entry"),
    path("search/", views.search, name="search"),
    path("create/", views.create_page, name="create"),
    path("edit/<str:title>/", views.edit_page, name="edit"),
    path("save_edit/<str:title>/", views.save_edit, name="save_edit"),
    path("random/", views.random_page, name="random"),   
]
