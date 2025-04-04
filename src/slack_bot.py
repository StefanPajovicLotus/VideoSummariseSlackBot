from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
import logging
import google.generativeai as genai
from video_processor import VideoProcessor
import tempfile

class SlackBot:
    def __init__(self):
        self.app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
        
        # Configure Gemini
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize VideoProcessor
        self.video_processor = VideoProcessor(api_key=self.api_key)
        
        # Register event handlers
        self.app.event("message")(self.handle_message_events)
        self.app.event("file_shared")(self.handle_file_shared)

    def handle_message_events(self, body, say):
        """Handle regular messages"""
        try:
            if "text" in body["event"]:
                message = body["event"]["text"]
                response = self.model.generate_content(message)
                say(response.text,
                    thread_ts=body["event"].get("thread_ts", body["event"]["ts"]))
        
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            say("Sorry, I encountered an error processing your message.")

    def handle_file_shared(self, body, say, client):
        """Handle video file uploads"""
        try:
            event = body["event"]
            file_id = event.get("file_id")
            
            # Get file info
            file_info = client.files_info(file=file_id)["file"]
            
            # Check if it's a video file
            if not file_info["mimetype"].startswith("video/"):
                return
            
            # Download the file
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
                response = client.files_download(file=file_id)
                temp_file.write(response["body"])
                temp_path = temp_file.name

            try:
                # Analyze the video using VideoProcessor
                analysis = self.video_processor.analyze_video(
                    temp_path,
                    content_type="bug"  # or "feature" based on your needs
                )
                
                if analysis:
                    # Post the analysis as a reply
                    say(
                        text=f"Video Analysis:\n```{analysis}```",
                        thread_ts=event.get("thread_ts", event["ts"])
                    )
                else:
                    say(
                        text="Sorry, I couldn't analyze the video.",
                        thread_ts=event.get("thread_ts", event["ts"])
                    )
            
            finally:
                # Cleanup temporary video file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            logging.error(f"Error processing video: {e}")
            say(
                text="Sorry, I encountered an error processing the video.",
                thread_ts=event.get("thread_ts", event["ts"])
            )

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