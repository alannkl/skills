from django.contrib.auth import get_user_model

User = get_user_model()


def deactivate(user_id: int) -> None:
    User.objects.filter(pk=user_id).update(is_active=False)
