import cv2
import tempfile
import os
import logging
import requests
import subprocess
from typing import List, Optional
import numpy as np
from PIL import Image
import shutil
from google import genai

class VideoProcessor:
    def __init__(self, api_key):
        self.temp_dir = tempfile.mkdtemp()
        self.api_key = api_key
        self.model_name = "gemini-2.5-pro-exp-03-25"
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')

    def download_video(self, video_url: str) -> Optional[str]:
        """Download video from Slack"""
        try:
            headers = {
                'Authorization': f'Bearer {os.environ.get("SLACK_BOT_TOKEN")}'
            }
            response = requests.get(video_url, headers=headers, stream=True)
            response.raise_for_status()
            
            video_path = os.path.join(self.temp_dir, "video.mp4")
            with open(video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return video_path
            
        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            return None

    def extract_frames(self, video_path: str, fps: int = 3) -> bool:
        """Extract frames from video at specified fps"""
        try:
            frames_dir = os.path.join(self.temp_dir, "frames")
            if not os.path.exists(frames_dir):
                os.makedirs(frames_dir)

            command = [
                "ffmpeg",
                "-i", video_path,
                "-vf", f"fps={fps}",
                os.path.join(frames_dir, "frame_%04d.png")
            ]
            subprocess.run(command, check=True)
            logging.info(f"Frames extracted successfully to {frames_dir}")
            return True

        except Exception as e:
            logging.error(f"Error extracting frames: {e}")
            return False

    def analyze_video(self, video_path: str, content_type: str = "bug") -> Optional[str]:
        """Analyze video content using extracted frames"""
        try:
            # Extract frames
            if not self.extract_frames(video_path):
                return None

            frames_dir = os.path.join(self.temp_dir, "frames")
            result = self.describe_video_content(frames_dir, content_type)

            # Cleanup
            self.cleanup()
            
            return result

        except Exception as e:
            logging.error(f"Error in video analysis: {e}")
            return None

    def describe_video_content(self, frames_dir: str, content_type: str = "bug") -> Optional[str]:
        """Analyze frames using Gemini Vision API"""
        try:
            image_files = sorted([f for f in os.listdir(frames_dir) 
                                if f.endswith((".png", ".jpg", ".jpeg"))])
            
            if not image_files:
                logging.error("No frames found for analysis")
                return None

            image_parts = []
            for image_file in image_files:
                try:
                    image_path = os.path.join(frames_dir, image_file)
                    pil_image = Image.open(image_path)
                    image_parts.append(pil_image)
                except Exception as e:
                    logging.error(f"Error processing frame {image_file}: {e}")

            if not image_parts:
                return None

            prompt = self._get_prompt(content_type)
            contents = [prompt, *image_parts]
            response = self.model.generate_content(contents)
            
            return response.text

        except Exception as e:
            logging.error(f"Error analyzing frames: {e}")
            return None

    def _get_prompt(self, content_type: str) -> str:
        """Returns appropriate prompt based on content type"""
        if content_type.lower() == "bug":
            return ("These images are frames extracted from a screen recording for QA testing. "
                   "Please provide a concise summary of the initial state, the key actions performed, "
                   "and any component-related flaws observed. Focus on UI components, navigation, "
                   "and state changes. Specifically, highlight any unexpected behavior, rendering issues, "
                   "or inconsistencies in the UI components' appearance or functionality. "
                   "Ignore any data-specific issues and focus solely on the UI and component interactions. "
                   "Highlight one flaw as a key issue (list it before everything else), and if there are others, "
                   "list them as possible issue. Format the entire output as a JSON response.")
        else:
            return ("This screen recording demonstrates a new feature. Please analyze the video frames "
                   "and provide a concise text summary describing the functionality being showcased. "
                   "Focus on the user's actions, the UI elements involved, and the overall purpose of the feature. "
                   "Clearly explain what the feature does and how it benefits the user. "
                   "Aim for a description suitable for a pull request, highlighting the key aspects "
                   "of the demonstrated functionality.")

    def cleanup(self):
        """Clean up temporary files"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logging.info("Cleaned up temporary files")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}") 