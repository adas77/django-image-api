from .serializers import ImageSerializer
from .models import User, Image
from django.utils import timezone
from datetime import timedelta
from django.db.models import F


class Uploader():
    ALLOWED_EXTENSIONS = ['image/jpeg', 'image/png']

    @staticmethod
    def validate_extensions(content_type: str):
        if content_type not in Uploader.ALLOWED_EXTENSIONS:
            raise Exception(
                f'Allowed extensions: {", ".join(Uploader.ALLOWED_EXTENSIONS)}')

    @staticmethod
    def handle_save_for_particular_tier(user: User, serializer: ImageSerializer):
        tier = user.tier
        data = serializer.validated_data
        response = []

        def create_image_helper(describtion: str, resize: int = None, expires=None):
            serializer = ImageSerializer(data=data)
            if serializer.is_valid():
                serializer.save(creator=user, resize=resize,
                                expires=expires)
                response_data = serializer.data
                response_data['description'] = describtion
                response.append(response_data)

        create_image_helper(
            describtion=f'{tier.thumbnail_size} pixel height shortcut',
            resize=tier.thumbnail_size)
        if tier.thumbnail_size_bigger:
            create_image_helper(
                describtion=f'{tier.thumbnail_size_bigger} pixel height shortcut',
                resize=tier.thumbnail_size_bigger)

        if tier.presence_of_link_to_og_file:
            create_image_helper(describtion='Original size image')

        # FIXME:
        MOCK_LINK_EXP = 333
        link_exp_seconds = MOCK_LINK_EXP
        if tier.ability_to_create_exp_link:
            datetime_value = timezone.now() + timedelta(seconds=link_exp_seconds)
            create_image_helper(
                describtion=f'Original size image with {link_exp_seconds}s fetch lifetime',
                expires=datetime_value)

        return response


class Downloader():
    @staticmethod
    def filter_images(creator: User = None):
        images = Image.objects.filter(uploaded_on__le=F('expires'))
        if creator:
            images = images.filter(creator=creator)

        serializer = ImageSerializer(data=images, many=True)
        if serializer.is_valid():
            return serializer.data
        return serializer.data
