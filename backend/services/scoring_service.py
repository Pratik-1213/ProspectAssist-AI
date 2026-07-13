from models import CustomerData

def calculate_lead_score(customer: CustomerData) -> int:
    # 0.25 Salary Stability
    salary_stability = min(100, (customer.salary_credits / 100000) * 100) if customer.salary_credits else 0
    
    # 0.20 Average Balance
    average_balance = min(100, (customer.balance / 200000) * 100) if customer.balance else 0
    
    # 0.15 EMI History
    if customer.missed_emi == 0:
        emi_score = 100
    elif customer.missed_emi == 1:
        emi_score = 70
    elif customer.missed_emi == 2:
        emi_score = 40
    else:
        emi_score = 0
        
    # 0.15 Credit Score
    credit_score = max(0, min(100, ((customer.credit_bureau_score - 300) / 600) * 100)) if customer.credit_bureau_score else 0
    
    # 0.15 Product Interest (App visits + calculator + product view)
    interest_score = min(100, (customer.app_visits * 10 + customer.loan_calculator_usage * 20))
    
    # 0.10 Spending Pattern (credits vs debits, ideally some savings)
    if customer.monthly_credits > 0:
        savings_ratio = max(0, (customer.monthly_credits - customer.monthly_debits) / customer.monthly_credits)
        spending_score = min(100, savings_ratio * 200) # 50% savings ratio = 100
    else:
        spending_score = 0
        
    score = (
        0.25 * salary_stability +
        0.20 * average_balance +
        0.15 * emi_score +
        0.15 * credit_score +
        0.15 * interest_score +
        0.10 * spending_score
    )
    
    return int(min(100, max(0, score)))

def estimate_income(customer: CustomerData) -> float:
    # Estimate based on salary credits and other credits
    base_salary = customer.salary_credits
    other_income = (customer.monthly_credits - customer.salary_credits) * 0.3 # Assuming 30% of other credits are income
    return base_salary + max(0, other_income)

def calculate_intent_score(customer: CustomerData) -> int:
    intent = 0
    if customer.loan_calculator_usage > 0:
        intent += 20
    
    if customer.product_viewed and customer.product_viewed.lower() != 'none':
        intent += 15
        if 'mortgage' in customer.product_viewed.lower() or 'home' in customer.product_viewed.lower():
            intent += 15
            
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

def enrich_customer_data(customer: CustomerData) -> CustomerData:
    customer.lead_score = calculate_lead_score(customer)
    customer.estimated_income = estimate_income(customer)
    customer.intent_score = calculate_intent_score(customer)
    customer.eligible_loans = determine_eligible_loans(customer)
    return customer
