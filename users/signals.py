# users/signals.py

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import CustomUser
# from .utils import send_confirmation_email
# import jwt
# from django.conf import settings
#
# @receiver(post_save, sender=CustomUser)
# def send_welcome_email(sender, instance, created, **kwargs):
#     if created:
#         # Generar un token de confirmación (este es un ejemplo, personaliza según tu lógica)
#         token = jwt.encode({'user_id': instance.id}, settings.SECRET_KEY, algorithm='HS256')
#         send_confirmation_email(instance, token)
