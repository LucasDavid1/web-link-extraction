from users.models import User


def get_user_by_id(user_id: int):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

