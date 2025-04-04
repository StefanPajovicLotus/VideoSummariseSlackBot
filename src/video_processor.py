import cv2
import tempfile
import os
import logging
import requests
from typing import List, Optional
import numpy as np

class VideoProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()

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

    def extract_frames(self, video_url: str, num_frames: int = 5) -> List[np.ndarray]:
        """Extract frames from video for analysis"""
        try:
            # Download video
            video_path = self.download_video(video_url)
            if not video_path:
                return []

            # Open video file
            cap = cv2.VideoCapture(video_path)
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_interval = total_frames // num_frames
            
            frames = []
            for i in range(num_frames):
                # Set frame position
                cap.set(cv2.CAP_PROP_POS_FRAMES, i * frame_interval)
                
                # Read frame
                ret, frame = cap.read()
                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
            
            cap.release()
            
            # Cleanup
            os.remove(video_path)
            
            return frames
            
        except Exception as e:
            logging.error(f"Error extracting frames: {e}")
            return [] 