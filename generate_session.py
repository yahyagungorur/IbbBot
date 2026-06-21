"""
Run this script ONCE locally to generate your SESSION_STRING.
Copy the printed string and add it as the SESSION_STRING environment variable in Railway.
"""
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
import os

load_dotenv()

api_id = int(os.environ['API_ID'])
api_hash = os.environ['API_HASH']

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\n✅ Your SESSION_STRING (add this to Railway env vars):")
    print(client.session.save())
