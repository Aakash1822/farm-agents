import httpx
from langchain.tools import tool
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.tools.base import tool_with_retry
import json

# Comprehensive scheme database (fallback when APIs unavailable)
SCHEMES_DATABASE = {
    "national": [
        {
            "name": "PM-KISAN",
            "benefit": "₹6,000/year in 3 installments",
            "eligibility": "Landholding farmers with cultivable land",
            "how_to_apply": "Visit pmkisan.gov.in or nearest CSC",
            "helpline": "155261"
        },
        {
            "name": "PMFBY (Crop Insurance)",
            "benefit": "Crop loss coverage at 1.5-2% premium",
            "eligibility": "Farmers growing notified crops",
            "how_to_apply": "Through banks/PACs before sowing",
            "helpline": "1800-180-1551"
        },
        {
            "name": "Soil Health Card Scheme",
            "benefit": "Free soil testing and recommendations",
            "eligibility": "All farmers",
            "how_to_apply": "Visit local agriculture office",
            "helpline": "1800-180-1551"
        },
        {
            "name": "Kisan Credit Card (KCC)",
            "benefit": "Credit at 4% interest, up to ₹3 lakh",
            "eligibility": "Farmers with cultivable land",
            "how_to_apply": "Apply at any public sector bank",
            "helpline": "1800-XXX-XXXX"
        },
        {
            "name": "PM-KUSUM",
            "benefit": "Solar pump installation subsidy",
            "eligibility": "Farmers with irrigation source",
            "how_to_apply": "Through state DISCOM",
            "helpline": "1800-180-3333"
        }
    ],
    "maharashtra": [
        {
            "name": "Maha AgX Subsidy",
            "benefit": "50-80% subsidy on agri-tech adoption",
            "eligibility": "Farmers in Maharashtra",
            "how_to_apply": "Through MahaAgX platform",
            "helpline": "1900-XXX-XXX"
        },
        {
            "name": "Maha Pashu (Livestock)",
            "benefit": "Livestock insurance at 4% premium",
            "eligibility": "Cattle/buffalo owners",
            "how_to_apply": "Through dairy cooperatives",
            "helpline": "1800-XXXX-XXX"
        },
        {
            "name": "Micro Irrigation Scheme",
            "benefit": "50-80% subsidy on drip/sprinkler",
            "eligibility": "Farmers with land",
            "how_to_apply": "Through agriculture department",
            "helpline": "1800-XXX-XXXX"
        }
    ],
    "punjab": [
        {
            "name": "Solar Pump Scheme",
            "benefit": "80% subsidy on 1-2HP pumps",
            "eligibility": "Small/marginal farmers",
            "how_to_apply": "Through PSPCL",
            "helpline": "1800-XXX-XXXX"
        },
        {
            "name": "KCC Special Scheme",
            "benefit": "4% interest, up to ₹3 lakh",
            "eligibility": "All farmers",
            "how_to_apply": "Through cooperative banks",
            "helpline": "1800-XXX-XXXX"
        }
    ],
    "up": [
        {
            "name": "MSP Procurement",
            "benefit": "Minimum support price guarantee",
            "eligibility": "Wheat/paddy farmers",
            "how_to_apply": "Register at purchase centers",
            "helpline": "1800-XXX-XXXX"
        }
    ],
    "karnataka": [
        {
            "name": "Raitha Vidya Nidhi",
            "benefit": "Education scholarship for farmers' children",
            "eligibility": "Small/marginal farmers",
            "how_to_apply": "Through e-District portal",
            "helpline": "1800-XXX-XXXX"
        }
    ],
    "tamil nadu": [
        {
            "name": "Uzhavar Sandhai",
            "benefit": "Direct farmer-to-consumer market access",
            "eligibility": "All farmers",
            "how_to_apply": "Register with agriculture department",
            "helpline": "1800-XXX-XXXX"
        }
    ]
}


@tool_with_retry(max_retries=2)
async def get_schemes(state: str, land_acres: float = 1.0, aadhar_last_4: str = None) -> str:
    """
    Get eligible government schemes for a farmer.
    Args:
        state: Indian state (maharashtra, punjab, up, etc.)
        land_acres: Land holding in acres
        aadhar_last_4: Last 4 digits of Aadhar (for eligibility check)
    """
    state = state.lower()
    
    pmkisan_data = await fetch_pmkisan_status(aadhar_last_4) if aadhar_last_4 and settings.PMKISAN_API_KEY else None
    
    state_schemes = SCHEMES_DATABASE.get(state, [])
    national_schemes = SCHEMES_DATABASE["national"]
    eligible_schemes = national_schemes + state_schemes
    
    if land_acres <= 2:
        eligible_schemes.append({
            "name": "Small/Marginal Farmer Priority",
            "benefit": "Priority in all schemes + lower interest rates",
            "eligibility": "Landholding ≤ 2 acres",
            "how_to_apply": "Automatic if land records show ≤2 acres",
            "helpline": "155261"
        })
    
    response = f"📜 *Government Schemes for {state.title()} Farmer*\n"
    response += f"🌾 *Land Holding:* {land_acres} acres"
    
    if pmkisan_data:
        response += f"\n\n💰 *PM-KISAN Status:* {pmkisan_data['status']}"
        if pmkisan_data.get('next_installment'):
            response += f"\n   • Next Installment: {pmkisan_data['next_installment']}"
    
    response += f"\n\n✅ *Eligible Schemes:*\n"
    
    for i, scheme in enumerate(eligible_schemes[:8], 1):
        response += f"\n{i}. *{scheme['name']}*\n"
        response += f"   💵 Benefit: {scheme['benefit']}\n"
        response += f"   📋 Eligibility: {scheme['eligibility']}\n"
        response += f"   📝 Apply: {scheme['how_to_apply']}\n"
        response += f"   📞 Helpline: {scheme['helpline']}\n"
    
    response += f"\n🔗 *Apply Online:*"
    response += f"\n   • PM-KISAN: pmkisan.gov.in"
    response += f"\n   • CSC Centers: csc.gov.in"
    response += f"\n   • State Portal: {state}.gov.in/agriculture"
    
    response += f"\n\n📞 *National Helplines:*"
    response += f"\n   • PM-KISAN: 155261"
    response += f"\n   • Kisan Call Centre: 1800-180-1551"
    response += f"\n   • Crop Insurance: 1800-180-1551"
    
    return response


async def fetch_pmkisan_status(aadhar_last_4: str) -> Optional[Dict[str, Any]]:
    """
    Fetch real PM-KISAN beneficiary status.
    Note: Official PM-KISAN API requires certificate-based authentication.
    This is a placeholder for the API integration pattern.
    """
    
    if not settings.PMKISAN_API_KEY or not settings.PMKISAN_CERT_PATH:
        return None
    
    # The official PM-KISAN API requires:
    # 1. API key from NIC
    # 2. Digital certificate (.p12 file)
    # 3. Registered IP address whitelisting
    
    # Endpoint (official - requires auth)
    # URL: https://pmkisan.gov.in/api/beneficiary-status
    
    async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
        try:
            
            response = await client.post(
                "https://pmkisan.gov.in/api/beneficiary-status",
                json={"aadhar_last_4": aadhar_last_4},
                headers={"X-API-Key": settings.PMKISAN_API_KEY}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": data.get("status", "Registered"),
                    "next_installment": data.get("next_payment_date", "Check portal"),
                    "last_received": data.get("last_payment_amount", "₹2,000")
                }
            
            return None
            
        except Exception as e:
            print(f"PM-KISAN API error: {e}")
            return None


async def check_scheme_eligibility(scheme_name: str, farmer_details: Dict) -> Dict:
    eligibility = {
        "eligible": True,
        "reason": "",
        "documents_required": []
    }
    
    if scheme_name == "PM-KISAN":
        exclusions = []
        
        if farmer_details.get("income_tax_payer", False):
            exclusions.append("Income Tax payer")
            eligibility["eligible"] = False
        
        if farmer_details.get("govt_employee", False):
            pension = farmer_details.get("monthly_pension", 0)
            if pension >= 10000:
                exclusions.append("Government pensioner with pension ≥ ₹10,000")
                eligibility["eligible"] = False
        
        if farmer_details.get("constitutional_post", False):
            exclusions.append("Holder of constitutional post")
            eligibility["eligible"] = False
        
        if exclusions:
            eligibility["reason"] = f"Excluded due to: {', '.join(exclusions)}"
        else:
            eligibility["documents_required"] = [
                "Land records (Khatauni/Patta)",
                "Aadhar card",
                "Bank account details",
                "Crop details (for verification)"
            ]
    
    elif scheme_name == "PMFBY":
        if farmer_details.get("loan_taken", False):
            eligibility["documents_required"] = [
                "Land records",
                "Loan documents (if applicable)",
                "Sowing certificate"
            ]
        else:
            eligibility["documents_required"] = [
                "Land records",
                "Bank account details",
                "Crop details with sowing date"
            ]
    
    return eligibility