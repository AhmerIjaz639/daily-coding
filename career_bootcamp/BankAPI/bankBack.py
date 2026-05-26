from enum import Enum
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Bank API", version="0.1.0")


# DATABASES
accounts = []
transactions = []

account_id_counter = 1
transaction_id_counter = 1


# ENUMS
class AccountType(str, Enum):
    current = "current"
    saving = "saving"


class TransactionType(str, Enum):
    deposit = "deposit"
    withdraw = "withdraw"
    transfer_in = "transfer_in"
    transfer_out = "transfer_out"


# MODELS
class Account(BaseModel):

    account_number: str = Field(..., min_length=10, max_length=10)

    owner_name: str = Field(..., min_length=3, max_length=20)

    balance: float = Field(..., gt=0)

    account_type: AccountType

    status: str = "active"


class Deposit(BaseModel):

    account_id: int

    amount: float = Field(..., gt=0)


class Withdrawal(BaseModel):

    account_id: int

    amount: float = Field(..., gt=0)


class Transfer(BaseModel):

    from_account_id: int

    to_account_id: int

    amount: float = Field(..., gt=0)

    description: Optional[str] = ""


class Transaction(BaseModel):

    account_id: int

    type: TransactionType

    amount: float

    timestamp: datetime = Field(default_factory=datetime.now)

    description: Optional[str] = None

    to_account_id: Optional[int] = None


# CREATE ACCOUNT
@app.post("/create_account")
def create_account(account_data: Account):

    global account_id_counter

    new_account = {
        "account_id": account_id_counter,
        "account_number": account_data.account_number,
        "owner_name": account_data.owner_name,
        "balance": account_data.balance,
        "account_type": account_data.account_type,
        "status": account_data.status,
        "created_at": datetime.now()
    }

    accounts.append(new_account)

    account_id_counter += 1

    return {
        "message": "Account created successfully",
        "data": new_account
    }


# GET ALL ACCOUNTS
@app.get("/accounts")
def get_accounts():
    return accounts


# SEARCH ACCOUNT
@app.get("/search_account/{account_number}")
def search_account(account_number: str):

    for account in accounts:

        if account["account_number"] == account_number:
            return account

    raise HTTPException(
        status_code=404,
        detail="Account not found"
    )


# CHECK BALANCE
@app.get("/balance/{account_id}")
def check_balance(account_id: int):

    for account in accounts:

        if account["account_id"] == account_id:

            return {
                "account_id": account_id,
                "account_number": account["account_number"],
                "balance": account["balance"]
            }

    raise HTTPException(
        status_code=404,
        detail="Account not found"
    )


# DEPOSIT
@app.post("/deposit")
def deposit(deposit: Deposit):

    global transaction_id_counter

    for account in accounts:

        if account["account_id"] == deposit.account_id:

            account["balance"] += deposit.amount

            new_transaction = {
                "transaction_id": transaction_id_counter,
                "account_id": deposit.account_id,
                "type": "deposit",
                "amount": deposit.amount,
                "timestamp": datetime.now(),
                "description": "Deposit",
                "to_account_id": None
            }

            transactions.append(new_transaction)

            transaction_id_counter += 1

            return {
                "message": "Deposit successful",
                "new_balance": account["balance"]
            }

    raise HTTPException(
        status_code=404,
        detail="Account not found"
    )


# WITHDRAW
@app.post("/withdraw")
def withdraw(withdrawal: Withdrawal):

    global transaction_id_counter

    for account in accounts:

        if account["account_id"] == withdrawal.account_id:

            if account["balance"] < withdrawal.amount:

                raise HTTPException(
                    status_code=400,
                    detail="Insufficient balance"
                )

            account["balance"] -= withdrawal.amount

            new_transaction = {
                "transaction_id": transaction_id_counter,
                "account_id": withdrawal.account_id,
                "type": "withdraw",
                "amount": withdrawal.amount,
                "timestamp": datetime.now(),
                "description": "Withdrawal",
                "to_account_id": None
            }

            transactions.append(new_transaction)

            transaction_id_counter += 1

            return {
                "message": "Withdrawal successful",
                "new_balance": account["balance"]
            }

    raise HTTPException(
        status_code=404,
        detail="Account not found"
    )


# TRANSFER
@app.post("/transfer")
def transfer_money(transfer: Transfer):

    global transaction_id_counter

    sender = None
    receiver = None

    for account in accounts:

        if account["account_id"] == transfer.from_account_id:
            sender = account

        if account["account_id"] == transfer.to_account_id:
            receiver = account

    if sender is None:
        raise HTTPException(404, "Sender account not found")

    if receiver is None:
        raise HTTPException(404, "Receiver account not found")

    if sender["balance"] < transfer.amount:
        raise HTTPException(400, "Insufficient balance")

    sender["balance"] -= transfer.amount

    receiver["balance"] += transfer.amount


    # Sender Transaction
    sender_transaction = {
        "transaction_id": transaction_id_counter,
        "account_id": transfer.from_account_id,
        "type": "transfer_out",
        "amount": transfer.amount,
        "timestamp": datetime.now(),
        "description": transfer.description,
        "to_account_id": transfer.to_account_id
    }

    transactions.append(sender_transaction)

    transaction_id_counter += 1


    # Receiver Transaction
    receiver_transaction = {
        "transaction_id": transaction_id_counter,
        "account_id": transfer.to_account_id,
        "type": "transfer_in",
        "amount": transfer.amount,
        "timestamp": datetime.now(),
        "description": transfer.description,
        "to_account_id": transfer.from_account_id
    }

    transactions.append(receiver_transaction)

    transaction_id_counter += 1

    return {
        "message": "Transfer successful",
        "sender_balance": sender["balance"],
        "receiver_balance": receiver["balance"]
    }


# GET TRANSACTIONS
@app.get("/transactions")
def get_transactions():
    return transactions