from django.contrib import admin
from .models import Recipe, UserPantry, Ingredient

for model in (Recipe, UserPantry, Ingredient):
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
