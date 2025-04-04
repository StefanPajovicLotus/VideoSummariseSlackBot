from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
import logging
import google.generativeai as genai

class SlackBot:
    def __init__(self):
        self.app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
        
        # Configure Gemini
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Register event handlers
        self.app.event("message")(self.handle_message_events)

    def handle_message_events(self, body, say):
        """Handle incoming messages"""
        try:
            # Get the message text
            if "text" in body["event"]:
                message = body["event"]["text"]
                
                # Generate response using Gemini
                response = self.model.generate_content(message)
                
                # Post response as a reply
                say(response.text,
                    thread_ts=body["event"].get("thread_ts", body["event"]["ts"]))
        
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            say("Sorry, I encountered an error processing your message.")

    def start(self):
        """Start the Slack bot"""
        try:
            handler = SocketModeHandler(
                app=self.app, 
                app_token=os.environ.get("SLACK_APP_TOKEN")
            )
            handler.start()
        except Exception as e:
            logging.error(f"Error starting bot: {e}")
            raise 