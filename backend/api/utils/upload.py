from ..serializers import ImageSerializer
from ..models import User


class Uploader():
    ALLOWED_EXTENSIONS = ['image/jpeg', 'image/png']

    @staticmethod
    def validate_extensions(content_type: str):
        if content_type not in Uploader.ALLOWED_EXTENSIONS:
            raise Exception(
                f"""Invalid extention: {content_type}.
                Possible only: {', '.join(Uploader.ALLOWED_EXTENSIONS)}""")

    @staticmethod
    def handle_save_for_particular_tier(user: User, serializer: ImageSerializer):
        # FIXME: c overriding a and b
        tier = user.tier
        tier.thumbnail_size

        a = serializer.save(creator=user, resize=tier.thumbnail_size)
        if tier.thumbnail_size_bigger:
            b = serializer.save(
                creator=user, resize=tier.thumbnail_size_bigger)

        if tier.presence_of_link_to_og_file:
            c = serializer.save(creator=user)

        if tier.ability_to_create_exp_link:
            Uploader.__create_exp_link(user, serializer)

        return "f"

    @staticmethod
    def __create_exp_link(user: User, serializer: ImageSerializer):
        # TODO: create_exp_link
        pass
