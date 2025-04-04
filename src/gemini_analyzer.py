import google.generativeai as genai
import os
import logging
from typing import List
import numpy as np
from PIL import Image
import io

class GeminiAnalyzer:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro-vision')

    def _prepare_frame(self, frame: np.ndarray) -> Image.Image:
        """Convert numpy array to PIL Image"""
        return Image.fromarray(frame)

    def analyze_frames(self, frames: List[np.ndarray]) -> str:
        """Analyze video frames using Gemini"""
        try:
            if not frames:
                return "No frames available for analysis"

            # Convert frames to PIL Images
            pil_frames = [self._prepare_frame(frame) for frame in frames]
            
            # Analyze frames with Gemini
            response = self.model.generate_content([
                "Analyze these key frames from a video and provide a summary of what's happening. " +
                "Focus on the main events and important details. Be concise but informative.",
                *pil_frames
            ])
            
            return response.text
            
        except Exception as e:
            logging.error(f"Error analyzing frames with Gemini: {e}")
            return "Sorry, I encountered an error analyzing the video." 