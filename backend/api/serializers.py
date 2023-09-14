from rest_framework.serializers import ModelSerializer, FileField
from .models import Image


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        exclude = ('pkid',)


class UploadSerializer(ModelSerializer):
    file_uploaded = FileField()

    class Meta:
        fields = ['file_uploaded']
