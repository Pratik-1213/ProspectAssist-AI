import os
import json
import google.generativeai as genai
from models import CustomerData, AIExplanationResponse

def analyze_customer(customer: CustomerData) -> AIExplanationResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Return mock response for demo purposes if no API key is provided
        return AIExplanationResponse(
            lead_score=customer.lead_score or 85,
            income_estimate=int(customer.estimated_income or 85000),
            repayment_capacity="High" if (customer.foir or 1.0) < 0.4 else "Moderate",
            loan_recommendation=customer.eligible_loans[0] if customer.eligible_loans else "Credit Card",
            intent="High" if (customer.intent_score or 0) > 60 else "Moderate",
            conversion_probability=f"{customer.predicted_conversion_rate or 36.0}%",
            risk_level="Low" if (customer.foir or 1.0) < 0.5 else "High",
            key_reasons=[
                f"Accurate income assessment includes investments & deposits (FOIR: {int((customer.foir or 0)*100)}%)",
                f"High digital engagement: {customer.website_time_spent} mins spent, {customer.loan_document_downloads} docs downloaded",
                "Stable salary inflows and low existing obligations",
                "Multiple interactions with targeted loan products"
            ],
            next_best_action="Call within 24 hours and offer Home Loan with pre-approved eligibility.",
            summary=f"Customer demonstrates strong repayment capacity with a FOIR of {int((customer.foir or 0)*100)}% considering accurate income streams. Digital footprint (time spent: {customer.website_time_spent}m, downloads: {customer.loan_document_downloads}) indicates high active purchase intent."
        )

    genai.configure(api_key=api_key)
    
    # We want JSON output. The easiest way with the generative AI API is to prompt it to return JSON
    # and then parse it. In newer versions, we can use response_mime_type="application/json".
    model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"response_mime_type": "application/json"})
    
    prompt = f"""
    You are an AI Lending Intelligence Assistant working for a retail bank.
    Analyze the customer's financial profile and behavioural data.
    
    Your objectives are:
    1. Assess accurate monthly income combining salary, investments, and deposits.
    2. Quantify repayment capacity by analyzing Fixed Obligation to Income Ratio (FOIR).
    3. Predict customer interest based on digital behavioral signals (website time, downloads).
    4. Recommend the best loan product.
    5. Calculate a lead quality score from 0-100.
    6. Analyze the customer's sentiment from the recent interaction notes. Factor this into your advice.
    7. Explain the reasoning clearly, mentioning specific data points like FOIR, time spent, and sentiment.
    8. Suggest the next best action for the relationship manager. Tailor the tone of the action based on their sentiment (e.g., empathetic if frustrated, urgent if ready to proceed).

    Customer Data:
    {customer.model_dump_json()}

    Return ONLY JSON in this format:
    {{
      "lead_score": 92,
      "income_estimate": 85000,
      "repayment_capacity":"High",
      "loan_recommendation":"Home Loan",
      "intent":"High",
      "conversion_probability":"36%",
      "risk_level":"Low",
      "key_reasons":[
          "...",
          "...",
          "..."
      ],
      "next_best_action":"Call within 24 hours and offer Home Loan with pre-approved eligibility.",
      "summary":"..."
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Parse the JSON string
        result = json.loads(response.text)
        return AIExplanationResponse(**result)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        # Fallback to mock
        return AIExplanationResponse(
            lead_score=customer.lead_score or 85,
            income_estimate=int(customer.estimated_income or 85000),
            repayment_capacity="High" if (customer.foir or 1.0) < 0.4 else "Moderate",
            loan_recommendation=customer.eligible_loans[0] if customer.eligible_loans else "Credit Card",
            intent="High",
            conversion_probability=f"{customer.predicted_conversion_rate or 36.0}%",
            risk_level="Low",
            key_reasons=[
                f"Calculated FOIR: {int((customer.foir or 0)*100)}%",
                f"Digital intent signals present ({customer.website_time_spent}m on site)"
            ],
            next_best_action="Relationship Manager should call within 24 hours.",
            summary=f"Error generating AI explanation. Proceed with standard procedures. Error: {str(e)}"
        )
