"""
AI-powered Image Analysis module for understanding grievance images
Uses vision AI models to analyze images and extract meaningful information
"""
import os
import logging
import base64
import requests
from typing import Dict, Optional, List
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

from config import Config

class AIImageAnalyzer:
    """Class for AI-powered image analysis using vision models"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Get API keys from environment
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        
        # Determine which API to use
        self.use_openai = bool(self.openai_api_key)
        self.use_google = bool(self.google_api_key)
        
        if not self.use_openai and not self.use_google:
            self.logger.warning("No AI API keys configured. Using fallback OCR mode.")
    
    def analyze_grievance_image(self, image_path: str) -> Dict:
        """
        Analyze a grievance image using AI vision models
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Try OpenAI first, then Google, then fallback
            if self.use_openai:
                return self._analyze_with_openai(image_path)
            elif self.use_google:
                return self._analyze_with_google(image_path)
            else:
                return self._fallback_analysis(image_path)
                
        except Exception as e:
            self.logger.error(f"Image analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'description': '',
                'category': 'other',
                'severity': 'medium',
                'suggested_department': 'General',
                'key_issues': []
            }
    
    def _analyze_with_openai(self, image_path: str) -> Dict:
        """Analyze image using OpenAI GPT-4 Vision"""
        try:
            # Encode image to base64
            with open(image_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare the prompt for grievance analysis
            prompt = """Analyze this image for a public grievance submission system. Provide:

1. **Description**: Detailed description of what you see (infrastructure issues, problems, etc.)
2. **Category**: Classify into one of: roads, water, electricity, sanitation, healthcare, education, transport, other
3. **Severity**: Rate as low, medium, high, or critical
4. **Key Issues**: List 3-5 specific problems visible in the image
5. **Suggested Department**: Which government department should handle this
6. **Location Clues**: Any visible location information (street names, landmarks, signs)

Format your response as JSON with these exact keys: description, category, severity, key_issues (array), suggested_department, location_clues (array)"""

            # Call OpenAI API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            payload = {
                "model": "gpt-4o",  # or gpt-4-vision-preview
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON response
                import json
                try:
                    # Try to extract JSON from markdown code blocks if present
                    if '```json' in content:
                        content = content.split('```json')[1].split('```')[0].strip()
                    elif '```' in content:
                        content = content.split('```')[1].split('```')[0].strip()
                    
                    analysis = json.loads(content)
                except json.JSONDecodeError:
                    # If JSON parsing fails, create structured response from text
                    analysis = {
                        'description': content,
                        'category': 'other',
                        'severity': 'medium',
                        'key_issues': [],
                        'suggested_department': 'General',
                        'location_clues': []
                    }
                
                self.logger.info("OpenAI image analysis completed successfully")
                
                return {
                    'success': True,
                    'description': analysis.get('description', ''),
                    'category': analysis.get('category', 'other'),
                    'severity': analysis.get('severity', 'medium'),
                    'key_issues': analysis.get('key_issues', []),
                    'suggested_department': analysis.get('suggested_department', 'General'),
                    'location_clues': analysis.get('location_clues', []),
                    'ai_model': 'openai-gpt4-vision'
                }
            else:
                self.logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return self._fallback_analysis(image_path)
                
        except Exception as e:
            self.logger.error(f"OpenAI analysis failed: {e}")
            return self._fallback_analysis(image_path)
    
    def _analyze_with_google(self, image_path: str) -> Dict:
        """Analyze image using Google Gemini Vision"""
        try:
            # Encode image to base64
            with open(image_path, 'rb') as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare the prompt
            prompt = """Analyze this image for a public grievance submission system. Provide:

1. Description: Detailed description of what you see
2. Category: roads, water, electricity, sanitation, healthcare, education, transport, or other
3. Severity: low, medium, high, or critical
4. Key Issues: List specific problems visible
5. Suggested Department: Which government department should handle this
6. Location Clues: Any visible location information

Format as JSON with keys: description, category, severity, key_issues, suggested_department, location_clues"""

            # Call Google Gemini API
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.google_api_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Parse JSON response
                import json
                try:
                    if '```json' in content:
                        content = content.split('```json')[1].split('```')[0].strip()
                    elif '```' in content:
                        content = content.split('```')[1].split('```')[0].strip()
                    
                    analysis = json.loads(content)
                except json.JSONDecodeError:
                    analysis = {
                        'description': content,
                        'category': 'other',
                        'severity': 'medium',
                        'key_issues': [],
                        'suggested_department': 'General',
                        'location_clues': []
                    }
                
                self.logger.info("Google Gemini analysis completed successfully")
                
                return {
                    'success': True,
                    'description': analysis.get('description', ''),
                    'category': analysis.get('category', 'other'),
                    'severity': analysis.get('severity', 'medium'),
                    'key_issues': analysis.get('key_issues', []),
                    'suggested_department': analysis.get('suggested_department', 'General'),
                    'location_clues': analysis.get('location_clues', []),
                    'ai_model': 'google-gemini-vision'
                }
            else:
                self.logger.error(f"Google API error: {response.status_code} - {response.text}")
                return self._fallback_analysis(image_path)
                
        except Exception as e:
            self.logger.error(f"Google analysis failed: {e}")
            return self._fallback_analysis(image_path)
    
    def _fallback_analysis(self, image_path: str) -> Dict:
        """Fallback to basic OCR when AI APIs are not available"""
        try:
            from ocr_processor import ocr_processor
            
            self.logger.info("Using fallback OCR analysis")
            
            # Extract text using OCR
            ocr_result = ocr_processor.extract_text_from_image(image_path)
            text = ocr_result.get('cleaned_text', '')
            
            # Basic keyword-based categorization
            category = self._categorize_from_text(text)
            
            return {
                'success': True,
                'description': text if text else "Image uploaded. Please provide additional details.",
                'category': category,
                'severity': 'medium',
                'key_issues': [text[:100]] if text else [],
                'suggested_department': self._get_department_from_category(category),
                'location_clues': [],
                'ai_model': 'fallback-ocr',
                'note': 'Using basic OCR. For better analysis, configure OPENAI_API_KEY or GOOGLE_API_KEY'
            }
            
        except Exception as e:
            self.logger.error(f"Fallback analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'description': 'Unable to analyze image. Please provide manual description.',
                'category': 'other',
                'severity': 'medium',
                'key_issues': [],
                'suggested_department': 'General',
                'location_clues': []
            }
    
    def _categorize_from_text(self, text: str) -> str:
        """Categorize complaint based on text keywords"""
        text_lower = text.lower()
        
        categories = {
            'roads': ['road', 'highway', 'street', 'pothole', 'traffic', 'pavement'],
            'water': ['water', 'drainage', 'sewer', 'pipeline', 'supply', 'leak'],
            'electricity': ['power', 'electricity', 'light', 'transformer', 'outage', 'wire'],
            'sanitation': ['garbage', 'waste', 'cleaning', 'toilet', 'hygiene', 'dump'],
            'healthcare': ['hospital', 'clinic', 'doctor', 'medicine', 'health', 'medical'],
            'education': ['school', 'college', 'teacher', 'education', 'student', 'class'],
            'transport': ['bus', 'train', 'transport', 'station', 'vehicle', 'metro']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def _get_department_from_category(self, category: str) -> str:
        """Map category to government department"""
        department_map = {
            'roads': 'Public Works Department (PWD)',
            'water': 'Water Supply Department',
            'electricity': 'Electricity Board',
            'sanitation': 'Municipal Corporation - Sanitation',
            'healthcare': 'Health Department',
            'education': 'Education Department',
            'transport': 'Transport Department',
            'other': 'General Administration'
        }
        
        return department_map.get(category, 'General Administration')

# Global AI image analyzer instance
ai_image_analyzer = AIImageAnalyzer()
