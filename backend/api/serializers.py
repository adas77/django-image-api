from collections import OrderedDict

from rest_framework.serializers import ModelSerializer

from .models import Image


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ('file', 'uploaded_on', 'expires')

    def to_representation(self, instance):
        result = super(ImageSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])
