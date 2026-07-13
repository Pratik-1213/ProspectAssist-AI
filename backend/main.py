from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import io
import os
from typing import List

from models import CustomerData, AIExplanationResponse
from services.scoring_service import enrich_customer_data
from services.ai_service import analyze_customer
from services.data_generator import generate_mock_csv

app = FastAPI(title="ProspectAssist AI Backend")

# Setup CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for the processed customers for the demo
db_customers = {}

@app.on_event("startup")
async def startup_event():
    # Ensure mock CSV exists on startup
    generate_mock_csv()

@app.get("/api/download-mock-csv")
async def download_mock_csv():
    filepath = "mock_customers.csv"
    if not os.path.exists(filepath):
        generate_mock_csv(filepath)
    return FileResponse(path=filepath, filename="mock_customers.csv", media_type='text/csv')

@app.post("/api/upload", response_model=List[CustomerData])
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")
        
    customers_list = []
    
    for _, row in df.iterrows():
        try:
            # Map row to CustomerData
            customer = CustomerData(
                customer_id=str(row.get('customer_id', '')),
                age=int(row.get('age', 0)),
                monthly_credits=float(row.get('monthly_credits', 0)),
                monthly_debits=float(row.get('monthly_debits', 0)),
                salary_credits=float(row.get('salary_credits', 0)),
                upi_transactions=int(row.get('upi_transactions', 0)),
                emi_history=str(row.get('emi_history', '')),
                credit_card_spend=float(row.get('credit_card_spend', 0)),
                balance=float(row.get('balance', 0)),
                missed_emi=int(row.get('missed_emi', 0)),
                occupation=str(row.get('occupation', '')),
                location=str(row.get('location', '')),
                credit_bureau_score=int(row.get('credit_bureau_score', 0)),
                previous_loan=str(row.get('previous_loan', '')),
                app_visits=int(row.get('app_visits', 0)),
                loan_calculator_usage=int(row.get('loan_calculator_usage', 0)),
                product_viewed=str(row.get('product_viewed', ''))
            )
            
            # Enrich data
            enriched = enrich_customer_data(customer)
            customers_list.append(enriched)
            
            # Store in DB
            db_customers[enriched.customer_id] = enriched
            
        except Exception as e:
            print(f"Error parsing row: {e}")
            continue
            
    return customers_list

@app.get("/api/dashboard")
async def get_dashboard_data():
    if not db_customers:
        return {
            "total_customers": 0,
            "qualified_leads": 0,
            "hot_leads": 0,
            "expected_conversion": 0,
            "average_income": 0,
            "lead_distribution": [],
            "income_distribution": []
        }
        
    customers = list(db_customers.values())
    total_customers = len(customers)
    
    qualified_leads = sum(1 for c in customers if c.lead_score and c.lead_score >= 60)
    hot_leads = sum(1 for c in customers if c.lead_score and c.lead_score >= 80)
    
    avg_income = sum(c.estimated_income for c in customers if c.estimated_income) / total_customers
    
    # Calculate distributions
    lead_distribution = [
        {"name": "Low (0-40)", "value": sum(1 for c in customers if c.lead_score and c.lead_score < 40)},
        {"name": "Medium (40-70)", "value": sum(1 for c in customers if c.lead_score and 40 <= c.lead_score < 70)},
        {"name": "High (70-90)", "value": sum(1 for c in customers if c.lead_score and 70 <= c.lead_score < 90)},
        {"name": "Hot (90-100)", "value": sum(1 for c in customers if c.lead_score and c.lead_score >= 90)},
    ]
    
    income_distribution = [
        {"name": "< 30k", "value": sum(1 for c in customers if c.estimated_income and c.estimated_income < 30000)},
        {"name": "30k-60k", "value": sum(1 for c in customers if c.estimated_income and 30000 <= c.estimated_income < 60000)},
        {"name": "60k-100k", "value": sum(1 for c in customers if c.estimated_income and 60000 <= c.estimated_income < 100000)},
        {"name": "> 100k", "value": sum(1 for c in customers if c.estimated_income and c.estimated_income >= 100000)},
    ]
    
    return {
        "total_customers": total_customers,
        "qualified_leads": qualified_leads,
        "hot_leads": hot_leads,
        "expected_conversion": round((hot_leads / total_customers) * 100) if total_customers > 0 else 0,
        "average_income": avg_income,
        "lead_distribution": lead_distribution,
        "income_distribution": income_distribution
    }

@app.post("/api/analyze/{customer_id}", response_model=AIExplanationResponse)
async def analyze_customer_endpoint(customer_id: str):
    if customer_id not in db_customers:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    customer = db_customers[customer_id]
    result = analyze_customer(customer)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
