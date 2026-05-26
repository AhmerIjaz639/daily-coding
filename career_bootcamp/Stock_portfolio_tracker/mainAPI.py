from fastapi import (HTTPException)

from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime,date
from typing import Optional
from career_bootcamp.Stock_portfolio_tracker.database import get_db

app=FastAPI(
    title="Finance Tracker API",
    version="0.1.0",
    description="API for tracking stocks and portfolio"
)

class StockPurchae(BaseModel):
    symbol:str=Field(...,min_length=1,max_length=10)
    quantity:int=Field(...,gt=0)
    company_name:str
    buy_price:float=Field(...,gt=0)
    buy_date:date

class PortfolioHolding(BaseModel):
    id:int
    symbol:str
    company_name:Optional[str]
    quantity:float
    buy_price:float
    buy_date:date
    status:str
    created_at:datetime

class ExpenseCreate(BaseModel):
    category:str=Field(...,min_length=1,max_length=10)
    amount:float=Field(...,gt=0)
    description:Optional[str]=None
    expense_date:date


#portfolio API endpoints

@app.get("/home")
def home_page():
    return{
        "message":"Welcome to Finance Tracker API",
        "version":"1.0.0",
        "endPoints":{
            "portfolio":"/portfolio",
            "buy_stocks":"/portfolio/buy",
            "expenses":"/expenses",
            "docs":"/docs"
        }
    }

@app.post("/portfolio/buy")
def buy_stocks(stock:StockPurchae):
    try:
        with get_db() as db:
            portfolio_query="""
            insert into portfolios
                (symbol,company_name,quantity,buy_price,buy_date,status)
                values(%s,%s,%s,%s,%s,'active')
            
            """
            db.execute(
                portfolio_query,
                (stock.symbol,stock.company_name,stock.quantity,stock.buy_price,stock.buy_date)

            )
            portfolio_id=db.lastrowid

            total_cost=stock.quantity*stock.buy_price

            transaction_query="""
            insert  into transactions
                (transaction_type,symbol,quantity,price,total_amount,description,transaction_date)
                               values(%s,%s,%s,%s,%s,%s,%s)"""
            db.execute(
                transaction_query,
                ('buy', stock.symbol.upper(), stock.quantity, stock.buy_price,
                 total_cost, f'Purchased {stock.company_name}', stock.buy_date)
            )

            return{
                "message": "Stock purchased successfully",
                "portfolio_id": portfolio_id,
                "symbol": stock.symbol.upper(),
                "quantity": stock.quantity,
                "buy_price": stock.buy_price,
                "total_cost": round(total_cost, 2)
            }
    except Exception as e :
        raise HTTPException(status_code=500,detail=f"Database error:{str(e)}")


