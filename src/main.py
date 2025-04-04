#!/usr/bin/env python

import os
import sys
import logging
from dotenv import load_dotenv
from slack_bot import SlackBot

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
    
    # Initialize and start the bot
    bot = SlackBot()
    bot.start()

if __name__ == '__main__':
    main() 