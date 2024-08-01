import pytest
from app.users.dao import UsersDAO


@pytest.mark.parametrize("email, exists", [
    ("test@test.com", True),
    ("artem@example.com", True),
    ("...", False),
])
async def test_find_one_user_or_none(email, exists):
    user = await UsersDAO.find_one_or_none(email=email)
    
    if exists:
        assert user
        assert user["email"] == email
    else:
        assert not user
    
    