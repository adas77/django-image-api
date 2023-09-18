from collections import OrderedDict

from django.conf import settings
from django.utils import timezone
from rest_framework.serializers import ModelSerializer

from .models import Image, Link, UploadImage


class UploadImageSerializer(ModelSerializer):
    class Meta:
        model = UploadImage
        fields = ("resize",)

    def to_representation(self, instance):
        result = super(UploadImageSerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None]
        )


class LinkSerializer(ModelSerializer):
    mediafile = UploadImageSerializer(required=True)

    class Meta:
        model = Link
        fields = ("url", "expires", "mediafile")

    def to_representation(self, instance):
        result = super(LinkSerializer, self).to_representation(instance)

        if instance.expires and instance.expires < timezone.now():
            return {}

        host = f"http://{settings.HOST}:{settings.PORT}{settings.MEDIA_URL[:-1]}"
        result["url"] = f'{host}/{result["url"]}'
        result["resize"] = result.pop("mediafile", None).pop("resize", None)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None]
        )


class ImageSerializer(ModelSerializer):
    links = LinkSerializer(source="link_set", many=True)

    class Meta:
        model = Image
        fields = ("name", "uploaded_on", "links")

    def to_representation(self, instance):
        result = super(ImageSerializer, self).to_representation(instance)
        return OrderedDict(
            [(key, result[key]) for key in result if result[key] is not None]
        )
