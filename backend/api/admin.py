from django.contrib import admin

from .models import Image, Link, User, Tier

admin.site.register(Image)
admin.site.register(User)
admin.site.register(Tier)
admin.site.register(Link)
