from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing", blank=True, related_name="watching_users")

    def __str__(self):
        return self.username


class Listing(models.Model):
    CATEGORY_CHOICES = [
        ("fashion", "Fashion"),
        ("toys", "Toys"),
        ("electronics", "Electronics"),
        ("home", "Home"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)  
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    closed = models.BooleanField(default=False)
    maker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def highest_bid_obj(self):
        return self.bids.order_by("-amount").first()

    @property
    def highest_bid(self):
        highest = self.highest_bid_obj()
        return highest.amount if highest else self.starting_bid



class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"${self.amount} by {self.user} on {self.listing}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.listing}"
