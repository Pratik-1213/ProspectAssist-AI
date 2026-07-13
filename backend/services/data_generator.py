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
    
    positive_notes = [
        "Customer asked about current interest rates for home loans, seemed very interested.",
        "Positive conversation about pre-approved limit. Requested a callback tomorrow.",
        "Expressed interest in upgrading credit card to a premium tier.",
        "Inquired about prepayment charges. Seems ready to proceed with the application."
    ]
    
    negative_notes = [
        "Customer was frustrated with the long hold time on the customer service line.",
        "Complained about hidden charges in the recent statement. Very upset.",
        "Not interested in any loans. Asked not to call again.",
        "Had a bad experience with the app crashing during payment."
    ]
    
    neutral_notes = [
        "General inquiry about branch timings.",
        "Customer updated their mailing address.",
        "Requested a copy of the last 6 months statement.",
        "No recent interaction recorded."
    ]
    
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
            "product_viewed": "Home Loan" if is_high_intent else random.choice(products),
            # New Transactional fields
            "investment_income": random.randint(5000, 30000) if is_good_profile else random.randint(0, 2000),
            "recurring_deposits": random.randint(2000, 15000) if is_good_profile else 0,
            "utility_bill_payments": random.randint(2000, 8000),
            "fixed_emi_obligations": random.randint(1000, 15000) if not is_good_profile else random.randint(5000, 40000),
            # New Behavioral fields
            "website_time_spent": random.randint(15, 120) if is_high_intent else random.randint(0, 10),
            "loan_document_downloads": random.randint(1, 4) if is_high_intent else 0,
            
            # New Unstructured fields
            "recent_interaction_notes": random.choice(positive_notes) if is_high_intent else (random.choice(negative_notes) if not is_good_profile else random.choice(neutral_notes))
        }
        data.append(customer)
        
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    return filepath
