from collections import OrderedDict

from rest_framework.serializers import ModelSerializer

from .models import Image, Link


class LinkSerializer(ModelSerializer):
    class Meta:
        model = Link
        fields = ('url', 'resize', 'expires')

    def to_representation(self, instance):
        # FIXME: delete mock
        MOCK_HOST = 'http://127.0.0.1:8000/media/'
        host = MOCK_HOST
        result = super(LinkSerializer, self).to_representation(instance)
        result['url'] = host+result['url']
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class ImageSerializer(ModelSerializer):
    links = LinkSerializer(source='link_set', many=True)

    class Meta:
        model = Image
        fields = ('name', 'uploaded_on', 'links')

    def to_representation(self, instance):
        result = super(ImageSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])
