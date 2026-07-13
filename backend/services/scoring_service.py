from models import CustomerData
from database import get_config

def calculate_lead_score(customer: CustomerData, foir: float) -> int:
    # Get dynamic weights from DB, fallback to defaults
    w_salary = float(get_config('weight_salary_stability', 0.25))
    w_balance = float(get_config('weight_average_balance', 0.20))
    w_emi = float(get_config('weight_emi_history', 0.15))
    w_credit = float(get_config('weight_credit_score', 0.15))
    w_interest = float(get_config('weight_product_interest', 0.15))
    w_spending = float(get_config('weight_spending_pattern', 0.10))

    # Salary Stability
    salary_stability = min(100, (customer.salary_credits / 100000) * 100) if customer.salary_credits else 0
    
    # Average Balance
    average_balance = min(100, (customer.balance / 200000) * 100) if customer.balance else 0
    
    # EMI History & FOIR
    if customer.missed_emi == 0:
        emi_score = 100
    elif customer.missed_emi == 1:
        emi_score = 70
    elif customer.missed_emi == 2:
        emi_score = 40
    else:
        emi_score = 0
        
    # FOIR Penalty
    if foir > 0.6:
        emi_score *= 0.4
    elif foir > 0.4:
        emi_score *= 0.8
        
    # Credit Score
    credit_score = max(0, min(100, ((customer.credit_bureau_score - 300) / 600) * 100)) if customer.credit_bureau_score else 0
    
    # Product Interest (App visits + calculator + product view)
    interest_score = min(100, (customer.app_visits * 10 + customer.loan_calculator_usage * 20 + customer.loan_document_downloads * 15))
    
    # Spending Pattern (credits vs debits, ideally some savings)
    if customer.monthly_credits > 0:
        savings_ratio = max(0, (customer.monthly_credits - customer.monthly_debits) / customer.monthly_credits)
        spending_score = min(100, savings_ratio * 200) # 50% savings ratio = 100
    else:
        spending_score = 0
        
    score = (
        w_salary * salary_stability +
        w_balance * average_balance +
        w_emi * emi_score +
        w_credit * credit_score +
        w_interest * interest_score +
        w_spending * spending_score
    )
    
    return int(min(100, max(0, score)))

def estimate_income(customer: CustomerData) -> float:
    # Accurate Assessment combining multiple quantitative streams
    base_salary = customer.salary_credits
    investment_yield = customer.investment_income
    rd_yield = customer.recurring_deposits
    other_income = max(0, (customer.monthly_credits - base_salary - investment_yield - rd_yield)) * 0.1
    return base_salary + investment_yield + rd_yield + other_income

def calculate_intent_score(customer: CustomerData) -> int:
    intent = 0
    
    # Core digital engagement
    if customer.loan_calculator_usage > 0:
        intent += 15
    if customer.loan_document_downloads > 0:
        intent += 20 * customer.loan_document_downloads
    if customer.website_time_spent > 15:
        intent += min(20, customer.website_time_spent // 3)
    
    # Product viewing specifics
    if customer.product_viewed and customer.product_viewed.lower() != 'none':
        intent += 10
        if 'mortgage' in customer.product_viewed.lower() or 'home' in customer.product_viewed.lower():
            intent += 10
            
    if customer.app_visits > 5:
        intent += 10
        
    return min(100, intent)

def determine_eligible_loans(customer: CustomerData) -> list:
    loans = []
    income = estimate_income(customer)
    
    if income >= 50000 and customer.credit_bureau_score >= 700:
        loans.append("Home Loan")
    
    if income >= 30000 and customer.credit_bureau_score >= 650:
        loans.append("Personal Loan")
        
    if income >= 40000 and customer.credit_bureau_score >= 680:
        loans.append("Car Loan")
        
    if not loans and income >= 20000:
        loans.append("Credit Card")
        
    return loans

def calculate_sentiment_score(text: str) -> int:
    if not text:
        return 50 # Neutral
    
    text = text.lower()
    positive_words = ['positive', 'interested', 'upgrade', 'premium', 'ready', 'proceed', 'good', 'great', 'happy']
    negative_words = ['frustrated', 'complained', 'upset', 'bad', 'crashing', 'hidden', 'charges', 'not interested']
    
    score = 50
    for word in positive_words:
        if word in text:
            score += 15
    for word in negative_words:
        if word in text:
            score -= 15
            
    return max(0, min(100, score))

def enrich_customer_data(customer: CustomerData) -> CustomerData:
    est_income = estimate_income(customer)
    foir = (customer.fixed_emi_obligations / est_income) if est_income > 0 else 1.0
    
    customer.foir = round(foir, 2)
    customer.estimated_income = round(est_income, 2)
    customer.sentiment_score = calculate_sentiment_score(customer.recent_interaction_notes)
    
    # Adjust intent score based on sentiment
    base_intent = calculate_intent_score(customer)
    if customer.sentiment_score > 70:
        base_intent += 15
    elif customer.sentiment_score < 40:
        base_intent -= 20
        
    customer.intent_score = max(0, min(100, base_intent))
    customer.lead_score = calculate_lead_score(customer, customer.foir)
    customer.eligible_loans = determine_eligible_loans(customer)
    
    # Predict conversion rate ensuring > 30% for high intent / good profiles
    base_conversion = (customer.intent_score * 0.4) + (customer.lead_score * 0.4)
    if foir > 0.5:
        base_conversion -= 15
    else:
        base_conversion += 5
        
    customer.predicted_conversion_rate = max(5.0, min(95.0, round(base_conversion, 1)))
    
    return customer
