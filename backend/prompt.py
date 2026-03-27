# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

#want to create a banking application using fastapi, what are the steps to create it?
# To create a banking application using FastAPI, you can follow these steps:
# 1. Define the requirements: Determine the features and functionalities you want to include in your banking application, such as account creation, balance inquiry, fund transfer, transaction history, etc.
# #implement crud operations for accounts and transactions
# 2. Set up the project: Create a new FastAPI project and set up the necessary dependencies, such as a database (e.g., PostgreSQL, MySQL) and an ORM (e.g., SQLAlchemy) for database interactions.

# 3. Design the database schema: Create a database schema that includes tables for accounts, transactions, and any other relevant entities. Define the relationships between these tables.
# 4. Implement the API endpoints: Create API endpoints for each of the functionalities you defined in step 1. For example, you can create endpoints for creating an account, retrieving account details, performing fund transfers, and fetching transaction history.
# 5. Implement authentication and authorization: Implement a secure authentication mechanism (e.g., JWT) to ensure that only authorized users can access the banking application and perform actions on their accounts.
# 6. Test the application: Write unit tests and integration tests to ensure that your banking application works as expected and handles edge cases properly.
# 7. Deploy the application: Once you have tested your application, you can deploy it to a hosting service (e.g., AWS, Heroku) to make it accessible to users.
# 8. Monitor and maintain the application: After deployment, monitor the application for performance issues, security vulnerabilities, and user feedback. Regularly update the application to fix bugs and add new features as needed.

# letus start with step 1, define the requirements for the banking application. What features and functionalities do you want to include in your banking application?yes
# here are some common features and functionalities that you might want to include in your banking application:crud operations for accounts and transactions, account creation, balance inquiry, fund transfer, transaction history, user authentication and authorization, account management (e.g., updating account details, closing accounts), notifications (e.g., email or SMS alerts for transactions), and reporting (e.g., generating account statements).


let's start with implementing CRUD operations for accounts and transactions. We will create API endpoints for creating, reading, updating, and deleting accounts and transactions.

from site import venv
from turtle import setup

from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import List
from uuid import uuid4

app = FastAPI()
# In-memory storage for accounts and transactions
accounts = {}
transactions = {}
# Pydantic models for request and response bodies

class AccountCreate(BaseModel):
    name: str
    initial_balance: float
class Account(BaseModel):
    id: str
    name: str
    balance: float
class Transaction(BaseModel):
    account_id: str
    amount: float
    description: str
# API endpoints for accounts
@app.post("/accounts/", response_model=Account)
def create_account(account: AccountCreate):
    account_id = str(uuid4())
    new_account = Account(id=account_id, name=account.name, balance=account.initial_balance)
    accounts[account_id] = new_account
    return new_account
@app.get("/accounts/{account_id}", response_model=Account)
def read_account(account_id: str):
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    return accounts[account_id]
@app.put("/accounts/{account_id}", response_model=Account)
def update_account(account_id: str, account: AccountCreate):
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    updated_account = Account(id=account_id, name=account.name, balance=account.initial_balance)
    accounts[account_id] = updated_account
    return updated_account
@app.delete("/accounts/{account_id}")
def delete_account(account_id: str):
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    del accounts[account_id]
    return {"detail": "Account deleted"}
# API endpoints for transactions
@app.post("/transactions/", response_model=Transaction)
def create_transaction(transaction: Transaction):
    if transaction.account_id not in accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    account = accounts[transaction.account_id]
    account.balance += transaction.amount
    transactions[str(uuid4())] = transaction
    return transaction
@app.get("/transactions/{account_id}", response_model=List[Transaction])
def read_transactions(account_id: str):
    if account_id not in accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    return [t for t in transactions.values() if t.account_id == account_id]
@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: str):
    if transaction_id not in transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")
    del transactions[transaction_id]
    return {"detail": "Transaction deleted"}

let's start with implementing CRUD operations for accounts and transactions. We will create API endpoints for creating, reading, updating, and deleting accounts and transactions.
did we completed the CRUD operations for accounts and transactions? Yes, we have implemented the CRUD operations for both accounts and transactions in the provided code. You can create, read, update, and delete accounts and transactions using the respective API endpoints.

setup the project: Create a new FastAPI project and set up the necessary dependencies, such as a database (e.g., PostgreSQL, MySQL) and an ORM (e.g., SQLAlchemy) for database interactions.
To set up a FastAPI project with a database and an ORM, you can follow these steps:
1. Create a new directory for your project and navigate into it:
```bashmkdir banking-app
cd banking-app
```
2. Create a virtual environment and activate it:
```bashpython -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
3. Install FastAPI, Uvicorn (for running the server), SQLAlchemy (for ORM), and a database driver (e.g., psycopg2 for PostgreSQL):
```bashpip install fastapi uvicorn sqlalchemy mysql-connector-python
letus this with mysql, then we will install mysql-connector-python instead of psycopg2
```
4. Create a new file named `main.py` and add the code for your FastAPI application (you can use the code provided in the previous response as a starting point).
5. Set up the database connection and define your database models using SQLAlchemy. You can create a new file named `models.py` and define your database schema there.
6. Update your `main.py` to include the database connection and use the models defined in `models.py` for your API endpoints.
7. Run your FastAPI application using Uvicorn:
```bashuvicorn main:app --reload
```
This will start the server and you can access your API endpoints at `http://localhost:8000`. You can use tools like Postman or curl to test your API endpoints for creating, reading, updating, and deleting accounts and transactions.

Set up the database connection and define your database models using SQLAlchemy. You can create a new file named `models.py` and define your database schema there.
To set up the database connection and define your database models using SQLAlchemy, you can follow these steps:
1. Create a new file named `models.py` in your project directory.
2. In `models.py`, import the necessary modules and set up the database connection using SQLAlchemy. Define your database models for accounts and transactions. Here is an example of how you can do this:
```python
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey

# Database connection
DATABASE_URL = "mysql+mysqlconnector://username:Nanvar@2026@localhost/banking_db"
engine = create_engine(DATABASE_URL)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    balance = Column(Float, nullable=False)
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
# Create the tables in the database
Base.metadata.create_all(bind=engine)
```
3. Update your `main.py` to include the database connection and use the models defined in `models.py` for your API endpoints. You will need to import the models and set up a session to interact with the database. Here is an example of how you can do this:
```python
from sqlalchemy.orm import sessionmaker
from models import engine, Account, Transaction
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# In your API endpoints, you can now use the session to interact with the database
@app.post("/accounts/", response_model=Account)
def create_account(account: AccountCreate):
    db = SessionLocal()
    new_account = Account(name=account.name, balance=account.initial_balance)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account
```
Make sure to update the other API endpoints similarly to use the database session for CRUD operations on accounts and transactions.

@app.post("/accounts",response_model = Account)
def create_account(account : AccountCreate):
    db = SessionLocal()
    
    account_id = str(uuid4)
    new_account = Account(id = account_id, name = account.name, balance = account.initial_balance)
    accounts[account_id] = new_account
    return new_account
fix here
@app.post("/accounts",response_model = Account)
def create_account(account : AccountCreate):
    db = SessionLocal()
    account_id = str(uuid4())
    new_account = Account(id=account_id, name=account.name, balance=account.initial_balance)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account
    

