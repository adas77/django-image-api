from django.contrib import admin

from .models import Image, Link, Tier, UploadImage, User

admin.site.register(User)

admin.site.register(Tier)

admin.site.register(Image)
admin.site.register(Link)
admin.site.register(UploadImage)
