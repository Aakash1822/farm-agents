"""WhatsApp webhook endpoint for Twilio integration."""
from fastapi import APIRouter, Request
from twilio.request_validator import RequestValidator
import logging

from app.core.config import settings
from app.integrations.whatsapp_bot import get_whatsapp_bot

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhook/whatsapp")
async def handle_whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages from Twilio.
    
    This endpoint validates the request from Twilio and processes incoming messages.
    """
    if not settings.TWILIO_AUTH_TOKEN:
        return {"error": "Twilio not configured"}, 400

    # Validate the request is from Twilio
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    form_data = await request.form()

    request_url = str(request.url)
    is_valid = validator.validate(request_url, form_data)

    if not is_valid:
        logger.warning("Invalid Twilio request signature")
        return {"error": "Invalid signature"}, 403

    # Extract message details
    from_whatsapp = form_data.get("From")
    message_body = form_data.get("Body", "").strip()

    if not message_body:
        return {"status": "ok"}

    bot = get_whatsapp_bot()
    if not bot:
        logger.error("WhatsApp bot not initialized")
        return {"error": "Bot not initialized"}, 500

    try:
        response = await bot.handle_incoming_message(from_whatsapp, message_body)
        return response
    except Exception as e:
        logger.error(f"Error handling WhatsApp message: {e}")
        return {"error": str(e)}, 500
