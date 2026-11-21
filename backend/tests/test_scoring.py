import pytest
from models import CustomerData
from services.scoring_service import calculate_lead_score

def test_calculate_lead_score_high_quality_borrower(monkeypatch):
    monkeypatch.setattr('services.scoring_service.get_config', lambda k, d: d)

    customer = CustomerData(
        customer_id="CUST-001",
        age=32,
        monthly_credits=100000.0,
        monthly_debits=55000.0,
        salary_credits=95000.0,
        upi_transactions=40,
        emi_history="No defaults",
        credit_card_spend=15000.0,
        balance=180000.0,
        missed_emi=0,
        occupation="Software Engineer",
        location="Pune",
        credit_bureau_score=780,
        previous_loan="Auto Loan (Closed)",
        app_visits=5,
        loan_calculator_usage=2,
        product_viewed="Home Loan",
        investment_income=12000.0,
        recurring_deposits=10000.0,
        utility_bill_payments=4500.0,
        fixed_emi_obligations=12000.0,
        website_time_spent=25,
        loan_document_downloads=1
    )
    foir = customer.fixed_emi_obligations / customer.salary_credits
    score = calculate_lead_score(customer, foir)

    assert isinstance(score, (int, float))
    assert score >= 65, f"Expected high score for prime customer, got {score}"

def test_calculate_lead_score_high_risk_borrower(monkeypatch):
    monkeypatch.setattr('services.scoring_service.get_config', lambda k, d: d)

    customer = CustomerData(
        customer_id="CUST-002",
        age=25,
        monthly_credits=25000.0,
        monthly_debits=24000.0,
        salary_credits=25000.0,
        upi_transactions=15,
        emi_history="Frequent delays",
        credit_card_spend=18000.0,
        balance=5000.0,
        missed_emi=3,
        occupation="Freelancer",
        location="Nashik",
        credit_bureau_score=520,
        previous_loan="Personal Loan (Defaulted)",
        app_visits=1,
        loan_calculator_usage=0,
        product_viewed="Instant Loan",
        investment_income=0.0,
        recurring_deposits=0.0,
        utility_bill_payments=2000.0,
        fixed_emi_obligations=18000.0,
        website_time_spent=3,
        loan_document_downloads=0
    )
    foir = customer.fixed_emi_obligations / customer.salary_credits
    score = calculate_lead_score(customer, foir)

    assert isinstance(score, (int, float))
    assert score < 45, f"Expected low score for high risk customer, got {score}"
