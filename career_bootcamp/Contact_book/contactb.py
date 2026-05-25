from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title='Contact Book', version='0.1.0')

contacts_db = []
contact_id_counter = 1


class CreateContact(BaseModel):
    name: str = Field(..., min_length=3, max_length=20)
    email: str = Field(..., min_length=5, max_length=30)
    phone: str = Field(..., min_length=10, max_length=15)


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class Contact(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    created_at: str


@app.get("/contacts", response_model=list[Contact])
def get_all_contacts():
    return contacts_db


@app.get("/contacts/{contact_name}", response_model=Contact)
def get_contact(contact_name: str):
    for contact in contacts_db:
        if contact["name"].lower() == contact_name.lower():
            return contact
    raise HTTPException(status_code=404, detail="Contact not found")



@app.post("/contacts", response_model=Contact)
def create_contact(contact: CreateContact):
    global contact_id_counter
    new_contact = {
        "id": contact_id_counter,
        "name": contact.name,
        "email": contact.email,
        "phone": contact.phone,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    contacts_db.append(new_contact)
    contact_id_counter += 1
    return new_contact


@app.patch("/contacts/{contact_id}", response_model=Contact)
def update_contact(contact_id: int, contact: ContactUpdate):
    for i, existing_contact in enumerate(contacts_db):
        if existing_contact["id"] == contact_id:
            update_data = contact.model_dump(exclude_none=True)
            contacts_db[i].update(update_data)
            return contacts_db[i]
    raise HTTPException(status_code=404, detail="Contact not found")


@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int):
    for i, contact in enumerate(contacts_db):
        if contact["id"] == contact_id:
            del contacts_db[i]
            return {"message": "Contact deleted successfully"}
    raise HTTPException(status_code=404, detail="Contact not found")
