from src.entities.user import Property

"""
Validate the following scenarios:
    - Create property 
    - Get properties
    - Get property by id
    - Update property by id
    - Delete property by id
"""

def test_create_property(client, test_property_request):
    response = client.post("/property", json=test_property_request.model_dump())
    assert response.status_code == 201