
from django.conf import settings
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Image
from .serializers import ImageSerializer
from .utils import Uploader


class ImageAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        # TODO: Also filter expired here?
        images = Image.objects.filter(creator=request.user.pk)
        serializer = ImageSerializer(instance=images, many=True)
        return Response(serializer.data)

    def post(self, request):
        uploaded_file = request.FILES.get(settings.MEDIA_UPLOAD_KEY, None)
        if uploaded_file is None:
            return Response(
                f'Provide image to form-data with key: {settings.MEDIA_UPLOAD_KEY}',
                status=status.HTTP_400_BAD_REQUEST
            )
        content_type = uploaded_file.content_type

        try:
            Uploader.validate_extensions(content_type)
        except Exception as e:
            return Response(
                str(e),
                status=status.HTTP_400_BAD_REQUEST
            )

        link_exp_seconds = request.GET.get('exp', None)
        try:
            link_exp_seconds = int(link_exp_seconds)
        except:
            link_exp_seconds = None

        if link_exp_seconds is not None and (link_exp_seconds < 300 or link_exp_seconds >= 30_000):
            return Response(
                f'{link_exp_seconds}s not between {300}s and {30_000}s',
                status=status.HTTP_400_BAD_REQUEST
            )

        data = Uploader.handle_save_for_particular_tier(
            request.user, uploaded_file, link_exp_seconds)

        return Response(
            data,
            status=status.HTTP_201_CREATED
        )
