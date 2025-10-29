from django.core.management.base import BaseCommand
from django.core.files import File
from GetFood.models import Ingredient, Recipe, RecipeIngredient
import os

BASE_IMAGE_PATH = os.path.join("media", "seed_images")


class Command(BaseCommand):
    help = "Seed the database with example ingredients and recipes (with all attributes)."

    def handle(self, *args, **options):
        # ---- INGREDIENTS ----
        ingredients_data = [
            {"name": "Eggs", "calories_per_100g": 155, "category": "Protein"},
            {"name": "Flour", "calories_per_100g": 364, "category": "Grains"},
            {"name": "Sugar", "calories_per_100g": 387, "category": "Sweeteners"},
            {"name": "Milk", "calories_per_100g": 42, "category": "Dairy"},
            {"name": "Butter", "calories_per_100g": 717, "category": "Dairy"},
            {"name": "Salt", "calories_per_100g": 0, "category": "Seasoning"},
            {"name": "Olive Oil", "calories_per_100g": 884, "category": "Oil"},
            {"name": "Chicken Breast", "calories_per_100g": 165, "category": "Protein"},
            {"name": "Tomato", "calories_per_100g": 18, "category": "Vegetables"},
            {"name": "Onion", "calories_per_100g": 40, "category": "Vegetables"},
            {"name": "Garlic", "calories_per_100g": 149, "category": "Vegetables"},
            {"name": "Rice", "calories_per_100g": 130, "category": "Grains"},
            {"name": "Cheese", "calories_per_100g": 402, "category": "Dairy"},
            {"name": "Beef", "calories_per_100g": 250, "category": "Protein"},
            {"name": "Potato", "calories_per_100g": 77, "category": "Vegetables"},
            {"name": "Pepper", "calories_per_100g": 40, "category": "Vegetables"},
            {"name": "Carrot", "calories_per_100g": 41, "category": "Vegetables"},
            {"name": "Lettuce", "calories_per_100g": 15, "category": "Vegetables"},
            {"name": "Bread", "calories_per_100g": 265, "category": "Grains"},
            {"name": "Chocolate", "calories_per_100g": 546, "category": "Sweeteners"},
        ]

        ingredients = {}
        for data in ingredients_data:
            obj, created = Ingredient.objects.get_or_create(
                name=data["name"],
                defaults={"calories_per_100g": data["calories_per_100g"], "category": data["category"]},
            )
            recipes_data = [
                {
                    "name": "Spaghetti Bolognese",
                    "description": "Classic Italian pasta with a rich beef and tomato sauce.",
                    "cooking_time": 45,
                    "instructions": "1. Cook pasta.\n2. Brown beef with onion and garlic.\n3. Add tomato and simmer.",
                    "image": "spaghetti.jpg",
                    "ingredients": [
                        ("Beef", "200", "g"),
                        ("Tomato", "2", "pcs"),
                        ("Onion", "1", "pcs"),
                        ("Garlic", "2", "cloves"),
                        ("Salt", "1", "tsp"),
                        ("Pepper", "0.5", "tsp"),
                    ],
                },
                {
                    "name": "Pancakes",
                    "description": "Fluffy pancakes perfect for breakfast.",
                    "cooking_time": 15,
                    "instructions": "1. Mix flour, sugar, milk, and eggs.\n2. Fry on a pan with butter.",
                    "image": "Pancakes.jpg",
                    "ingredients": [
                        ("Flour", "100", "g"),
                        ("Milk", "200", "ml"),
                        ("Eggs", "2", "pcs"),
                        ("Sugar", "1", "tbsp"),
                        ("Butter", "20", "g"),
                    ],
                },
                {
                    "name": "Chicken Fried Rice",
                    "description": "Quick stir-fried rice with chicken, eggs, and veggies.",
                    "cooking_time": 20,
                    "instructions": "1. Cook rice.\n2. Stir-fry chicken, add veggies and rice.",
                    "image": "Chicken.jpg",
                    "ingredients": [
                        ("Rice", "200", "g"),
                        ("Chicken Breast", "150", "g"),
                        ("Eggs", "2", "pcs"),
                        ("Onion", "1", "pcs"),
                        ("Carrot", "1", "pcs"),
                        ("Salt", "1", "tsp"),
                    ],
                },
                {
                    "name": "Chocolate Cake",
                    "description": "Rich and moist chocolate cake.",
                    "cooking_time": 60,
                    "instructions": "1. Mix all ingredients.\n2. Bake for 45 minutes at 180°C.",
                    "image": "Chocolate.jpg",
                    "ingredients": [
                        ("Flour", "150", "g"),
                        ("Sugar", "100", "g"),
                        ("Butter", "100", "g"),
                        ("Eggs", "2", "pcs"),
                        ("Chocolate", "100", "g"),
                    ],
                },
                {
                    "name": "Caesar Salad",
                    "description": "Crisp lettuce salad with cheese and croutons.",
                    "cooking_time": 10,
                    "instructions": "1. Chop lettuce.\n2. Mix with cheese and croutons.",
                    "image": "Caesar.jpg",
                    "ingredients": [
                        ("Lettuce", "100", "g"),
                        ("Cheese", "50", "g"),
                        ("Bread", "2", "slices"),
                        ("Olive Oil", "1", "tbsp"),
                        ("Salt", "0.5", "tsp"),
                    ],
                },
                {
                    "name": "Garlic Bread",
                    "description": "Toasted bread with garlic butter spread.",
                    "cooking_time": 10,
                    "instructions": "1. Mix butter with garlic.\n2. Spread on bread and toast.",
                    "image": "Garlic.jpg",
                    "ingredients": [
                        ("Bread", "3", "slices"),
                        ("Butter", "20", "g"),
                        ("Garlic", "2", "cloves"),
                        ("Salt", "pinch", "tsp"),
                    ],
                },
                {
                    "name": "Mashed Potatoes",
                    "description": "Creamy mashed potatoes with butter and milk.",
                    "cooking_time": 25,
                    "instructions": "1. Boil potatoes.\n2. Mash with butter and milk.",
                    "image": "potatoes.jpg",
                    "ingredients": [
                        ("Potato", "300", "g"),
                        ("Butter", "50", "g"),
                        ("Milk", "100", "ml"),
                        ("Salt", "1", "tsp"),
                    ],
                },
                {
                    "name": "Omelette",
                    "description": "Simple egg omelette with onions and cheese.",
                    "cooking_time": 10,
                    "instructions": "1. Beat eggs.\n2. Add onions and cheese.\n3. Fry until golden.",
                    "image": "Omelette.jpg",
                    "ingredients": [
                        ("Eggs", "3", "pcs"),
                        ("Onion", "0.5", "pcs"),
                        ("Cheese", "30", "g"),
                        ("Salt", "0.5", "tsp"),
                        ("Pepper", "pinch", "tsp"),
                    ],
                },
                {
                    "name": "Grilled Chicken",
                    "description": "Tender chicken breast grilled with olive oil and pepper.",
                    "cooking_time": 30,
                    "instructions": "1. Marinate chicken.\n2. Grill until cooked through.",
                    "image": "grilled.jpg",
                    "ingredients": [
                        ("Chicken Breast", "200", "g"),
                        ("Olive Oil", "1", "tbsp"),
                        ("Salt", "1", "tsp"),
                        ("Pepper", "0.5", "tsp"),
                    ],
                },
                {
                    "name": "Beef Stew",
                    "description": "Hearty stew with beef, carrots, and potatoes.",
                    "cooking_time": 90,
                    "instructions": "1. Brown beef.\n2. Add vegetables and simmer until tender.",
                    "image": "beef.jpg",
                    "ingredients": [
                        ("Beef", "250", "g"),
                        ("Carrot", "2", "pcs"),
                        ("Potato", "2", "pcs"),
                        ("Onion", "1", "pcs"),
                        ("Salt", "1", "tsp"),
                    ],
                },
                {
                    "name": "Fish Tacos",
                    "description": "Crispy fish wrapped in soft tortillas with fresh toppings.",
                    "cooking_time": 25,
                    "instructions": "1. Fry fish.\n2. Assemble tacos with toppings.\n3. Serve with lime.",
                    "image": "Fish_Tacos.jpeg",
                    "ingredients": [
                        ("Fish Fillet", "200", "g"),
                        ("Tortilla", "3", "pcs"),
                        ("Lettuce", "50", "g"),
                        ("Tomato", "1", "pcs"),
                        ("Lime", "1", "pcs"),
                    ],
                },
                {
                    "name": "Vegetable Stir Fry",
                    "description": "Colorful vegetables stir-fried in a savory soy sauce glaze.",
                    "cooking_time": 20,
                    "instructions": "1. Chop vegetables.\n2. Stir-fry with soy sauce and garlic.",
                    "image": "stir_fry.jpeg",
                    "ingredients": [
                        ("Carrot", "1", "pcs"),
                        ("Bell Pepper", "1", "pcs"),
                        ("Broccoli", "100", "g"),
                        ("Soy Sauce", "1", "tbsp"),
                        ("Garlic", "2", "cloves"),
                    ],
                },
                {
                    "name": "Shrimp Alfredo Pasta",
                    "description": "Creamy Alfredo pasta with juicy shrimp and parmesan.",
                    "cooking_time": 30,
                    "instructions": "1. Cook pasta.\n2. Make Alfredo sauce.\n3. Add shrimp and mix well.",
                    "image": "shrimp_alfredo.jpeg",
                    "ingredients": [
                        ("Shrimp", "150", "g"),
                        ("Pasta", "200", "g"),
                        ("Cream", "100", "ml"),
                        ("Cheese", "50", "g"),
                        ("Butter", "20", "g"),
                    ],
                },
                {
                    "name": "Mushroom Risotto",
                    "description": "Rich, creamy risotto made with mushrooms and parmesan.",
                    "cooking_time": 40,
                    "instructions": "1. Sauté mushrooms.\n2. Add rice and broth gradually until creamy.",
                    "image": "risotto.jpeg",
                    "ingredients": [
                        ("Rice", "200", "g"),
                        ("Mushroom", "100", "g"),
                        ("Cheese", "50", "g"),
                        ("Onion", "1", "pcs"),
                        ("Butter", "30", "g"),
                    ],
                },
                {
                    "name": "Greek Salad",
                    "description": "Refreshing salad with feta, cucumber, and olives.",
                    "cooking_time": 10,
                    "instructions": "1. Chop vegetables.\n2. Mix with olive oil and feta.",
                    "image": "greek_salad.jpeg",
                    "ingredients": [
                        ("Tomato", "2", "pcs"),
                        ("Cucumber", "1", "pcs"),
                        ("Cheese", "50", "g"),
                        ("Olive Oil", "1", "tbsp"),
                        ("Onion", "0.5", "pcs"),
                    ],
                },
                {
                    "name": "Lentil Soup",
                    "description": "Comforting lentil soup with carrots and spices.",
                    "cooking_time": 45,
                    "instructions": "1. Boil lentils.\n2. Add vegetables and simmer until soft.",
                    "image": "lentil_soup.jpeg",
                    "ingredients": [
                        ("Lentils", "200", "g"),
                        ("Carrot", "2", "pcs"),
                        ("Onion", "1", "pcs"),
                        ("Garlic", "2", "cloves"),
                        ("Salt", "1", "tsp"),
                    ],
                },
                {
                    "name": "Stuffed Peppers",
                    "description": "Bell peppers filled with rice, beef, and spices.",
                    "cooking_time": 50,
                    "instructions": "1. Mix filling.\n2. Stuff peppers and bake until tender.",
                    "image": "stuffed_peppers.jpeg",
                    "ingredients": [
                        ("Bell Pepper", "3", "pcs"),
                        ("Rice", "150", "g"),
                        ("Beef", "200", "g"),
                        ("Tomato", "1", "pcs"),
                        ("Onion", "1", "pcs"),
                    ],
                },

            ]
            ingredients[data["name"]] = obj

        self.stdout.write(self.style.SUCCESS(f"✅ Added/verified {len(ingredients)} ingredients."))

        # ---- RECIPES ----

        Recipe.objects.all().delete()
        RecipeIngredient.objects.all().delete()

        for data in recipes_data:
            recipe, _ = Recipe.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "cooking_time": data["cooking_time"],
                    "instructions": data["instructions"],
                },
            )
            if data.get("image"):
                image_path = os.path.join(BASE_IMAGE_PATH, data["image"])
                if os.path.exists(image_path):
                    with open(image_path, "rb") as f:
                        recipe.image.save(data["image"], File(f), save=True)

            recipe.save()
            recipe.ingredients.clear()
            for ing_name, qty, unit in data["ingredients"]:
                ing = ingredients.get(ing_name)
                if ing:
                    RecipeIngredient.objects.get_or_create(
                        recipe=recipe,
                        ingredient=ing,
                        defaults={"quantity": qty, "unit": unit},
                    )

        self.stdout.write(self.style.SUCCESS(f"🍽️ Added/verified {len(recipes_data)} recipes with ingredients."))
        self.stdout.write(self.style.SUCCESS("🎉 Database seeding complete!"))
