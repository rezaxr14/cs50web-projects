from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count


from .models import User, Listing, Comment, Bid 
from .forms import CreateListingForm


def index(request):
    
    return render(request, "auctions/index.html",{
        "listings":Listing.objects.all(),
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.maker = request.user
            listing.save()
            return redirect("index")
    form = CreateListingForm()
    return render(request, "auctions/create.html", {
        "form":form
    })


def listings(request, listing):
    listing_obj = get_object_or_404(Listing, pk=listing)

    if request.method == "POST":
        if request.user.is_authenticated:
            if "add" in request.POST:
                request.user.watchlist.add(listing_obj)
            elif "remove" in request.POST:
                request.user.watchlist.remove(listing_obj)
            elif "close" in request.POST and request.user == listing_obj.maker:
                listing_obj.closed = True
                listing_obj.save()
            elif "bid_amount" in request.POST and not listing_obj.closed:
                try:
                    print("Raw bid amount:", request.POST.get("bid_amount"))
                    bid_amount = float(request.POST.get("bid_amount"))
                    current_highest = listing_obj.highest_bid

                    if bid_amount > current_highest:
                        Bid.objects.create(
                            user=request.user,
                            amount=bid_amount,
                            listing=listing_obj
                        )
                    else:
                        messages.error(request, f"Your bid must be higher than the current highest bid (${current_highest}).")
                except (ValueError, TypeError):
                    messages.error(request, "Invalid bid amount.")
            elif "content" in request.POST:
                content = request.POST.get("content").strip()
                try:
                    Comment.objects.create(
                        user=request.user,
                        content=content,
                        listing=listing_obj,
                    )
                except (ValueError,TypeError):
                    messages.error(request, "Invalid Comment Text.")
            return redirect("listing", listing=listing_obj.id)
    return render(request, "auctions/listings.html", {
        "listing": listing_obj,
    })

@login_required
def watchlist(request):
    items = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html",{
        "items": items
    })


def categories_view(request):
    categories = Listing.objects.values_list('category', flat=True).distinct()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })
    
def category_view(request,category):
    items = Listing.objects.filter(category=category)
    return render(request, "auctions/category.html", {
        "items": items
    })
    
     