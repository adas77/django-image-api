import os
from datetime import timedelta

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone

from .models import Image, Link, UploadImage, User
from .serializers import ImageSerializer


class Uploader():
    ALLOWED_EXTENSIONS = ['.jpg', '.png']

    @staticmethod
    def validate_extensions(uploaded_file):
        _, extension = os.path.splitext(uploaded_file.name)

        if extension not in Uploader.ALLOWED_EXTENSIONS:
            raise Exception(
                f'Allowed extensions: {", ".join(Uploader.ALLOWED_EXTENSIONS)}')

    @staticmethod
    def handle_save_for_particular_tier(user: User, uploaded_file: InMemoryUploadedFile,
                                        link_exp_seconds: int | None):
        tier = user.tier
        image = Image(creator=user, name=uploaded_file.name)
        image.save()

        def create_link_helper(describtion: str, create_or_connect: InMemoryUploadedFile
                               | UploadImage = uploaded_file, resize: int = None,  expires=None):
            if type(create_or_connect) == InMemoryUploadedFile:
                mediafile = UploadImage(
                    mediafile=create_or_connect, resize=resize)
                mediafile.save()
            elif type(create_or_connect) == UploadImage:
                mediafile = create_or_connect
            else:
                raise Exception('Unreachable')
            link = Link(image=image, mediafile=mediafile, expires=expires)
            link.save()
            return mediafile

        create_link_helper(
            describtion=f'{tier.thumbnail_size} pixel height shortcut',
            resize=tier.thumbnail_size)

        if tier.thumbnail_size_bigger:
            create_link_helper(
                describtion=f'{tier.thumbnail_size_bigger} pixel height shortcut',
                resize=tier.thumbnail_size_bigger)

        og_size_file = uploaded_file
        if tier.presence_of_link_to_og_file:
            og_size_file = create_link_helper(
                describtion='Original size image')

        if tier.ability_to_create_exp_link and link_exp_seconds is not None:
            datetime_value = timezone.now() + timedelta(seconds=link_exp_seconds)
            create_link_helper(
                describtion=f'Original size image with {link_exp_seconds}s fetch lifetime',
                create_or_connect=og_size_file,
                expires=datetime_value)

        serializer = ImageSerializer(instance=image)
        image = serializer.data
        return image
