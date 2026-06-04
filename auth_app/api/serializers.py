from rest_framework import serializers
from auth_app.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """Serialisiert die Registrierung von Benutzern, einschließlich des 'type'-Felds."""

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        """Prüft, ob beide Passwörter übereinstimmen."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({"password": "Die Passwörter stimmen nicht überein."})
        return attrs
    
    def create(self, validated_data):
        """Erstellt einen neuen User mit gehashtem Passwort."""
        validated_data.pop('repeated_password')
        user = CustomUser.objects.create_user(**validated_data)
        return user