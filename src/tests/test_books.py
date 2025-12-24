from fastapi import status
from datetime import datetime, date
import uuid

def test_get_all_books(client, mock_session):
    # 1. Arrange: Create valid book data (Matches your Book Schema)
    mock_book = {
        "uid": uuid.uuid4(),
        "title": "Mock Book 1",
        "author": "Author One",
        "publisher": "Publisher One",
        "published_date": date.today(),
        "page_count": 200,
        "language": "English",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    # 2. Mock the DB response
    mock_session.exec.return_value.all.return_value = [mock_book]

    # 3. Act
    response = client.get("/api/v1/books/")

    # 4. Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Mock Book 1"

def test_create_book(client, mock_session):
    # 1. Arrange
    book_data = {
        "title": "Unit Testing 101",
        "author": "Tester",
        "publisher": "TestPress",
        "published_date": "2025-01-01", # Sending String as per CreateModel
        "page_count": 100,
        "language": "English"
    }

    # 2. Act
    response = client.post("/api/v1/books/", json=book_data)

    # 3. Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Unit Testing 101"