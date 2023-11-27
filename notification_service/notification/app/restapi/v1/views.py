from drf_yasg.utils import swagger_auto_schema
from notify.models import NotificationTypes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from restapi.utils import create_notification_log
from restapi.v1.serializers.base import ReceiverBaseSerializer
from restapi.v1.serializers.bookmarks_serializer import BookmarksSerializer
from restapi.v1.serializers.like_serializer import LikesSerializer
from restapi.v1.serializers.movie_serializer import MovieSerializer


class NotificationPostMixin:

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.data

            try:
                guid = create_notification_log(self.log_type, data).guid
            except Exception as e:
                # т.к. дергать эту ручку будет наш же сервис, мы можем выкидывать ошибку наружу.
                error = {'error': str(e)}
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            response = {'success': True,
                        'notification_guid': guid}
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikesView(NotificationPostMixin, APIView):
    serializer_class = LikesSerializer
    log_type = NotificationTypes.like

    @swagger_auto_schema(
        operation_description='Лайки.',
        request_body=LikesSerializer
    )
    def post(self, request):
        return super().post(request)


class WelcomeView(NotificationPostMixin, APIView):
    serializer_class = ReceiverBaseSerializer
    log_type = NotificationTypes.welcome

    @swagger_auto_schema(
        operation_description='Приветственное письмо.',
        request_body=ReceiverBaseSerializer
    )
    def post(self, request):
        return super().post(request)


class BirthdayView(NotificationPostMixin, APIView):
    serializer_class = ReceiverBaseSerializer
    log_type = NotificationTypes.birthday

    @swagger_auto_schema(
        operation_description='Письмо поздравление',
        request_body=ReceiverBaseSerializer
    )
    def post(self, request):
        return super().post(request)


class BookmarksView(APIView):
    serializer_class = BookmarksSerializer

    @swagger_auto_schema(
        operation_description="Закладки",
        request_body=BookmarksSerializer
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewMovieView(NotificationPostMixin, APIView):
    serializer_class = MovieSerializer
    log_type = NotificationTypes.new_movie

    @swagger_auto_schema(
        operation_description='Новый фильм',
        request_body=MovieSerializer
    )
    def post(self, request):
        return super().post(request)
