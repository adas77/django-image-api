from django.contrib import admin

from .models import Image, Account, Tier

admin.site.register(Image)
admin.site.register(Account)
admin.site.register(Tier)
