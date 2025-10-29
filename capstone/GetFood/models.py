from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    calories_per_100g = models.FloatField(null=True, blank=True)
    category = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    cooking_time = models.IntegerField(help_text="Time in minutes", null=True, blank=True)
    instructions = models.TextField(blank=True)
    image = models.ImageField(upload_to="recipes/", blank=True, null=True)
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=100, default="to taste")
    unit = models.CharField(max_length=20, default="g")

    def __str__(self):
        return f"{self.quantity}{self.unit} {self.ingredient.name} for {self.recipe.name}"


class UserPantry(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Pantry"


class AISuggestionCache(models.Model):
    ingredients_hash = models.CharField(max_length=255, unique=True)
    ai_response = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Cache for {self.ingredients_hash}"


@receiver(post_save, sender=AISuggestionCache)
def clean_expired_ai_caches(sender, **kwargs):
    """Delete AI suggestions older than 1 day."""
    expiry_time = timezone.now() - timedelta(days=3)
    AISuggestionCache.objects.filter(created_at__lt=expiry_time).delete()

