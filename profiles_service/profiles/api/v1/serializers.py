from rest_framework import serializers

from profiles_service.profiles.models import Person


class ProfileCreateOrUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['email', 'first_name', 'last_name', 'date_of_birth', 'gender', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Person(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            if field == 'password':
                instance.set_password(value)
            else:
                setattr(instance, field, value)
        instance.save()
        return instance


class PersonResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'
        read_only_fields = ['id']
