from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    # Add a simple helper method
    def total_likes(self):
        return self.likes.count()


class Following(models.Model):
    # The user who is doing the following
    user_following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relations')

    # The user who is being followed
    user_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relations')

    class Meta:
        unique_together = ('user_following', 'user_followed')
