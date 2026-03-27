from sqlalchemy import create_engine, Column, String, Float, ForeignKey

from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

# Database connection
load_dotenv()

#db_url = "postgresql://postgres:nandu2026@localhost:5432/nandudb"
DATABASE_URL =os.getenv("DATABASE_URL","postgresql://postgres:nandu2026@localhost:5432/banking_db")
#DATABASE_URL = "mysql+mysqlconnector://root:Nanvar2026@localhost/banking_db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
class User(Base):
    __tablename__ = "users" #lowercase convention
    id = Column(String(36),primary_key = True,index=True)
    username = Column(String(36),unique=True,index=True,nullable=False)
    hashed_password = Column(String(255),nullable=False)


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(String(36), primary_key=True, index=True)  # Change to String(36)
    account_number = Column(String(20),unique = True , nullable = False)
    name = Column(String(255), nullable=False)
    balance = Column(Float, nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(String(36), primary_key=True, index=True)  # Change to String(36)
    account_id = Column(String(36), ForeignKey('accounts.id'), nullable=False)  # Change to String(36)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
# Create the tables in the database
Base.metadata.create_all(bind=engine)