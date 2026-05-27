from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional
from decimal import Decimal, ROUND_HALF_UP

from career_bootcamp.InvestmentCal.databaseInvest import get_db
from career_bootcamp.InvestmentCal.queriesInvest import *

app = FastAPI(
    title="Investment Calculator",
    version="1.0.0",
    description="Track investments with precise calculations"
)




def safe_percentage(profit, invested):
    """Calculate percentage safely (handles zero division)"""
    if not invested or invested == 0:
        return 0.0
    return round(float((profit / invested) * 100), 2)


def safe_round(value, decimals=2):
    """Safely round a value (handles None and Decimal)"""
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value.quantize(Decimal('0.01'), ROUND_HALF_UP))
    return round(float(value), decimals)




class InvestmentCreate(BaseModel):
    asset_name: str = Field(..., min_length=2, max_length=100)
    asset_type: str = Field(..., min_length=2, max_length=50)
    buy_price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    quantity: Decimal = Field(..., gt=0, max_digits=10, decimal_places=4)
    buy_date: date
    current_price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)

    @validator('asset_type')
    def validate_type(cls, v):
        valid = ['stock', 'crypto', 'gold', 'real_estate', 'mutual_fund', 'bond', 'other']
        if v.lower() not in valid:
            raise ValueError(f'Must be one of: {", ".join(valid)}')
        return v.lower()

    class Config:
        json_encoders = {
            Decimal: float
        }


class PriceUpdate(BaseModel):
    current_price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)

    class Config:
        json_encoders = {
            Decimal: float
        }



@app.get("/")
def home():
    return {
        "message": "Investment Calculator API",
        "version": "1.0.0",
        "features": [
            "Precise decimal calculations",
            "Portfolio tracking",
            "Performance analytics",
            "Asset type filtering"
        ]
    }


@app.post("/invest", status_code=201)
def add_investment(investment: InvestmentCreate):
    """Add new investment with precise calculations"""
    try:
        with get_db() as db:
            db.execute(
                add_in_investment,
                (
                    investment.asset_name,
                    investment.asset_type,
                    float(investment.buy_price),
                    float(investment.quantity),
                    investment.buy_date,
                    float(investment.current_price)
                )
            )
            investment_id = db.lastrowid


            invested = investment.buy_price * investment.quantity
            current_value = investment.quantity * investment.current_price
            profit = current_value - invested
            profit_percent = safe_percentage(profit, invested)

            return {
                "message": "Investment added successfully",
                "investment_id": investment_id,
                "asset_name": investment.asset_name,
                "asset_type": investment.asset_type,
                "total_invested": safe_round(invested),
                "current_value": safe_round(current_value),
                "profit_loss": safe_round(profit),
                "profit_percent": profit_percent,
                "status": "profit" if profit > 0 else "loss" if profit < 0 else "breakeven"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/investments")
def get_all_investments():
    """Get all investments with MySQL calculations (most precise!)"""
    try:
        with get_db() as db:
            query = """
                    SELECT id, \
                           asset_name, \
                           asset_type, \
                           buy_price, \
                           quantity, \
                           current_price, \
                           buy_date, \
                           created_at, \
                           CAST(ROUND(quantity * buy_price, 2) AS DECIMAL(15, 2))                                as invested, \
                           CAST(ROUND(quantity * current_price, 2) AS DECIMAL(15, 2))                            as current_value, \
                           CAST(ROUND((quantity * current_price) - (quantity * buy_price), 2) AS DECIMAL(15, 2)) as profit_loss, \
                           CAST(ROUND( \
                                   CASE \
                                       WHEN (quantity * buy_price) = 0 THEN 0 \
                                       ELSE ((current_price - buy_price) / buy_price * 100) \
                                       END, 2 \
                                ) AS DECIMAL(10, 2))                                                             as profit_percent
                    FROM investments
                    ORDER BY buy_date DESC \
                    """
            db.execute(query)
            investments = db.fetchall()

            if not investments:
                return {
                    "message": "No investments found. Add one with POST /invest",
                    "total_investments": 0,
                    "investments": []
                }


            total_invested = sum(Decimal(str(inv['invested'])) for inv in investments)
            total_current = sum(Decimal(str(inv['current_value'])) for inv in investments)
            total_profit = sum(Decimal(str(inv['profit_loss'])) for inv in investments)

            return {
                "total_investments": len(investments),
                "summary": {
                    "total_invested": safe_round(total_invested),
                    "total_current_value": safe_round(total_current),
                    "total_profit_loss": safe_round(total_profit),
                    "total_profit_percent": safe_percentage(total_profit, total_invested)
                },
                "investments": investments
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/invest/{investment_id}/price")
def update_price(investment_id: int, price_update: PriceUpdate):
    """Update current price with precise calculations"""
    try:
        with get_db() as db:
            # Get investment
            db.execute("SELECT * FROM investments WHERE id = %s", (investment_id,))
            investment = db.fetchone()

            if not investment:
                raise HTTPException(status_code=404, detail="Investment not found")

            # Update price
            db.execute(
                "UPDATE investments SET current_price = %s WHERE id = %s",
                (float(price_update.current_price), investment_id)
            )


            quantity = Decimal(str(investment['quantity']))
            buy_price = Decimal(str(investment['buy_price']))
            new_price = price_update.current_price

            invested = quantity * buy_price
            new_value = quantity * new_price
            profit = new_value - invested

            return {
                "message": "Price updated successfully",
                "asset_name": investment['asset_name'],
                "old_price": safe_round(investment['current_price']),
                "new_price": safe_round(new_price),
                "price_change": safe_round(new_price - Decimal(str(investment['current_price']))),
                "new_value": safe_round(new_value),
                "profit_loss": safe_round(profit),
                "profit_percent": safe_percentage(profit, invested)
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/summary")
def get_summary():
    """Get portfolio summary with MySQL aggregations"""
    try:
        with get_db() as db:
            query = """
                    SELECT COUNT(*)                                                                                   as total_assets, \
                           CAST(ROUND(SUM(quantity * buy_price), 2) AS DECIMAL(15, 2))                                as total_invested, \
                           CAST(ROUND(SUM(quantity * current_price), 2) AS DECIMAL(15, 2))                            as total_current_value, \
                           CAST(ROUND(SUM((quantity * current_price) - (quantity * buy_price)), 2) AS DECIMAL(15, 2)) as total_profit
                    FROM investments \
                    """
            db.execute(query)
            summary = db.fetchone()

            if summary['total_assets'] == 0:
                return {"message": "No investments found"}

            total_invested = Decimal(str(summary['total_invested']))
            total_current = Decimal(str(summary['total_current_value']))
            total_profit = Decimal(str(summary['total_profit']))

            return {
                "total_assets": summary['total_assets'],
                "total_invested": safe_round(total_invested),
                "total_current_value": safe_round(total_current),
                "total_profit_loss": safe_round(total_profit),
                "total_profit_percent": safe_percentage(total_profit, total_invested),
                "status": "Profit 📈" if total_profit > 0 else "Loss 📉" if total_profit < 0 else "Breakeven ➡️"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/invest/type/{asset_type}")
def get_by_type(asset_type: str):
    """Filter by asset type"""
    try:
        with get_db() as db:
            query = """
                    SELECT id, \
                           asset_name, \
                           asset_type, \
                           quantity, \
                           buy_price, \
                           current_price, \
                           CAST(ROUND(quantity * buy_price, 2) AS DECIMAL(15, 2))                                as invested, \
                           CAST(ROUND(quantity * current_price, 2) AS DECIMAL(15, 2))                            as current_value, \
                           CAST(ROUND((quantity * current_price) - (quantity * buy_price), 2) AS DECIMAL(15, 2)) as profit_loss, \
                           CAST(ROUND( \
                                   CASE \
                                       WHEN (quantity * buy_price) = 0 THEN 0 \
                                       ELSE ((current_price - buy_price) / buy_price * 100) \
                                       END, 2 \
                                ) AS DECIMAL(10, 2))                                                             as profit_percent
                    FROM investments
                    WHERE asset_type = %s
                    ORDER BY profit_percent DESC \
                    """
            db.execute(query, (asset_type.lower(),))
            investments = db.fetchall()

            if not investments:
                raise HTTPException(404, f"No {asset_type} investments found")

            return {
                "asset_type": asset_type.title(),
                "count": len(investments),
                "investments": investments
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/invest/best")
def get_best():
    """Best performer"""
    try:
        with get_db() as db:
            query = """
                    SELECT asset_name, \
                           asset_type, \
                           buy_price, \
                           current_price, \
                           CAST(ROUND(((current_price - buy_price) / buy_price * 100), 2) AS DECIMAL(10, 2)) as profit_percent
                    FROM investments
                    ORDER BY profit_percent DESC LIMIT 1 \
                    """
            db.execute(query)
            best = db.fetchone()

            if not best:
                raise HTTPException(404, "No investments found")

            return {
                "title": " Best Performer",
                "asset_name": best['asset_name'],
                "asset_type": best['asset_type'],
                "buy_price": safe_round(best['buy_price']),
                "current_price": safe_round(best['current_price']),
                "profit_percent": safe_round(best['profit_percent'])
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/invest/worst")
def get_worst():
    """Worst performer"""
    try:
        with get_db() as db:
            query = """
                    SELECT asset_name, \
                           asset_type, \
                           buy_price, \
                           current_price, \
                           CAST(ROUND(((current_price - buy_price) / buy_price * 100), 2) AS DECIMAL(10, 2)) as profit_percent
                    FROM investments
                    ORDER BY profit_percent ASC LIMIT 1 \
                    """
            db.execute(query)
            worst = db.fetchone()

            if not worst:
                raise HTTPException(404, "No investments found")

            return {
                "title": " Worst Performer",
                "asset_name": worst['asset_name'],
                "asset_type": worst['asset_type'],
                "buy_price": safe_round(worst['buy_price']),
                "current_price": safe_round(worst['current_price']),
                "profit_percent": safe_round(worst['profit_percent'])
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/invest/{investment_id}")
def delete_investment(investment_id: int):
    """Delete investment"""
    try:
        with get_db() as db:
            db.execute("SELECT * FROM investments WHERE id = %s", (investment_id,))
            investment = db.fetchone()

            if not investment:
                raise HTTPException(404, "Investment not found")

            db.execute("DELETE FROM investments WHERE id = %s", (investment_id,))

            return {
                "message": "Investment deleted successfully",
                "deleted_asset": investment['asset_name']
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))