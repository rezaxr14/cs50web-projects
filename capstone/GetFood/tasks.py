import json
import re
import requests
import hashlib
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django.conf import settings

from .models import AISuggestionCache
from .utils import find_best_image

LMSTUDIO_URL = getattr(settings, "LMSTUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions")
MODEL_NAME = getattr(settings, "MODEL_NAME", "llama-3.2-3b-instruct")


@shared_task(bind=True)
def generate_ai_suggestions_task(self, ingredients_list, ingredients_hash):
    """
    Celery async task: generate AI-based recipe ideas from ingredients.
    """
    prompt = (
        f"You are a creative chef. Based on these ingredients: {', '.join(ingredients_list)}, "
        "suggest 5 realistic dishes. "
        "Return ONLY valid JSON with key 'dishes', where each item has: "
        "name, short_description, cuisine, difficulty, image_hint."
    )

    try:
        resp = requests.post(
            LMSTUDIO_URL,
            headers={"Content-Type": "application/json"},
            json={"model": MODEL_NAME, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7},
            timeout=180,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        # Clean markdown fences if any
        content = content.replace("```json", "").replace("```", "").strip()

        recipes = []
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "dishes" in parsed:
                recipes = parsed["dishes"]
            elif isinstance(parsed, list):
                recipes = parsed
        except json.JSONDecodeError:
            matches = re.findall(r"\{.*?\}", content)
            for m in matches:
                try:
                    obj = json.loads(m)
                    if "name" in obj:
                        recipes.append(obj)
                except Exception:
                    continue

        for r in recipes:
            r["image"] = find_best_image(r.get("name", "dish"))

        AISuggestionCache.objects.create(
            ingredients_hash=ingredients_hash,
            ai_response=recipes,
            created_at=timezone.now()
        )

        return {"status": "ok", "count": len(recipes)}

    except Exception as exc:
        AISuggestionCache.objects.create(
            ingredients_hash=ingredients_hash,
            ai_response={"error": str(exc)},
            created_at=timezone.now()
        )
        return {"status": "error", "error": str(exc)}
