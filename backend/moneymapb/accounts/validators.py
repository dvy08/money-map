import re 
from rest_framework import serializers

def validate_password_strength(password):
    if not re.search(r"[A-Z]", password):
        raise serializers.ValidationError(
            "Password must contain an uppercase letter."
        )
    
    if not re.search(r"\d", password):
        raise serializers.ValidationError(
            "Password must contain a number"
        )
    return password