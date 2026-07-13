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
            repayment_capacity="High",
            loan_recommendation=customer.eligible_loans[0] if customer.eligible_loans else "Credit Card",
            intent="High",
            conversion_probability="36%",
            risk_level="Low",
            key_reasons=[
                "Stable salary inflows over the last six months",
                "Low debt obligations",
                "Increasing savings trend",
                "Multiple interactions with loan products"
            ],
            next_best_action="Call within 24 hours and offer Home Loan with pre-approved eligibility.",
            summary="Customer has stable salary inflows over the last six months, low debt obligations, increasing savings trend, and multiple interactions with loan products. These indicators suggest both repayment capacity and active purchase intent."
        )

    genai.configure(api_key=api_key)
    
    # We want JSON output. The easiest way with the generative AI API is to prompt it to return JSON
    # and then parse it. In newer versions, we can use response_mime_type="application/json".
    model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"response_mime_type": "application/json"})
    
    prompt = f"""
    You are an AI Lending Intelligence Assistant working for a retail bank.
    Analyze the customer's financial profile and behavioural data.
    
    Your objectives are:
    1. Estimate monthly income.
    2. Assess repayment capacity.
    3. Predict customer interest in taking a loan.
    4. Recommend the best loan product.
    5. Calculate a lead quality score from 0-100.
    6. Explain the reasoning.
    7. Mention possible risks.
    8. Suggest the next best action for the relationship manager.

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
            repayment_capacity="High",
            loan_recommendation=customer.eligible_loans[0] if customer.eligible_loans else "Credit Card",
            intent="High",
            conversion_probability="36%",
            risk_level="Low",
            key_reasons=[
                "Stable salary inflows",
                "Good credit bureau score"
            ],
            next_best_action="Relationship Manager should call within 24 hours.",
            summary=f"Error generating AI explanation. Proceed with standard procedures. Error: {str(e)}"
        )
