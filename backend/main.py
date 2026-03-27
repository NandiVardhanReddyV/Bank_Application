from site import venv
from turtle import setup
from unicodedata import name
from fastapi.security import OAuth2PasswordRequestForm,HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI,HTTPException,Depends
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from datetime import timedelta,datetime,timezone
from sqlalchemy.orm import sessionmaker,Session
from models import engine, Account as AccountModel, Transaction as TransactionModel,User as UserModel
from jose import jwt, JWTError
from fastapi.middleware.cors import CORSMiddleware
import random


from auth import(
    hash_password,verify_password,create_access_token,decode_token,
    oauth2_scheme, Token,UserCreate,UserResponse, TokenData,
    ACCESS_TOKEN_EXPIRE_MINUTES,IST,SECRET_KEY,ALGORITHM
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#In memory Storage for accounts and transaction
SessionLocal = sessionmaker(autocommit = False,autoflush = False, bind = engine)

accounts = {}
transactions = {}

# ----- DB dependency ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Auth dependency --------
def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> UserModel:
    token_data: TokenData = decode_token(token)
    user = db.query(UserModel).filter(UserModel.username == token_data.username).first()
    if not user:
        raise HTTPException(status_code = 401,detail = "User not found")
    return user
def generate_account_number(db: Session) -> str:
    """ Generate a unique 12-digit account number."""
    while True:
        account_number = str(random.randint(100000000000, 999999999999))
        exists = db.query(AccountModel).filter(
            AccountModel.account_number == account_number
        ).first()
        if not exists:
            return account_number # guaranteed unique

#pydantic models for request and response bodies
class AccountCreate(BaseModel):
    name: str
    balance: float
    model_config = {"from_attributes": True}  # ✅ Pydantic v2


class Account(BaseModel):
    id: str
    account_number: str      # ← must be account_number not account
    name: str
    balance: float

class TransactionCreate(BaseModel):
    account_id:str
    amount: float
    description:str

class Transaction(BaseModel):
    id: str  # Add id field to Transaction model
    account_id: str  # Add account_id field to Transaction model
    amount: float
    description: str
    model_config = {"from_attributes": True}  # ✅ Pydantic v2

class TransactionWithAccount(BaseModel):
    transaction_id: str
    account_id: str
    amount: float
    description: str
    # model_config = {"from_attributes": True}  # ✅ Pydantic v2

# --- Auth routes -----------
@app.post("/auth/register",response_model = UserResponse)
def register(user: UserCreate,db: Session = Depends(get_db)):
    #"Register a new user."
    existing = db.query(UserModel).filter(UserModel.username ==user.username).first()
    if existing:
        raise HTTPException(status_code = 400,detail = "Username already taken")
    new_user = UserModel(
        id = str(uuid4()),
        username = user.username,
        hashed_password = hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login",response_model = Token)
def login(form: OAuth2PasswordRequestForm = Depends(),db :Session = Depends(get_db)):
    """ Login and receive a JWT access token."""
    user = db.query(UserModel).filter(UserModel.username == form.username).first()
    if not user or not verify_password(form.password,user.hashed_password):
        raise HTTPException(status_code = 401,detail = "Incorrect username or password")
    token = create_access_token(
        data = {"sub": user.username},
        expires_delta = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)

    )
    return {"access_token": token,"token_type":"bearer"}

@app.post("/auth/verify",response_model = None)
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        payload = jwt.decode(credentials.credentials,SECRET_KEY,algorithms=[ALGORITHM])
        exp_utc = datetime.fromtimestamp(payload.get("exp"), tz = timezone.utc)
        exp_ist = exp_utc.astimezone(IST)
        now_ist = datetime.now(IST)
        remaining = exp_ist - now_ist

        return {
            "valid": True,
            "username": payload.get("sub"),
            "expires_at_ist": exp_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
            "current_time_ist": now_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
            "minutes_remaining": max(0,int(remaining.total_seconds() / 60))

        }
    except JWTError:
        raise HTTPException(status_code = 401,detail = "Invalid or expired token")

#API endpoints for accounts
@app.get("/accounts",response_model = List[Account])
def read_accounts(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) # protected
):
    
    return db.query(AccountModel).all()

@app.post("/accounts", response_model=Account)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    account_number = generate_account_number(db) # ✅auto generate
    new_account = AccountModel(
        id=str(uuid4()), 
        account_number = account_number,        # ✅ pass it here
        name=account.name, 
        balance=account.balance
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

@app.get("/accounts/{account_id}", response_model=Account)
def read_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    
    account = db.query(AccountModel).filter(AccountModel.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not Found")
    return account
@app.put("/accounts/{account_id}", response_model=Account)
def update_account(
    account_id: str,
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)  # protected
):
    existing = db.query(AccountModel).filter(AccountModel.id == account_id ).first()
    if not existing:
        raise HTTPException(status_code = 404,detail = "Account not found")
    existing.name = account.name
    existing.balance = account.balance
    db.commit()
    db.refresh(existing)
    return existing

@app.delete("/accounts/{account_id}")
def delete_account(
    account_id: str,
    db : Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    
    account = db.query(AccountModel).filter(AccountModel.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not Found")
    db.delete(account)
    db.commit()
    return {"detail": "Account deleted"}
# API endpoints for transactions
@app.get("/transactions",response_model = List[Transaction])
def read_all_transactions(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) # protected
):
    return db.query(TransactionModel).all()
@app.get("/transactionswithaccount", response_model=List[TransactionWithAccount])
def read_all_transactions(
    db: Session = Depends(get_db),
    current_user : UserModel = Depends(get_current_user) #protected
):
    
    transactions = db.query(TransactionModel).all()
    result = []
    for transaction in transactions:
        account = db.query(AccountModel).filter(AccountModel.id == transaction.account_id).first()
        result.append(TransactionWithAccount(
            transaction_id=transaction.id,
            account_id=transaction.account_id,
            amount=transaction.amount,
            description=transaction.description
        ))
    return result
@app.post("/transactions", response_model=Transaction)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) # protected
):
    
    account = db.query(AccountModel).filter(AccountModel.id == transaction.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not Found")
    account.balance += transaction.amount
    new_transaction = TransactionModel(
        id=str(uuid4()),
        account_id=transaction.account_id, 
        amount=transaction.amount,
        description=transaction.description
        )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction
@app.get("/transactions/{account_id}", response_model=List[Transaction])
def read_transactions(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) # protected
    ):
    
    account = db.query(AccountModel).filter(AccountModel.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not Found")
    return db.query(TransactionModel).filter(TransactionModel.account_id == account_id).all()
@app.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    
    transaction = db.query(TransactionModel).filter(TransactionModel.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not Found")
    db.delete(transaction)
    db.commit()
    return {"detail": "Transaction deleted"}









