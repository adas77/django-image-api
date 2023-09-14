from django.contrib import admin

from .models import Image, User, Tier

admin.site.register(Image)
admin.site.register(User)
admin.site.register(Tier)
