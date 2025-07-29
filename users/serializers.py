from rest_framework import serializers
from users.models import User


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'full_name', 'email', 'address', 'is_staff', 'is_superuser', 'created_at']

class UserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'full_name', 'email', 'address', 'password', 'is_staff', 'is_superuser']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'default': False},
            'is_superuser': {'default': False},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'password', 'full_name', 'is_superuser']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        password = validated_data.get('password')
        return user

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'full_name', 'email', 'address', 'is_superuser']
        extra_kwargs = {
            'phone': {'read_only': True},
            'id': {'read_only': True}
        }