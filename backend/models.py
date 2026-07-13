from pydantic import BaseModel
from typing import List, Optional

class CustomerData(BaseModel):
    customer_id: str
    age: int
    monthly_credits: float
    monthly_debits: float
    salary_credits: float
    upi_transactions: int
    emi_history: str
    credit_card_spend: float
    balance: float
    missed_emi: int
    occupation: str
    location: str
    credit_bureau_score: int
    previous_loan: str
    app_visits: int
    loan_calculator_usage: int
    product_viewed: str
    
    # New Transactional fields
    investment_income: float
    recurring_deposits: float
    utility_bill_payments: float
    fixed_emi_obligations: float
    
    # New Behavioral fields
    website_time_spent: int # in minutes
    loan_document_downloads: int
    
    # New Unstructured fields
    recent_interaction_notes: Optional[str] = None
    
    # Computed fields
    lead_score: Optional[int] = None
    estimated_income: Optional[float] = None
    intent_score: Optional[int] = None
    eligible_loans: Optional[List[str]] = None
    foir: Optional[float] = None
    predicted_conversion_rate: Optional[float] = None
    sentiment_score: Optional[int] = None

class AIExplanationResponse(BaseModel):
    lead_score: int
    income_estimate: int
    repayment_capacity: str
    loan_recommendation: str
    intent: str
    conversion_probability: str
    risk_level: str
    key_reasons: List[str]
    next_best_action: str
    summary: str

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
