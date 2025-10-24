import os

from typing import Optional
from dotenv import load_dotenv

from utilities.settings import bot

load_dotenv("token.env")
token: Optional[str] = os.getenv("TOKEN")
bot.run(token)