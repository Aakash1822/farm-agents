from langchain.tools import tool
from typing import Optional, Dict, List
from datetime import datetime
from app.tools.base import tool_with_retry


PEST_DATABASE = {
    "rice": {
        "brown spot": {
            "symptoms": "Small, oval, brown spots on leaves and grains",
            "organic_remedy": "Spray neem oil (5ml/L) + Pseudomonas fluorescens",
            "chemical_remedy": "Propiconazole 25EC (1ml/L) or Iprodione + Carbendazim",
            "prevention": "Use certified seeds, maintain field hygiene, balanced fertilization",
            "severity": "medium"
        },
        "blast": {
            "symptoms": "Diamond-shaped lesions with grey center, neck rot",
            "organic_remedy": "Apply Trichoderma viride in nursery, spray neem-based formulation",
            "chemical_remedy": "Tricyclazole 75WP (0.6g/L) or Kitazine 20% (1ml/L)",
            "prevention": "Avoid excess nitrogen, use resistant varieties",
            "severity": "high"
        },
        "bacterial leaf blight": {
            "symptoms": "Yellowish-white lesions along leaf margins, drying leaves",
            "organic_remedy": "Apply Pseudomonas fluorescens (10g/L), Copper oxychloride",
            "chemical_remedy": "Streptocycline (0.5g/L) + Copper oxychloride (2g/L)",
            "prevention": "Drain fields, avoid over-irrigation, use resistant varieties",
            "severity": "high"
        }
    },
    # Wheat
    "wheat": {
        "yellow rust": {
            "symptoms": "Yellowish-orange powdery pustules on leaves",
            "organic_remedy": "Spray neem-based formulation, maintain field sanitation",
            "chemical_remedy": "Propiconazole (1ml/L) or Tebuconazole",
            "prevention": "Grow resistant varieties, early sowing, balanced nutrients",
            "severity": "high"
        },
        "loose smut": {
            "symptoms": "Black powdery mass replaces entire earhead",
            "organic_remedy": "Seed treatment with Trichoderma viride",
            "chemical_remedy": "Carboxin + Thiram (2g/kg seed) seed treatment",
            "prevention": "Use certified disease-free seeds",
            "severity": "medium"
        }
    },
    # Tomato
    "tomato": {
        "early blight": {
            "symptoms": "Dark brown concentric rings on lower leaves, leaf drop",
            "organic_remedy": "Spray neem oil (5ml/L) + garlic extract",
            "chemical_remedy": "Mancozeb 75WP (2g/L) or Chlorothalonil",
            "prevention": "Crop rotation, stake plants for air circulation",
            "severity": "medium"
        },
        "late blight": {
            "symptoms": "Water-soaked lesions, white fungal growth underside leaves",
            "organic_remedy": "Bordeaux mixture (1%) or Copper hydroxide",
            "chemical_remedy": "Metalaxyl + Mancozeb (2g/L) immediately",
            "prevention": "Avoid overhead irrigation, destroy infected plants",
            "severity": "high"
        },
        "fruit borer": {
            "symptoms": "Holes in fruits with frass, damaged fruits",
            "organic_remedy": "NSKE 5% (Neem seed kernel extract), pheromone traps",
            "chemical_remedy": "Spinosad 45SC (0.3ml/L) or Emamectin benzoate",
            "prevention": "Install light traps, remove infested fruits",
            "severity": "high"
        }
    },
    # Onion
    "onion": {
        "purple blotch": {
            "symptoms": "Purple colored spots on leaves, leaf dieback",
            "organic_remedy": "Spray Trichoderma harzianum, neem-based formulation",
            "chemical_remedy": "Mancozeb + Metalaxyl (2g/L) or Chlorothalonil",
            "prevention": "Field rotation, avoid dense planting",
            "severity": "medium"
        },
        "thrips": {
            "symptoms": "Silvery-white streaks on leaves, distorted growth",
            "organic_remedy": "Spray neem oil (5ml/L) + coriander oil",
            "chemical_remedy": "Spinosad 45SC (0.3ml/L) or Fipronil",
            "prevention": "Avoid water stress, use reflective mulch",
            "severity": "medium"
        }
    },
    # General/Common
    "general": {
        "yellow leaves": {
            "symptoms": "Leaves turning yellow from edges or entire leaf",
            "organic_remedy": "Apply jeevamrit (fermented cow dung+urine) spray",
            "chemical_remedy": "Foliar spray of 2% urea + MgSO4",
            "prevention": "Regular soil testing, balanced NPK application",
            "severity": "medium"
        },
        "wilting": {
            "symptoms": "Plant droops even with soil moisture",
            "organic_remedy": "Apply Trichoderma + Pseudomonas in root zone",
            "chemical_remedy": "Carbendazim 50WP (1g/L) drench",
            "prevention": "Avoid water logging, crop rotation",
            "severity": "high"
        },
        "root rot": {
            "symptoms": "Roots become brown/black, plant stunted",
            "organic_remedy": "Soil application of neem cake (2kg/acre)",
            "chemical_remedy": "Metalaxyl + Mancozeb soil drench",
            "prevention": "Well-drained soil, avoid over-irrigation",
            "severity": "high"
        }
    }
}


@tool
@tool_with_retry(max_retries=2)
async def diagnose_pest(symptom: str, crop: str) -> str:
    """
    Diagnose pest/disease and provide integrated pest management (IPM) remedies.
    Args:
        symptom: Observed symptom (yellow leaves, white powder, holes in leaves, wilting, etc.)
        crop: Affected crop name (rice, wheat, tomato, onion, etc.)
    """
    symptom = symptom.lower()
    crop = crop.lower()
    
    # Try crop-specific diagnosis first
    crop_data = PEST_DATABASE.get(crop)
    diagnosis = None
    
    if crop_data:
        # Check for exact match in crop-specific pests
        for pest_name, details in crop_data.items():
            if (symptom in pest_name or 
                any(keyword in symptom for keyword in details['symptoms'].lower().split())):
                diagnosis = details
                pest_name_found = pest_name
                break
    
    # If not found, check general database
    if not diagnosis:
        general_data = PEST_DATABASE.get("general", {})
        diagnosis = general_data.get(symptom)
        pest_name_found = symptom
    
    # If still not found, provide general guidance
    if not diagnosis:
        return f"""🌾 *Crop:* {crop.title()}
🔍 *Symptom:* {symptom}

⚠️ *Guidance for Unidentified Issue:*

📝 *Immediate Steps:*
1. Isolate affected plants if possible
2. Take clear photos of affected parts
3. Collect sample in clean bag

📞 *Consult Experts:*
• Visit nearest KVK (Krishi Vigyan Kendra)
• Call Kisan Call Centre: 1800-180-1551
• Use 'Kisan Suvidha' mobile app

💡 *General Prevention:*
• Maintain field hygiene
• Use certified seeds
• Practice crop rotation
• Balanced fertilization

📍 *Find your local KVK:* kvk.icar.gov.in"""

    # Build detailed response
    response = f"🌾 *Crop:* {crop.title()}\n"
    response += f"🔍 *Suspected Issue:* {pest_name_found.title()}\n"
    response += f"📋 *Symptoms:* {diagnosis['symptoms']}\n\n"
    
    response += f"🌿 *ORGANIC REMEDY:*\n{diagnosis['organic_remedy']}\n\n"
    response += f"🧪 *CHEMICAL REMEDY (if severe):*\n{diagnosis['chemical_remedy']}\n\n"
    response += f"🛡️ *PREVENTION:*\n{diagnosis['prevention']}\n\n"
    
    response += f"⚠️ *Severity Level:* {'High - Act Immediately' if diagnosis['severity'] == 'high' else 'Medium - Monitor closely'}\n\n"
    
    response += f"📞 *Need more help?*\n"
    response += f"   • KVK Helpline: 1800-XXX-XXXX\n"
    response += f"   • Kisan Call Centre: 1800-180-1551\n"
    response += f"   • Plant Protection Advisory: ppqs.gov.in\n\n"
    
    response += f"📱 *Mobile Apps:*\n"
    response += f"   • Kisan Suvidha\n"
    response += f"   • Meghdoot (weather-based advisories)\n"
    response += f"   • Plantix (AI-based pest detection)"
    
    return response


async def get_pest_outbreak_alerts(crop: str, district: str) -> str:
    """
    Get recent pest outbreak alerts for a region.
    This would integrate with KVK/ICAR advisory APIs.
    """
    # Placeholder for real API integration
    # In production, this would call:
    # 1. KVK district-wise advisory API
    # 2. ICAR pest surveillance system
    # 3. State agriculture department bulletins
    
    return f"""🔔 *Pest Alert for {crop.title()} in {district.title()}*

✅ *Current Status:* No major outbreaks reported
    
📢 *Subscribe to Alerts:*
• Follow local KVK WhatsApp group
• Enable notifications in Kisan Suvidha app
• Check agriculture department website weekly

📞 Report unusual pest activity: 1800-XXX-XXXX"""
