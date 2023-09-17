import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image as PIL_Image


class Tier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    thumbnail_size = models.PositiveIntegerField(default=200)
    thumbnail_size_bigger = models.PositiveIntegerField(null=True)
    presence_of_link_to_og_file = models.BooleanField(default=False)
    ability_to_create_exp_link = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class User(AbstractUser):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.username}:{self.tier.name}'


class Image(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.creator}-{self.name}:{self.uploaded_on}'


class UploadImage(models.Model):
    def upload_to(instance, filename):
        _, extension = os.path.splitext(filename)
        uid = uuid.uuid4()
        return f'{uid}{extension}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = PIL_Image.open(self.mediafile)
        if self.resize:
            width, height = img.size
            target_height = self.resize
            w_coefficient = height / self.resize
            target_width = width / w_coefficient
            img = img.resize((int(target_width), int(
                target_height)), PIL_Image.ANTIALIAS)

        img.save(self.mediafile.path, quality=100)
        img.close()
        self.mediafile.close()

    mediafile = models.FileField(upload_to=upload_to, unique=True)
    resize = models.PositiveIntegerField(null=True, default=None)


class Link(models.Model):
    url = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    expires = models.DateTimeField(null=True, default=None)

    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    mediafile = models.ForeignKey(UploadImage, on_delete=models.CASCADE)

    def __str__(self):
        return f'mediafile:{self.mediafile.mediafile}\nurl:{self.url}\nexpires:{self.expires}'
