from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


User = get_user_model()

def create_user(**validated_data):
    password = validated_data.pop('password')
    password2 = validated_data.pop('password2', None)

    if password != password2:
        raise ValidationError({'password': "Passwords don't match."})

    try:
        validate_password(password)
    except ValidationError as e:
        raise ValidationError({'password': e.messages})

    user = User(**validated_data)
    user.set_password(password)
    user.save()
    return user
