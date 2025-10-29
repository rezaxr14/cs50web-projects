from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
import json

from django.http import JsonResponse

from .models import User, Post, Following


def index(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            new_post = json.loads(request.body).get('newPost')
            Post.objects.create(content=new_post, author=request.user)
    return render(request, "network/index.html")


def posts(request):
    # Get all posts, ordered by the most recent
    all_posts = Post.objects.all().order_by('-date_posted')

    # Paginate the posts, with 10 posts per page
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Serialize the posts on the current page
    posts_on_page = []
    for post in page_obj.object_list:
        posts_on_page.append({
            "id": post.id,
            "author": post.author.username,
            "content": post.content,
            "date_posted": post.date_posted.strftime("%b %d %Y, %I:%M %p"),
            "likes": post.total_likes(),
            "is_liked_by_user": request.user in post.likes.all() if request.user.is_authenticated else False
        })

    # Return the posts and pagination info as JSON
    return JsonResponse({
        "posts": posts_on_page,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
        "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
        "num_pages": paginator.num_pages
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def user(request, user: str):
    # Get the user object for the profile being viewed
    profile_user = get_object_or_404(User, username=user)

    is_following = False
    if request.user.is_authenticated:
        # Check if a "Following" relationship exists from the logged-in user to the profile user
        is_following = Following.objects.filter(
            user_following=request.user,
            user_followed=profile_user
        ).exists()

    # Pass the result of the check into the context
    context = {
        "model": profile_user,
        "current_user": request.user,
        "is_following": is_following  # Pass the boolean to the template
    }

    return render(request, "network/user.html", context)


@login_required
def toggle_follow(request, username: str):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        target_user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User not found")

    if request.user == target_user:
        return JsonResponse({"error": "Cannot follow yourself"}, status=400)

    # Toggle logic
    follow_obj, created = Following.objects.get_or_create(
        user_following=request.user,
        user_followed=target_user
    )

    if created:
        # If the row was just created, the user is now following.
        is_following = True
    else:
        # If the row already existed, delete it to "unfollow".
        follow_obj.delete()
        is_following = False

    new_follower_count = Following.objects.filter(user_followed=target_user).count()

    return JsonResponse({
        "is_following": is_following,
        "new_follower_count": new_follower_count
    }, status=200)


@login_required
def following(request):
    # Get the IDs of all users that the current user is following
    followed_user_ids = Following.objects.filter(user_following=request.user).values_list('user_followed_id', flat=True)

    # Get all posts from those users, ordered by most recent
    all_posts = Post.objects.filter(author__id__in=followed_user_ids).order_by('-date_posted')

    # Create a Paginator object with 10 posts per page
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass the paginated object to the template
    return render(request, "network/following.html", {
        "page_obj": page_obj
    })


def user_posts_api(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    all_posts = Post.objects.filter(author=user).order_by('-date_posted')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    posts_on_page = [
        {
            "id": post.id,
            "author": post.author.username,
            "content": post.content,
            "date_posted": post.date_posted.strftime("%b %d %Y, %I:%M %p"),
            "likes": post.total_likes(),
            "is_liked_by_user": request.user in post.likes.all() if request.user.is_authenticated else False
        }
        for post in page_obj.object_list
    ]

    return JsonResponse({
        "posts": posts_on_page,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
        "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
    })


@login_required
def edit_post(request, post_id):
    # Only allow PUT requests
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=405)

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Security Check: Ensure the user is the author of the post
    if post.author != request.user:
        return JsonResponse({"error": "You are not authorized to edit this post."}, status=403)

    # Update the post content
    data = json.loads(request.body)
    post.content = data.get("content", "")
    post.save()

    return JsonResponse({"message": "Post updated successfully."}, status=200)


@login_required
def toggle_like(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=405)

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Check if user has already liked the post
    if request.user in post.likes.all():
        # If yes, remove the like (unlike)
        post.likes.remove(request.user)
        is_liked = False
    else:
        # If no, add the like
        post.likes.add(request.user)
        is_liked = True

    return JsonResponse({
        "is_liked": is_liked,
        "like_count": post.total_likes()
    }, status=200)
