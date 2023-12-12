from rest_framework import serializers

from profiles.models import Person, FilmReview, Favorite, Bookmark


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        read_only_fields = ('id',)
        exclude = ('password',)


class ProfileCreateOrUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = ['email', 'first_name', 'last_name', 'date_of_birth', 'gender', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def _set_user_password(self, user, password):
        if password is not None:
            user.set_password(password)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Person(**validated_data)
        self._set_user_password(user, password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        self._set_user_password(instance, password)
        instance.save()
        return instance


class PersonResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'
        read_only_fields = ['id']


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ['id']

    def create(self, validated_data):
        favorite_movie = Favorite(**validated_data)
        favorite_movie.save()
        return favorite_movie


class BookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookmark
        fields = '__all__'
        read_only_fields = ['id']
