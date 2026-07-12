import os

from dotenv import load_dotenv

from app.core.elgatron import Elgatron


def main():
    load_dotenv(".env")

    token: str | None = os.getenv("TOKEN")
    if not token:
        raise ValueError("TOKEN not found in environment")

    bot = Elgatron()
    bot.run(token)


if __name__ == "__main__":
    main()
