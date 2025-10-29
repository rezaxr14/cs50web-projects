recipe_names = ["Spaghetti Bolognese",
                "Pancakes",
                "Chicken Fried Rice"
                "Chocolate Cake",
                "Caesar Salad",
                "Garlic Bread",
                "Mashed Potatoes",
                "Omelette",
                "Grilled Chicken",
                "Beef Stew",
                "Fish Tacos",
                "Vegetable Stir Fry"
                "Shrimp Alfredo Pasta"
                "Mushroom Risotto",
                "Greek Salad",
                "Lentil Soup",
                "Stuffed Peppers",
                ]
recipe_image_locations = [
    "spaghetti.jpg",
    "Pancakes.jpg",
    "Chicken.jpg",
    "Chocolate.jpg",
    "Caesar.jpg",
    "Garlic.jpg",
    "potatoes.jpg",
    "Omelette.jpg",
    "grilled.jpg",
    "beef.jpg",
    "Fish_Tacos.jpeg",
    "stir_fry.jpeg",
    "shrimp_alfredo.jpeg",
    "risotto.jpeg",
    "greek_salad.jpeg",
    "lentil_soup.jpeg",
    "stuffed_peppers.jpeg",
]

recipe_image_map = dict(zip(
    [name.lower() for name in recipe_names],  # lowercase for case-insensitive matching
    recipe_image_locations
))

import difflib


def find_best_image(recipe_name: str) -> str:
    """
    Returns the best matching image for a recipe name.
    Matches on any word in the name or uses fuzzy matching.
    """
    name_lower = recipe_name.lower()
    words = name_lower.split()

    # 1️ Check if any word matches a seed recipe
    for seed_name in recipe_image_map.keys():
        seed_words = seed_name.split()
        if any(word in seed_words for word in words):
            return f"/media/recipes/{recipe_image_map[seed_name]}"

    # 2️ Fuzzy match as a fallback
    close_matches = difflib.get_close_matches(name_lower, recipe_image_map.keys(), n=1, cutoff=0.5)
    if close_matches:
        best_match = close_matches[0]
        return f"/media/recipes/{recipe_image_map[best_match]}"

    # 3️ Default image
    return "/media/recipes/default.png"
