from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from rest_framework import viewsets

from .models import Ingredient, Recipe, UserPantry
from .serializers import IngredientSerializer, RecipeSerializer, UserPantrySerializer
from .utils import find_best_image

LMSTUDIO_URL = settings.LMSTUDIO_URL
MODEL_NAME = settings.MODEL_NAME


# Create your views here.
class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class UserPantryViewSet(viewsets.ModelViewSet):
    queryset = UserPantry.objects.all()
    serializer_class = UserPantrySerializer


def index(request):
    recipes = Recipe.objects.all()
    ingredients = Ingredient.objects.all()
    user_pantry = UserPantry.objects.first()

    page = request.GET.get('page', 1)  # Get page number from query params, default 1
    paginator = Paginator(recipes, 6)
    try:
        paginated_recipes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        paginated_recipes = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        paginated_recipes = paginator.page(paginator.num_pages)

    context = {
        "recipes": paginated_recipes,
        "ingredients": ingredients,
        "user_pantry": user_pantry,
        "num_pages": paginator.num_pages,
        "current_page": paginated_recipes.number,
    }
    return render(request, "GetFood/index.html", context)


@login_required
def pantry(request):
    user_pantry, _ = UserPantry.objects.get_or_create(user=request.user)
    ingredients = user_pantry.ingredients.all()
    available_ingredients = Ingredient.objects.exclude(id__in=ingredients)

    if request.method == "POST":
        if "ingredient_id" in request.POST:  # Add ingredient
            ingredient_id = request.POST.get("ingredient_id")
            if ingredient_id:
                ingredient = Ingredient.objects.get(id=ingredient_id)
                user_pantry.ingredients.add(ingredient)
                return redirect("pantry")

        elif "remove_id" in request.POST:  # Remove ingredient
            remove_id = request.POST.get("remove_id")
            if remove_id:
                ingredient = Ingredient.objects.get(id=remove_id)
                user_pantry.ingredients.remove(ingredient)
                return redirect("pantry")

    return render(request, "GetFood/pantry.html", {
        "ingredients": ingredients,
        "available_ingredients": available_ingredients,
    })


def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    instructions_list = recipe.instructions.split('\n') if recipe.instructions else []
    context = {
        "recipe": recipe,
        "instructions_list": instructions_list,
    }
    return render(request, "GetFood/recipe_detail.html", context)


def can_cook(request):
    user = request.user
    pantry_ingredients = []

    if user.is_authenticated:
        try:
            pantry = UserPantry.objects.get(user=user)
            pantry_ingredients = pantry.ingredients.all()
        except UserPantry.DoesNotExist:
            pantry_ingredients = []

    # Recipes where all ingredients are in user's pantry
    possible_recipes = []
    for recipe in Recipe.objects.all():
        recipe_ingredients = [ri.ingredient for ri in recipe.recipeingredient_set.all()]
        if all(ingredient in pantry_ingredients for ingredient in recipe_ingredients):
            possible_recipes.append(recipe)

    paginator = Paginator(possible_recipes, 6)
    page = request.GET.get('page', default=1)
    try:
        paginated_recipes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        paginated_recipes = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        paginated_recipes = paginator.page(paginator.num_pages)

    context = {
        "possible_recipes": paginated_recipes,
        "pantry_ingredients": pantry_ingredients,
        "num_pages": paginator.num_pages,
        "current_page": paginated_recipes.number,
    }
    return render(request, "GetFood/can_cook.html", context)


# Signup
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create an empty pantry for the user
            UserPantry.objects.create(user=user)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'GetFood/signup.html', {'form': form})


# Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'GetFood/login.html', {'form': form})


@login_required
def ai_suggestions(request):
    """Generate dish ideas using LM Studio model."""
    return render(request, "GetFood/ai_suggestions.html")


@login_required
def ai_recipe_detail(request, name):
    """Render base page; fetch details via AJAX later."""
    return render(request, "GetFood/ai_recipe_detail.html", {"recipe_name": name})


import hashlib, json, requests
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import AISuggestionCache, UserPantry
from .tasks import generate_ai_suggestions_task  # new celery task


@login_required
def ai_suggestions_api(request):
    """
    Return cached suggestions if available; otherwise enqueue a Celery task
    and return a task_id. Frontend will poll task status endpoint.
    """
    user = request.user
    try:
        pantry = UserPantry.objects.get(user=user)
    except UserPantry.DoesNotExist:
        return JsonResponse({"error": "Your pantry is empty! Add ingredients first."}, status=400)

    ingredients = [i.name for i in pantry.ingredients.all()]
    if not ingredients:
        return JsonResponse({"error": "Your pantry is empty! Add ingredients first."}, status=400)

    ingredients_str = ', '.join(sorted(ingredients))
    ingredients_hash = hashlib.sha256(ingredients_str.encode()).hexdigest()

    # check cache (24h)
    cache_entry = AISuggestionCache.objects.filter(
        ingredients_hash=ingredients_hash,
        created_at__gte=timezone.now() - timedelta(days=1)
    ).first()

    if cache_entry:
        # If cached response is an error dict, return error
        if isinstance(cache_entry.ai_response, dict) and cache_entry.ai_response.get("error"):
            return JsonResponse({"error": cache_entry.ai_response.get("error")}, status=500)
        return JsonResponse({"recipes": cache_entry.ai_response})

    # Not cached: enqueue background task
    task = generate_ai_suggestions_task.delay(ingredients, ingredients_hash)

    return JsonResponse({"status": "processing", "task_id": task.id})


from celery.result import AsyncResult
from django.views.decorators.http import require_GET


@require_GET
@login_required
def ai_task_status(request, task_id):
    """
    Poll this endpoint from the frontend to check if the async Celery task finished.
    When finished, read the AISuggestionCache (by ingredients_hash) and return recipes.
    We return either {"status":"pending"} or {"status":"done", "recipes": [...]}
    """
    # Check task state
    res = AsyncResult(task_id)
    if not res.ready():
        return JsonResponse({"status": "pending"})

    try:
        user = request.user
        pantry = UserPantry.objects.get(user=user)
        ingredients = [i.name for i in pantry.ingredients.all()]
        ingredients_str = ", ".join(sorted(ingredients))
        ingredients_hash = hashlib.sha256(ingredients_str.encode()).hexdigest()

        cache_entry = AISuggestionCache.objects.filter(
            ingredients_hash=ingredients_hash,
            created_at__gte=timezone.now() - timedelta(minutes=10)
        ).first()

        if cache_entry:
            return JsonResponse({"status": "done", "recipes": cache_entry.ai_response})
        else:
            return JsonResponse({"status": "done", "recipes": []})
    except UserPantry.DoesNotExist:
        return JsonResponse({"status": "done", "recipes": []})


@require_GET
@login_required
def ai_recipe_detail_api(request, recipe_name):
    try:
        prompt = (
            f"You are a master chef. Give detailed step-by-step instructions for cooking '{recipe_name}'. "
            "Return valid JSON with these keys: "
            "{'name', 'ingredients' (list of dicts with 'name', 'amount', 'unit'), "
            "'instructions' (list of dicts with 'step' and optional 'time_minutes'), 'time_minutes'}. "
            "Return ONLY raw JSON, no markdown, code fences, or comments."
        )

        response = requests.post(
            LMSTUDIO_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            },
            timeout=120,
        )

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        # Remove markdown/code fences if they exist
        if content.startswith("```"):
            content = content.strip("`").replace("json\n", "").replace("```", "").strip()

        # Sometimes the model returns extra quotes or escapes
        try:
            recipe_data = json.loads(content)
        except json.JSONDecodeError:
            # Try unescaping extra quotes
            recipe_data = json.loads(content.encode('utf-8').decode('unicode_escape'))

        # Optional: add image if you have mapping
        recipe_data["image"] = find_best_image(recipe_name)

        return JsonResponse(recipe_data)

    except Exception as e:
        return JsonResponse({"error": f"Error fetching recipe details: {e}"})
