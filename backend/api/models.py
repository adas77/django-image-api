import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
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
    def upload_to(instance, filename):
        _, extension = os.path.splitext(filename)
        # creator_uid = instance.creator.uid
        file_uid = uuid.uuid4()
        # FIXME: user/image or /image
        return f'{file_uid}{extension}'
        # return f'{creator_uid}/{file_uid}{extension}'

    def validate_link_exp(value):
        MIN = 300
        MAX = 30_000
        if value < MIN or value > MAX:
            raise ValidationError(f'{value}s not between {MIN}s and {MAX}s')

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    resize = models.PositiveIntegerField(null=True, default=None)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(null=True)
    file = models.FileField(upload_to=upload_to)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = PIL_Image.open(self.file)
        if self.resize:
            width, height = img.size
            target_width = self.resize
            h_coefficient = width/self.resize
            target_height = height/h_coefficient
            img = img.resize((int(target_width), int(
                target_height)), PIL_Image.ANTIALIAS)
        img.save(self.file.path, quality=100)
        img.close()
        self.file.close()

    def __str__(self):
        return f'{self.resize}'
