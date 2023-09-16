from datetime import timedelta

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone

from .models import Image, User
from .serializers import ImageSerializer


class Uploader():
    ALLOWED_EXTENSIONS = ['image/jpeg', 'image/png']

    @staticmethod
    def validate_extensions(content_type: str):
        if content_type not in Uploader.ALLOWED_EXTENSIONS:
            raise Exception(
                f'Allowed extensions: {", ".join(Uploader.ALLOWED_EXTENSIONS)}')

    @staticmethod
    def handle_save_for_particular_tier(user: User, uploaded_file: InMemoryUploadedFile,
                                        link_exp_seconds: int | None):
        tier = user.tier
        image = Image(creator=user, name=uploaded_file.name)
        image.save()

        def create_link_helper(describtion: str, resize: int = None, expires=None):
            image.link_set.create(
                mediafile=uploaded_file, resize=resize, expires=expires)

        create_link_helper(
            describtion=f'{tier.thumbnail_size} pixel height shortcut',
            resize=tier.thumbnail_size)

        if tier.thumbnail_size_bigger:
            create_link_helper(
                describtion=f'{tier.thumbnail_size_bigger} pixel height shortcut',
                resize=tier.thumbnail_size_bigger)

        if tier.presence_of_link_to_og_file:
            create_link_helper(describtion='Original size image')

        if tier.ability_to_create_exp_link and link_exp_seconds is not None:
            datetime_value = timezone.now() + timedelta(seconds=link_exp_seconds)
            create_link_helper(
                describtion=f'Original size image with {link_exp_seconds}s fetch lifetime',
                expires=datetime_value)

        serializer = ImageSerializer(instance=image)
        image = serializer.data
        print(image)
        return image
