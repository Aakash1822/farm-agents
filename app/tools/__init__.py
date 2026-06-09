from app.tools.price import get_price
from app.tools.pest import diagnose_pest
from app.tools.scheme import get_schemes

ALL_TOOLS = [get_price, diagnose_pest, get_schemes]

__all__ = ["get_price", "diagnose_pest", "get_schemes", "ALL_TOOLS"]