from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, RecipeViewSet, UserPantryViewSet
from django.contrib.auth import views as auth_views


router = DefaultRouter()
router.register("ingredients", IngredientViewSet)
router.register("recipes", RecipeViewSet)
router.register("pantries", UserPantryViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path('', views.index, name='index'),
    path("recipe/<int:recipe_id>/", views.recipe_detail, name="recipe_detail"),
    path("pantry/", views.pantry, name="pantry"),
    path("can_cook/", views.can_cook, name="can_cook"),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path("ai_suggestions/", views.ai_suggestions, name="ai_suggestions"),
    path("ai/recipe/<str:name>/", views.ai_recipe_detail, name="ai_recipe_detail"),
    path("ai/suggestions/api/", views.ai_suggestions_api, name="ai_suggestions_api"),
    path("ai/recipe/<str:recipe_name>/api/", views.ai_recipe_detail_api, name="ai_recipe_detail_api"),
    path("ai/task-status/<str:task_id>/", views.ai_task_status, name="ai_task_status"),

]
