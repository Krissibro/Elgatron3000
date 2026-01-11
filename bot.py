import os

from typing import Optional
from dotenv import load_dotenv

from utilities.elgatron import Elgatron

bot = Elgatron()

load_dotenv("token.env")
token: Optional[str] = os.getenv("TOKEN")

if not token:
    raise ValueError("TOKEN not found in environment")

bot.run(token)