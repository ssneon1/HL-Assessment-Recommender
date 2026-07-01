from fastapi.testclient import TestClient
from main import app
import os
from unittest.mock import patch
from models import ChatResponse, Recommendation

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_mocked():
    # If GEMINI_API_KEY is not set, we can mock the behavior
    # We will just verify the endpoint parses request correctly.
    with patch('main.process_chat') as mock_process:
        mock_process.return_value = ChatResponse(
            reply="Mocked reply",
            recommendations=[Recommendation(name="Test", url="http", test_type="K")],
            end_of_conversation=False
        )
        
        req_data = {
            "messages": [
                {"role": "user", "content": "I need a Java assessment"}
            ]
        }
        response = client.post("/chat", json=req_data)
        assert response.status_code == 200
        assert response.json()["reply"] == "Mocked reply"
        print("Test passed successfully!")

if __name__ == "__main__":
    test_health()
    test_chat_mocked()
    print("All tests passed.")
