from rest_framework import serializers
from auth_app.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """Serializes user registration, including the 'type' field."""

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        """Checks that both passwords match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        """Creates a new user with a hashed password."""
        validated_data.pop('repeated_password')
        user = CustomUser.objects.create_user(**validated_data)
        return user
