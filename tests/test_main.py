from random import choice

from fastapi.testclient import TestClient
from starlette import status

from src.main import app

client = TestClient(app)


def test_info():
    print("eko")

    # Validation error case
    # file header for m2p, vob, mpg, mpeg
    file_header = bytes([0x00, 0x00, 0x01, 0xBA])
    filetype = 'avi'

    response = client.post(f"/utility/type/verification/{filetype}", files={"file_header": file_header})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "File content doesn't match the declared file type"
    }

    # Success case
    filetype = 'vob'
    response = client.post(f"/utility/type/verification/{filetype}", files={"file_header": file_header})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is None
