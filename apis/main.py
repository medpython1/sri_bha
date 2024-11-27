from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
import jwt
from mongoengine import *
import json
from starlette.responses import JSONResponse
import base64
from fastapi.staticfiles import StaticFiles
from apis.model import *
from apis.schema import *
import datetime
from jwt.exceptions import PyJWTError

app = FastAPI()

connect(db="Sri_bha",username='new_user', password='Svs@123', host="18.215.153.62", port=27017)
# connect(db="New_data",host="localhost",port=27017)

# connect( db='SMBT', username='api-user', password='mh$cover@47', host='ec2-13-127-65-92.ap-south-1.compute.amazonaws.com:27017')



SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(user_id, password):
    try:
        user = User.objects(user_id=user_id).only('password', 'roles','department').first()
        if user:
            user_dict = json.loads(user.to_json())
            password_check = pwd_context.verify(password, user_dict.get('password'))
            if password_check:
                return user_dict['roles']
        return False
    except User.DoesNotExist:
        return False


def get_password(password):
    return pwd_context.hash(password)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Invalid authentication token")
        token_data = User(user_id=user_id)
    except PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid authentication token")
    user = User.objects(user_id=user_id).first()
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.Active_Status == "A":
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

## if two or more manager having same access but different departments in that case we use this code##
def get_current_admin(current_user: User = Depends(get_current_user)):
    if  current_user.roles == "admin" and current_user.department not in ["It","Hr"]:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return current_user
def get_current_hr_access(current_user: User = Depends(get_current_user)):
    if not (current_user.department == "Hr" and (current_user.roles=="Manager" or current_user.roles=="Hr") and current_user.Active_Status=="Active"):
        # return HTTPException(status_code=400, detail="Inactive User")
        raise HTTPException(status_code=400, detail="Not enough permissions")   
    return current_user
@app.post("/token")
async def login(from_data: OAuth2PasswordRequestForm = Depends()):
    user_id = from_data.username
    password = from_data.password
    try:
        roles = authenticate_user(user_id, password)
        if not roles:
            raise ValueError("Invalid email or password")
        access_token = create_access_token(data={"sub": user_id, "roles": roles})
        data = {"Error": "False", "Message": "Login successful", "access_token": access_token, "token_type": "bearer"}
        return data
    except ValueError as e:
        data = {
            "Error": "True",
            "Message": str(e)
        }
        return JSONResponse(content=data, status_code=401)


@app.post("/signup")
async def signup(me: UserCreate, current_user: User = Depends(get_current_active_user)):
    
    result = User.objects.order_by("-user_id").first()
    if result:
        Employee_id = result.user_id + 1
    else:
        Employee_id = 1001

    password = get_password(me.password)
    user = User(sno=User.objects.count()+1,user_id=Employee_id,name=me.name, password=password, roles=me.roles, department=me.department)
    try:
        user.save()
        return {"Error":"False","message": "User created successfully"}
    except OperationError:
        return "Invalid Credentials"
    
@app.get("/get_user_list")
def getting_data(current_user: User = Depends(get_current_active_user)):
    gett_user=User.objects().to_json()
    get_data=json.loads(gett_user)
    if get_data:
        data=[{"name":data["name"],"Department":data["department"]} for data in get_data]
    return data

@app.post("/change_password")
def change_password(me:change_pass_schema, current_user: User = Depends(get_current_active_user)):
    new=User.objects(user_id=me.user_id).to_json()
    new1=json.loads(new)
    if new1:
            if me.new_password==me.confirm_password:
                a= User.objects(user_id=me.user_id).update_one(set__password=get_password(me.new_password))
                b="Successfully Updated"
                if a:
                    return {"Error":"False","Message":b}
                else:
                    a={"Error":"True","Message":"Your password and confirmation password do not match"}
                return JSONResponse(content=a, status_code=400)
            else:
                a={"Error":"True","Message":"Your password and confirmation password do not match"}
                return JSONResponse(content=a, status_code=400)
    else:
         a={"Error":"True","Message":"User Id Wrong"}
         return JSONResponse(content=a, status_code=400)
#Create Vendor Details
@app.post("/Create_vendor")
def create_vendor_fun(get_Schema:add_vendor_schema, current_user: User = Depends(get_current_active_user)):
    current_time=datetime.datetime.now()
    company_code="VEN{:002d}".format(vendor_master_data.objects.count()+1)
    store_vendor_db=vendor_master_data(sno=vendor_master_data.objects.count()+1,company_code=company_code,
                                       company_name=get_Schema.company_name,company_address=get_Schema.company_address,
                                       city=get_Schema.city,state=get_Schema.state,pincode=get_Schema.pincode,
                                       gst=get_Schema.gst,mobilenumber=get_Schema.mobilenumber,created_by=get_Schema.created_by,created_on=current_time,
                                       modify_by=get_Schema.created_by,modify_on=current_time).save()
    return {"Error":"False","message": "Vendor created successfully"}
current_time=datetime.datetime.now()
@app.get("/get_vendor_data")
def get_vendor_fun(current_user: User = Depends(get_current_active_user)):
    data={"Error":"False","Message":"Data found","Vendordata":[]}
    get_vendor_que=json.loads(vendor_master_data.objects().to_json())
    if get_vendor_que:
        geting_data=[{"sno":loop_data["sno"],"company_name":loop_data["company_name"],
                      "company_address":loop_data["company_address"],
                      "city":loop_data["city"],"state":loop_data["state"],
                      "gst":loop_data["gst"],"mobilenumber":loop_data["mobilenumber"],"Unique_id":loop_data["company_code"],"status":loop_data["status"]} for loop_data in get_vendor_que]
        data["Vendordata"].append(geting_data)

        return data
    else:
        a={"Error":"True","Message":"Data not found"}
        return JSONResponse(content=a, status_code=400)

@app.post("/update_vendor_date")
def update_vendor_fun(get_schema:update_vendor_schema, current_user: User = Depends(get_current_active_user)):
     update_vendor_query = vendor_master_data.objects(
            company_code=get_schema.company_code, status="A"
        ).update_one(
            set__company_name=get_schema.company_name,
            set__company_address=get_schema.company_address,
            set__city=get_schema.city,
            set__state=get_schema.state,
            set__pincode=get_schema.pincode,
            set__gst=get_schema.gst,
            set__mobilenumber=get_schema.mobilenumber,
            set__modify_by=get_schema.modify_by,
            set__modify_on=current_time,
        )
     if update_vendor_query:
        sucess_message={"Error":"False","Message":"Successfully Updated"}
        return JSONResponse(content=sucess_message, status_code=200)
@app.post("/generate_bill")
def generate_bill_fun(me:create_bill_schema):
    invoice_num="INV{:002d}".format(generate_bill.objects.count()+1)
    store_data_in_db=generate_bill(sno=generate_bill.objects.count()+1,
                                  invoice_no=invoice_num,
                                  eway_number=me.eway_number,purchase_number=me.purchase_number,
                                  purchase_date=me.purchase_date,company_name=me.company_name,
                                  billing_address=me.billing_address,shipping_address=me.shipping_address,
                                  gst_number=me.gst_number,vechine_number=me.vechine_number,created_on=current_time,
                                  created_by="admin"
                                  ).save()
    bill_product_details_data=bill_product_details(sno=bill_product_details.objects.count()+1,
                                              inv_bill=invoice_num,product_name=me.product_name_list,
                                              Hsn=me.Hsn_list,UOM_data=me.UOM_data_list,
                                              price=me.price_list,Amount=me.total_list,created_on=current_time,
                                              created_by="admin").save()
    bill_id="Bill{:002d}".format(bill_details.objects.count()+1)
    bill_details_data=bill_details(sno=bill_details.objects.count()+1,
                                   company_name=me.company_name,bill_id=bill_id,inv_bill=invoice_num,
                                   total_amount=me.total_amount,sgst=me.sgst,cgst=me.cgst,
                                   file_path=me.file_path,qr_code=me.qr_path,
                                   created_on=current_time,created_by="Admin").save()
    
    if store_data_in_db:
        a={"Error":"False","Message":"Successfully Bill Created"}
        return JSONResponse(content=a, status_code=200)
    else:
        a={"Error":"True","Message":"Something Went Wrong"}
        return JSONResponse(content=a, status_code=400)





                                       


