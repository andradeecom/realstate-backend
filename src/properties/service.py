from sqlmodel import Session, select, delete
from src.entities.user import Property
from uuid import UUID
from . import models, repository
from datetime import datetime
import logging
from src.entities.user import Property
from src.database.core import SessionDep
from src.exceptions import PropertyAlreadyExistsError, PropertyNotFoundError

def create_property(property: models.CreatePropertyRequest, db: SessionDep) -> models.CreatePropertyResponse:
    existing_property = db.exec(select(Property).filter(Property.address == property.address)).one_or_none() 
    # If already exists raise error
    if existing_property:
        logging.error("Property already exists")
        raise PropertyAlreadyExistsError

    # Create new Property 
    new_property = Property(
        title = property.title,
        address = property.address,
        cover_image = property.cover_image
    )

    logging.info("Property created successfully")
    repository.create_property(new_property, db)

    return models.CreatePropertyResponse(
        id=new_property.id,
        address=new_property.address,
        title=new_property.title,
        status_code=201
    )

def get_properties(db: SessionDep) -> list[models.GetPropertiesResponse]:
    db_properties = db.exec(select(Property)).all()
    properties_response = [
        models.GetPropertiesResponse(
            id=property.id,
            title=property.title,
            address=property.address,
            cover_image=property.cover_image
        ) for property in db_properties
    ]

    return properties_response

def get_property_by_id(id: UUID, db: SessionDep) -> models.GetPropertiesResponse:
    db_property = db.exec(select(Property).filter(Property.id == id)).one_or_none()
    if db_property:
        return models.GetPropertiesResponse(
            id=db_property.id,
            title=db_property.title,
            address=db_property.address,
            cover_image=db_property.cover_image
        )
    else:
        logging.error("Property not found")
        raise PropertyNotFoundError
    
def update_property_by_id(id: UUID, property: models.UpdatePropertyByIdRequest, db: SessionDep):
    db_property = db.exec(select(Property).filter(Property.id == id)).one_or_none()
    if db_property:
        if property.title:
            db_property.title = property.title
        if property.address:
            db_property.address = property.address
        if property.cover_image:
            db_property.cover_image = property.cover_image
        db_property.updated_at = datetime.now().isoformat()  
        db.commit()

    return {"message": "Property updated successfully"}  

def delete_property_by_id(id: UUID, db: SessionDep):
    db_property = db.exec(select(Property).filter(Property.id == id)).one_or_none()
    if not db_property:
        logging.error("Property not found")
        raise PropertyNotFoundError
    db.exec(delete(Property).where(Property.id == id))
    db.commit()
    return {"message": f"Property was deleted successfully"}