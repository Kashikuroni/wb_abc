from src.auth.models import User
from src.auth.schemas import UserRead


def user_to_read(user: User) -> UserRead:
    return UserRead.model_validate(user)
