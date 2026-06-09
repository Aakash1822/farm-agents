"""WhatsApp bot integration via Twilio for Kisan Saarthi."""
import logging
import httpx
from typing import Optional
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

logger = logging.getLogger(__name__)


class WhatsAppBot:
    """WhatsApp bot handler using Twilio."""

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_whatsapp: str,
        backend_url: str = "http://localhost:8000",
    ):
        """Initialize WhatsApp bot with Twilio credentials.
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            from_whatsapp: Twilio WhatsApp sender number (e.g., "whatsapp:+1234567890")
            backend_url: Backend API URL
        """
        self.client = Client(account_sid, auth_token)
        self.from_whatsapp = from_whatsapp
        self.backend_url = backend_url

    async def handle_incoming_message(
        self, from_whatsapp: str, message_body: str
    ) -> MessagingResponse:
        """Handle incoming WhatsApp message and return response.
        
        Args:
            from_whatsapp: Sender's WhatsApp number
            message_body: The message text
            
        Returns:
            MessagingResponse object to send back to Twilio
        """
        user_id = from_whatsapp.replace("whatsapp:", "").replace("+", "")
        session_id = f"whatsapp_{user_id}"

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "query": message_body,
                    "user_id": user_id,
                    "session_id": session_id,
                    "language": "hi",
                }
                response = await client.post(
                    f"{self.backend_url}/api/v1/ask",
                    json=payload,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
                answer = data.get("response", "माफ कीजिए, मुझे जवाब नहीं मिला।")
        except Exception as e:
            logger.error(f"Error calling backend: {e}")
            answer = f"माफ कीजिए, मुझे समस्या हुई। कृपया फिर से कोशिश करें।"

        resp = MessagingResponse()
        resp.message(answer)
        return resp

    def send_message(self, to_whatsapp: str, message: str) -> None:
        """Send a WhatsApp message.
        
        Args:
            to_whatsapp: Recipient WhatsApp number
            message: Message text
        """
        self.client.messages.create(
            from_=self.from_whatsapp, to=to_whatsapp, body=message
        )
        logger.info(f"Message sent to {to_whatsapp}")


# Global instance (optional, for convenience)
_bot_instance: Optional[WhatsAppBot] = None


def init_whatsapp_bot(
    account_sid: str,
    auth_token: str,
    from_whatsapp: str,
    backend_url: str = "http://localhost:8000",
) -> WhatsAppBot:
    """Initialize global WhatsApp bot instance."""
    global _bot_instance
    _bot_instance = WhatsAppBot(account_sid, auth_token, from_whatsapp, backend_url)
    return _bot_instance


def get_whatsapp_bot() -> Optional[WhatsAppBot]:
    """Get global WhatsApp bot instance."""
    return _bot_instance
