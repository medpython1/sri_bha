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
class create_bill_schema(BaseModel):
    billing_address :str
    shipping_address :str
    eway_number :str
    purchase_number :str
    purchase_date  :str
    gst_number:str
    vechine_number :str
    product_name_list :str
    Hsn_list:str
    Quantity_list :float
    UOM_data_list:str
    price_list :float
    total_list:float
    company_name:str
    total_amount :float
    sgst :float
    file_path:str
    qr_path:str
    cgst :float
    igst:float
    total_amount_after_tax :float
    for_in_words:str

class search_vendor_data(BaseModel):
    unit_name:str

