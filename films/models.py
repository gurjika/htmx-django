from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.functions import Lower

class User(AbstractUser):
    pass


class Films(models.Model):
    name = models.CharField(max_length=128, unique=True)
    users = models.ManyToManyField(User, related_name='films', through='UserFilms')
    image = models.ImageField(upload_to='film_images/', default='default_poster.jpg')

    class Meta:
        ordering = [Lower('name')]

    def __str__(self) -> str:
        return self.name
    
class UserFilms(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    film = models.ForeignKey(Films, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()
    
    class Meta:
        ordering = ['order']