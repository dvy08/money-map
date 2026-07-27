from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .validators import validate_password_strength

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[
            validate_password,
            validate_password_strength
        ]
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
            'income_type',
            'tax_allotment_needed',
            'currency'
        ]
        
    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data
        )

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'income_type',
            'tax_allotment_needed',
            'currency',
            'created_at',
        ]