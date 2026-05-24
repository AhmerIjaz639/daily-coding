from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="EMI-Calculator", version="0.1.0")


class loanReq(BaseModel):
    principal: float = Field(..., gt=0, description="Loan amount")
    interest_rate: float = Field(..., gt=0, le=100, description="Interest rate")
    tenure: int = Field(..., gt=0, description="Loan tenure in months")


@app.post("/cal-emi")
def calculate_emi(loanReq: loanReq):

    monthly_rate = (loanReq.interest_rate / 12) / 100

    emi = (
        loanReq.principal
        * monthly_rate
        * (1 + monthly_rate) ** loanReq.tenure
    ) / (((1 + monthly_rate) ** loanReq.tenure) - 1)

    total_pay = emi * loanReq.tenure

    total_interest = total_pay - loanReq.principal

    return {
        "emi": round(emi, 2),
        "total_payment": round(total_pay, 2),
        "total_interest": round(total_interest, 2)
    }