import os
from dotenv import load_dotenv

# Load environment variables from .env file
# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config:
    SMARTAPI_API_KEY = os.getenv("SMARTAPI_API_KEY")
    SMARTAPI_CLIENT_ID = os.getenv("SMARTAPI_CLIENT_ID")
    SMARTAPI_MPIN = os.getenv("SMARTAPI_MPIN")
    SMARTAPI_TOTP_SECRET = os.getenv("SMARTAPI_TOTP_SECRET")
    
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    @classmethod
    def validate(cls):
        """Check if all required variables are set."""
        required_vars = [
            "SMARTAPI_API_KEY", "SMARTAPI_CLIENT_ID", "SMARTAPI_MPIN", 
            "SMARTAPI_TOTP_SECRET", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"
        ]
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

# Validate on import to ensure fail-fast behavior
# Config.validate() # Optional: Uncomment if you want strict validation on startup
