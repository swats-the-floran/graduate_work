from profiles_service.profiles.api.v1.serializers import ProfileCreateOrUpdateSerializer


class PersonService:
    @staticmethod
    def create_user(data):
        serializer = ProfileCreateOrUpdateSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            return serializer.save()

    @staticmethod
    def update_user(user, data):
        serializer = ProfileCreateOrUpdateSerializer(user, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            return serializer.save()
