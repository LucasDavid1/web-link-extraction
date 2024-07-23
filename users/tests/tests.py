import pytest

from users.services import get_user_by_id 
from users.models import User


@pytest.mark.django_db
class TestGetUserById:

    @pytest.fixture
    def create_user(self):
        def _create_user(username="testuser", password="12345"):
            return User.objects.create_user(username=username, password=password)
        return _create_user

    def test_get_existing_user(self, create_user):
        user = create_user()
        retrieved_user = get_user_by_id(user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.username == user.username

    def test_get_non_existent_user(self):
        non_existent_id = 9999
        retrieved_user = get_user_by_id(non_existent_id)
        assert retrieved_user is None

    def test_get_user_with_invalid_id_type(self):
        invalid_id = "not_an_integer"
        with pytest.raises(ValueError):
            get_user_by_id(invalid_id)

    @pytest.mark.parametrize("user_id", [-1, 0])
    def test_get_user_with_invalid_id_value(self, user_id):
        retrieved_user = get_user_by_id(user_id)
        assert retrieved_user is None

    def test_get_multiple_users(self, create_user):
        user1 = create_user(username="user1")
        user2 = create_user(username="user2")
        
        retrieved_user1 = get_user_by_id(user1.id)
        retrieved_user2 = get_user_by_id(user2.id)
        
        assert retrieved_user1.id == user1.id
        assert retrieved_user2.id == user2.id
        assert retrieved_user1 != retrieved_user2
