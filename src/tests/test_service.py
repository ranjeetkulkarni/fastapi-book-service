from auth.schemas import UserCreate
from unittest.mock import Mock

def test_create_user_calls_db_add(mock_user_service, mock_session):
    # 1. Arrange: Prepare data
    user_data = {
        "username": "unittest",
        "email": "unit@test.com",
        "password": "password123",
        "first_name": "Unit",
        "last_name": "Test"
    }
    user_create_model = UserCreate(**user_data)

    # 2. Mock the behavior
    # Tell the mock: "When checking if user exists, say No (None)"
    # This ensures we enter the creation logic
    mock_user_service.user_exists = Mock(return_value=False)

    # 3. Act: Call the function
    mock_user_service.create_user(user_create_model)

    # 4. Assert: Check if DB was touched
    # "Did we try to ADD a new user to the session?"
    assert mock_session.add.called
    
    # "Did we try to COMMIT the session?"
    assert mock_session.commit.called
    
    # "Did we try to REFRESH the user?"
    assert mock_session.refresh.called
    
    print("Service Logic Verified: DB Add/Commit called successfully.")