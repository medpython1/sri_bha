from mongoengine import *


class User(Document):
    sno=IntField()
    user_id=IntField()
    name=StringField()
    password=StringField()
    roles=StringField()
    department=StringField()
    Active_Status=StringField(default='A')

class vendor_master_data(Document):
    sno=IntField(uniuqe=True)
    company_name=StringField()
    company_code= StringField()
    company_address= StringField()
    city= StringField()
    state= StringField()
    pincode= StringField()
    gst= StringField()
    # phone_number= StringField()
    mobilenumber=StringField()
    created_on= DateTimeField()
    created_by= StringField()
    modify_by=StringField()
    modify_on=DateTimeField()
    status= StringField(default='A')