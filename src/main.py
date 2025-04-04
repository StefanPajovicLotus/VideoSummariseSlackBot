#!/usr/bin/env python

import os
import sys
import logging
from dotenv import load_dotenv
from slack_bot import SlackBot

def handler(request):
    # Check if the app is running on Vercel
    if os.environ.get("VERCEL") == "1":
        return {
            "statusCode": 200,
            "body": "The app is running on Vercel!"
        }
    else:
        return {
            "statusCode": 200,
            "body": "The app is NOT running on Vercel."
        }
        
def setup_logging():
    kw = {
        'format': '[%(asctime)s] %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': logging.DEBUG,
        'stream': sys.stdout,
    }
    logging.basicConfig(**kw)

def main():
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    # Debug: Print environment variables (tokens will be partially hidden)
    bot_token = os.environ.get("SLACK_BOT_TOKEN", "Not found")
    app_token = os.environ.get("SLACK_APP_TOKEN", "Not found")
    api_key = os.environ.get("GOOGLE_API_KEY", "Not found")
    
    logging.debug(f"SLACK_BOT_TOKEN: {bot_token[:10]}...{bot_token[-4:] if len(bot_token)>14 else ''}")
    logging.debug(f"SLACK_APP_TOKEN: {app_token[:10]}...{app_token[-4:] if len(app_token)>14 else ''}")
    logging.debug(f"GOOGLE_API_KEY: {api_key[:10]}...{api_key[-4:] if len(api_key)>14 else ''}")
    
    # Initialize and start the bot
    bot = SlackBot()
    bot.start()

if __name__ == '__main__':
    main() 