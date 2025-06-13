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

def test_get_properties(client):
    # arrange
    test_property = {
        "title": "Test Property",
        "address": "123 Test St",
        "cover_image": "http://example.com/image.jpg"
    }
    test_property_2 = {
        "title": "Another Property",
        "address": "456 Another St",
        "cover_image": "http://example.com/image2.jpg"
    }

    # act
    client.post("/property", json=test_property)
    client.post("/property", json=test_property_2)
    response = client.get("/property")

    # assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    for property in response.json():
        assert isinstance(property, dict)
        assert "title" in property
        assert "address" in property
        assert "id" in property
        

def test_get_property_by_id(client, test_property_request):
    # arrange
    created_property = client.post("/property", json=test_property_request.model_dump())
    created_property_id = created_property.json()["id"] 

    # act
    response = client.get(f"/property/{created_property_id}")

    # assert
    assert isinstance(response.json(), dict)
    assert response.status_code == 200
    assert response.json()["id"] == created_property_id
    assert response.json()["title"] == test_property_request.title
    assert response.json()["address"] == test_property_request.address

def test_update_property_by_id(client, test_property_request):
    # arrange
    created_property = client.post("/property", json=test_property_request.model_dump())
    created_property_id = created_property.json()["id"] 
    modifications = [
        {
            "title": "modified title",
            "address": "modified address",
            "cover_image": "modified cover image"
        },
        {
            "title": "modified title",
            "address": "modified address"
        },
        {
            "title": "modified title",
            "cover_image": "modified cover image"
        },
        {
            "address": "modified address",
            "cover_image": "modified cover image"
        },
        {
            "title": "modified title"
        },
        {
            "address": "modified address"
        },
        {
            "cover_image": "modified cover image"
        }
    ]
    
    for mod in modifications:
        # act
        client.put(f"/property/{created_property_id}", json=mod)
        response = client.get(f"/property/{created_property_id}")
        # assert
        if "title" in mod:
            assert response.json()["title"] == mod["title"]
        if "address" in mod:
            assert response.json()["address"] == mod["address"]
        if "cover_image" in mod:
            assert response.json()["cover_image"] == mod["cover_image"]