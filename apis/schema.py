from pydantic import BaseModel, Field
class UserCreate(BaseModel):
    name:str
    password:str
    roles:str
    department:str
class change_pass_schema(BaseModel):
    user_id:int
    new_password:str
    confirm_password:str

class add_vendor_schema(BaseModel):
    company_name:str
    company_address:str
    city:str
    state:str
    pincode:str
    gst:str
    mobilenumber:str
    created_by:str

class update_vendor_schema(BaseModel):
    company_code:str
    company_name:str
    company_address:str
    city:str
    state:str
    pincode:str
    gst:str
    mobilenumber:str
    modify_by:str

