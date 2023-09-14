from django.db import models
import uuid
from django.contrib.auth.models import User


class Tier(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    name = models.CharField(max_length=100, unique=True)
    thumbnail_size = models.PositiveIntegerField(default=200)
    thumbnail_size_bigger = models.PositiveIntegerField(null=True)
    presence_of_link_to_og_file = models.BooleanField(default=False)
    ability_to_create_exp_link = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Account(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tier = models.OneToOneField(Tier, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username}:{self.tier.name}'


class Image(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
