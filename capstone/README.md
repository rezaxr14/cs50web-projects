# 🍳 WhatToCook — Intelligent Recipe Assistant

**Author:** *Reza Nadmi*

**🎥 Project Demo:** [![WhatToCook — Intelligent Recipe Assistant](https://img.youtube.com/vi/bEDYRpNFxOQ/0.jpg)](https://youtu.be/bEDYRpNFxOQ)

**🖼️ Screenshots:**

* *Screenshot 1: Homepage* ![Homepage](/media/readme_images/homepage.png)
* *Screenshot 2: AI Recipe Suggestions*![AI Recipe Suggestions](/media/readme_images/AI%20Recipe%20Suggestions.png)
* *Screenshot 3: Pantry Management*![Homepage](/media/readme_images/Pantry%20Management.png)
* *Screenshot 4: Recipe Details Page*![Homepage](/media/readme_images/Recipe%20Details%20Page.png)

---

## 🧩 Distinctiveness and Complexity

**WhatToCook** is a full-stack intelligent recipe recommendation web application built with **Django**, **JavaScript (fetch + dynamic DOM rendering)**, and a **PostgreSQL** database, fully containerized using **Docker**.

It goes far beyond standard CRUD web apps or course examples like CS50W’s Commerce or Network projects. Instead of serving static content or simple transactions, this app integrates a **live AI suggestion engine** that dynamically generates personalized recipe ideas based on the user’s pantry ingredients, stored in the database and cached for later use.

Distinct features include:

* 🧠 **AI-driven recipe generation** using a connected LLM API (Llama model hosted locally via LM Studio).
* ⚙️ **Dynamic caching of AI responses** (with a database hash system ensuring users see the same results upon return, avoiding redundant API calls).
* 🥕 **User pantry system** — users can add and remove ingredients, and AI suggestions are built dynamically from these ingredients.
* 🧾 **Interactive front-end** — uses async JavaScript fetch requests, JSON APIs, and graceful fallback/retry for failed responses.
* 💾 **Persistent backend** with PostgreSQL, connected via Docker Compose.
* 📱 **Responsive layout** built using Tailwind CSS, making the app mobile-friendly and modern.
* 🔁 **Temporary AI cache database** and automatic cleanup of expired entries through Django signals.
* ⚡ **Pagination, detailed views, and API modularity** with Django REST Framework.

The combination of **AI-based JSON parsing, caching, user interactivity, and live Django data persistence** results in a significantly more complex and technically deep project than other examples like social networks or e-commerce.



## 🧩 Project Structure & File Descriptions

### Root Directory

* **Dockerfile** – Defines how the Django app container is built (Python setup, dependencies, commands).
* **docker-compose.yml** – Orchestrates multiple containers (Django app, Redis, Celery worker).
* **manage.py** – Django’s command-line utility for running the server, migrations, etc.
* **requirements.txt** – Lists all Python dependencies needed for the project.
* **README.md** – Documentation file describing the project setup and usage.
* **.env** – Stores environment variables (API keys, model names, secrets).

---

### 📦 WhatToCook (Main Django Project)

* ****init**.py** – Marks this directory as a Python package.
* **asgi.py** – ASGI configuration for async web server deployment.
* **wsgi.py** – WSGI configuration for production servers (like Gunicorn).
* **urls.py** – Main URL router for the entire Django project.
* **settings.py** – Core configuration file (databases, installed apps, static files, Celery setup).
* **celery.py** – Configures Celery to work with Django and Redis for background tasks.

---

### 🍲 GetFood (Main App inside WhatToCook)

* **admin.py** – Registers models for Django’s admin interface.
* **apps.py** – Configuration for the GetFood Django app.
* **models.py** – Defines database models like Recipe, Ingredient, Pantry, etc.
* **serializers.py** – Converts model instances to JSON for API responses.
* **urls.py** – App-specific URL routes (e.g., `/recipes/`, `/ai_suggestions/`).
* **views.py** – Handles HTTP requests and responses (main logic for each page).
* **tasks.py** – Celery background tasks (AI API calls, caching, etc.).
* **utils.py** – Helper functions (e.g., image processing, JSON parsing).
* **tests.py** – Unit and integration tests for app functionality.

---

### 🧠 Templates (Frontend HTML Files)

Located at: `GetFood/templates/GetFood/`

* **layout.html** – Base template containing the navbar, styles, and layout.
* **index.html** – Homepage showing recipe categories and featured items.
* **login.html / signup.html** – Authentication pages with styled form borders.
* **pantry.html** – Page where users can manage ingredients they own.
* **can_cook.html** – Displays recipes the user can cook based on pantry items.
* **ai_suggestions.html** – Shows AI-generated recipe ideas fetched asynchronously.
* **ai_recipe_detail.html / recipe_detail.html** – Detailed recipe view (manual or AI-generated).

---

### 🧰 Management Commands

Located at: `GetFood/management/commands/`

* **seed_data.py** – Custom Django command to prefill the database with sample recipes and ingredients.

---

### 🗂 Media Folder

* **recipes/** – Stores uploaded or AI-generated recipe images.
* **seed_images/** – Preloaded example images for seeding data.
* **readme_images/** – Screenshots used in documentation.

---

### 🧪 Tests

* **tests/** – Contains organized test cases for models, APIs, and AI logic.

---

## ⚙️ How to Run the Application

### 🐳 Run with Docker Compose

1. **Clone the repository:**

   ```bash
   git clone https://github.com/rezaxr14/whattocook.git
   cd whattocook
   ```

2. **Build and start containers:**

   ```bash
   docker compose up -d
   ```
3. **Migrate the databases:**

   ```
    docker compose run web python manage.py migrate
   ```

4. **Seed initial data:**

   ```bash
   docker compose run web python manage.py seed_data
   ```

5. **Access the app:**
   Visit [http://localhost:9000](http://localhost:9000)

---

## 🧠 AI Functionality

When users visit the AI Suggestions page, the system:

1. Reads the user’s pantry ingredients.
2. Generates a hash from the ingredient list to check the cache.
3. If cached data exists (within 24h), returns it immediately.
4. Otherwise, it sends the ingredient list to a **local Llama model** hosted via LM Studio.
5. The AI returns structured JSON with `name`, `description`, `difficulty`, `cuisine`, and `image_hint`.
6. The response is parsed, cleaned, validated, and images are mapped automatically.
7. Recipes are displayed beautifully on the frontend, with async loading and fallback messages.

---

## 📱 Mobile Responsiveness

The entire interface is responsive using Tailwind CSS. Layouts such as AI Suggestions, Recipe Details, and Pantry Management automatically adjust to screen sizes. Buttons are large and touch-friendly for mobile devices.

---

## 🧹 Technical Polish

* **Automatic Cache Cleanup:** A Django signal removes expired AI cache entries older than 24 hours.
* **Graceful Frontend Recovery:** If an API fetch fails, the page retries automatically after a few seconds.
* **Pagination:** Index page shows 6 recipes per page with a clean, centered navigation.
* **Improved User Forms:** Login and Signup forms have visible input borders and mobile-friendly spacing.
* **Unit Tests:** JSON parsing and AI API responses are verified using Django’s test suite.

---

## 🧪 Running Unit Tests

```bash
docker compose run web python manage.py test
```

This runs all test cases inside the isolated web container, ensuring deterministic results regardless of the host OS.

---


## 🧰 Requirements

All dependencies are listed in `requirements.txt`. To install locally (outside Docker):

```bash
pip install -r requirements.txt
```

---

## 💡 Conclusion

**WhatToCook** is not just another recipe website — it’s an intelligent, responsive, and cache-aware AI assistant that dynamically generates personalized meals based on real user input. Built with Django, PostgreSQL, and modern frontend practices, it demonstrates deep understanding of backend architecture, API design, and asynchronous UI updates.

*This project showcases full-stack integration, AI JSON handling, and containerized deployment — far exceeding the complexity of standard CRUD or social web apps.*
