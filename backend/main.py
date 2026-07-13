from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import time
import pandas as pd
import io
import os
import jwt
from typing import List

from models import CustomerData, AIExplanationResponse, UserCreate, UserLogin, Token
from services.scoring_service import enrich_customer_data
from services.ai_service import analyze_customer
from services.data_generator import generate_mock_csv
from services.auth_service import create_user, get_user_by_email, verify_password, create_access_token, SECRET_KEY, ALGORITHM
from database import save_customer, get_all_customers, get_customer as get_customer_db, log_audit

app = FastAPI(title="ProspectAssist AI Backend")
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        role: str = payload.get("role", "loan_officer")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": email, "role": role}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Setup CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/api/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# db_customers is removed, using SQLite from database.py now

@app.on_event("startup")
async def startup_event():
    # Ensure mock CSV exists on startup
    generate_mock_csv()
    
    # Setup APScheduler
    scheduler = AsyncIOScheduler()
    
    def poll_s3_mock():
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [APScheduler] Polling S3 for new Lead Data CSVs...")
        
    scheduler.add_job(poll_s3_mock, 'interval', minutes=1)
    scheduler.start()

@app.post("/api/auth/register", response_model=Token)
async def register(user: UserCreate):
    new_user = create_user(user.email, user.password)
    log_audit(new_user["email"], "register", "User registered")
    access_token = create_access_token(data={"email": new_user["email"], "role": new_user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/login", response_model=Token)
async def login(user: UserLogin):
    db_user = get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    log_audit(db_user["email"], "login", "User logged in")
    access_token = create_access_token(data={"email": db_user["email"], "role": db_user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/download-mock-csv")
async def download_mock_csv(current_user: dict = Depends(get_current_user)):
    log_audit(current_user["email"], "download_mock_csv", "Downloaded mock CSV data")
    filepath = "mock_customers.csv"
    if not os.path.exists(filepath):
        generate_mock_csv(filepath)
    return FileResponse(path=filepath, filename="mock_customers.csv", media_type='text/csv')

async def process_csv_background(df: pd.DataFrame, client_id: str):
    total = len(df)
    customers_list = []
    
    # Iterate with index explicitly to calculate progress
    for i in range(total):
        row = df.iloc[i]
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
                product_viewed=str(row.get('product_viewed', '')),
                investment_income=float(row.get('investment_income', 0)),
                recurring_deposits=float(row.get('recurring_deposits', 0)),
                utility_bill_payments=float(row.get('utility_bill_payments', 0)),
                fixed_emi_obligations=float(row.get('fixed_emi_obligations', 0)),
                website_time_spent=int(row.get('website_time_spent', 0)),
                loan_document_downloads=int(row.get('loan_document_downloads', 0)),
                recent_interaction_notes=str(row.get('recent_interaction_notes', '')) if pd.notna(row.get('recent_interaction_notes')) else None
            )
            
            # Enrich data
            enriched = enrich_customer_data(customer)
            customers_list.append(enriched)
            
            # Store in DB
            save_customer(enriched.customer_id, enriched.model_dump())
            
            # Mock Webhook/Email for Hot Leads
            if enriched.lead_score and enriched.lead_score >= 80:
                print(f"[WEBHOOK] Hot lead identified: {enriched.customer_id} (Score: {enriched.lead_score}). Sending notification...")
                log_audit("system@prospectassist.com", "webhook_trigger", f"Sent Hot Lead Webhook for {enriched.customer_id}")
            
        except Exception as e:
            print(f"Error parsing row: {e}")
            pass
            
        # Update progress every 5 rows or at the end
        if i % 5 == 0 or i == total - 1:
            percent = int(((i + 1) / total) * 100)
            await manager.send_message({"type": "progress", "percent": percent}, client_id)
            await asyncio.sleep(0.01) # Yield to event loop
            
    await manager.send_message({"type": "complete", "message": "Processing finished"}, client_id)

@app.post("/api/upload")
async def upload_csv(background_tasks: BackgroundTasks, client_id: str, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    log_audit(current_user["email"], "upload_csv", f"Uploaded file: {file.filename}")
    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")
        
    background_tasks.add_task(process_csv_background, df, client_id)
    return {"message": "Processing started in the background"}

@app.get("/api/dashboard")
async def get_dashboard_data(current_user: dict = Depends(get_current_user)):
    log_audit(current_user["email"], "view_dashboard", "Viewed dashboard data")
    customers_data = get_all_customers()
    if not customers_data:
        return {
            "total_customers": 0,
            "qualified_leads": 0,
            "hot_leads": 0,
            "expected_conversion": 0,
            "average_income": 0,
            "lead_distribution": [],
            "income_distribution": []
        }
        
    customers = [CustomerData(**c) for c in customers_data]
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

@app.get("/api/customers", response_model=List[CustomerData])
async def get_customers_endpoint(skip: int = 0, limit: int = 50, current_user: dict = Depends(get_current_user)):
    all_customers = get_all_customers()
    customers = [CustomerData(**c) for c in all_customers[skip : skip + limit]]
    return customers

@app.get("/api/export-customers")
async def export_customers_endpoint(current_user: dict = Depends(get_current_user)):
    from fastapi.responses import StreamingResponse
    log_audit(current_user["email"], "export_customers", "Exported customers to CSV")
    all_customers = get_all_customers()
    if not all_customers:
        raise HTTPException(status_code=404, detail="No data to export")
    
    df = pd.DataFrame(all_customers)
    csv_data = df.to_csv(index=False)
    
    return StreamingResponse(
        io.BytesIO(csv_data.encode()), 
        media_type='text/csv',
        headers={"Content-Disposition": "attachment; filename=exported_customers.csv"}
    )

@app.post("/api/analyze/{customer_id}", response_model=AIExplanationResponse)
async def analyze_customer_endpoint(customer_id: str, current_user: dict = Depends(get_current_user)):
    log_audit(current_user["email"], "analyze_customer", f"Viewed AI insights for {customer_id}")
    customer_data = get_customer_db(customer_id)
    if not customer_data:
        raise HTTPException(status_code=404, detail="Customer not found")
        
    customer = CustomerData(**customer_data)
    result = analyze_customer(customer)
    return result

from pydantic import BaseModel

class ConfigUpdate(BaseModel):
    configs: dict

@app.get("/api/config")
async def get_configuration(current_user: dict = Depends(get_current_user)):
    from database import get_config
    return {
        "weight_salary_stability": get_config("weight_salary_stability", "0.25"),
        "weight_average_balance": get_config("weight_average_balance", "0.20"),
        "weight_emi_history": get_config("weight_emi_history", "0.15"),
        "weight_credit_score": get_config("weight_credit_score", "0.15"),
        "weight_product_interest": get_config("weight_product_interest", "0.15"),
        "weight_spending_pattern": get_config("weight_spending_pattern", "0.10"),
    }

@app.post("/api/config")
async def update_configuration(config_update: ConfigUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update config")
    from database import set_config
    for k, v in config_update.configs.items():
        set_config(k, str(v))
    log_audit(current_user["email"], "update_config", "Updated lead scoring weights")
    return {"message": "Configuration updated successfully"}

@app.post("/api/crm/sync")
async def sync_crm(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can trigger CRM sync")
    log_audit(current_user["email"], "crm_sync", "Initiated CRM Sync")
    await asyncio.sleep(2) # Mock delay
    return {"message": "Successfully synchronized hot leads with Salesforce CRM."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
