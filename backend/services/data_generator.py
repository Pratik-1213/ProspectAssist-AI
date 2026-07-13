import pandas as pd
import random
import os

def generate_mock_csv(filepath: str = "mock_customers.csv") -> str:
    if os.path.exists(filepath):
        return filepath
        
    occupations = ["Salaried", "Self-Employed", "Business", "Professional"]
    locations = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Pune", "Chennai"]
    emi_histories = ["No Defaults", "Missed 1", "Missed 2", "No History"]
    previous_loans = ["Home Loan", "Personal Loan", "Car Loan", "Credit Card", "None"]
    products = ["Home Loan", "Personal Loan", "Car Loan", "Credit Card", "None"]
    
    data = []
    for i in range(1, 51):
        is_high_intent = random.random() > 0.7
        is_good_profile = random.random() > 0.4
        
        salary_credits = random.randint(30000, 200000) if is_good_profile else random.randint(15000, 40000)
        monthly_credits = salary_credits + random.randint(0, 20000)
        monthly_debits = int(monthly_credits * random.uniform(0.3, 0.9))
        balance = monthly_credits * random.uniform(1, 10)
        
        customer = {
            "customer_id": f"CUST{1000 + i}",
            "age": random.randint(22, 60),
            "monthly_credits": monthly_credits,
            "monthly_debits": monthly_debits,
            "salary_credits": salary_credits,
            "upi_transactions": random.randint(10, 150),
            "emi_history": "No Defaults" if is_good_profile else random.choice(emi_histories),
            "credit_card_spend": random.randint(1000, 50000),
            "balance": balance,
            "missed_emi": 0 if is_good_profile else random.randint(0, 2),
            "occupation": random.choice(occupations),
            "location": random.choice(locations),
            "credit_bureau_score": random.randint(700, 850) if is_good_profile else random.randint(500, 720),
            "previous_loan": random.choice(previous_loans),
            "app_visits": random.randint(5, 30) if is_high_intent else random.randint(0, 5),
            "loan_calculator_usage": random.randint(1, 5) if is_high_intent else 0,
            "product_viewed": "Home Loan" if is_high_intent else random.choice(products)
        }
        data.append(customer)
        
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    return filepath
