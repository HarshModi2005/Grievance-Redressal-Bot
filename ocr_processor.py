"""
OCR Processing module for extracting text from images
"""
import pytesseract
from PIL import Image, ExifTags
import exifread
import logging
import re
import os
from typing import Dict, Optional, Tuple, List
from config import Config

class OCRProcessor:
    """Class for handling OCR operations and image text extraction"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Set Tesseract command path if configured
        if Config.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
        
        self.supported_languages = Config.OCR_LANGUAGES
        
        # Indian address patterns for location extraction
        self.address_patterns = [
            # Pin code pattern
            r'\b\d{6}\b',
            # Indian state patterns
            r'\b(?:Andhra Pradesh|Arunachal Pradesh|Assam|Bihar|Chhattisgarh|Goa|Gujarat|Haryana|Himachal Pradesh|Jharkhand|Karnataka|Kerala|Madhya Pradesh|Maharashtra|Manipur|Meghalaya|Mizoram|Nagaland|Odisha|Punjab|Rajasthan|Sikkim|Tamil Nadu|Telangana|Tripura|Uttar Pradesh|Uttarakhand|West Bengal|Delhi|Puducherry|Chandigarh|Dadra and Nagar Haveli|Daman and Diu|Lakshadweep|Jammu and Kashmir|Ladakh)\b',
            # Common Indian city/location terms
            r'\b(?:Road|Street|Lane|Gali|Marg|Nagar|Colony|Sector|Block|Phase|Plot|House|Building|Apartment|Society|Area|District|Taluka|Mandal|Ward|Village|Town|City)\b',
            # Address line patterns
            r'(?:Near|Opp|Behind|Front|Adjacent|Next to)\s+[\w\s]+',
        ]
        
    def extract_text_from_image(self, image_path: str, languages: Optional[List[str]] = None) -> Dict:
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image_path: Path to the image file
            languages: List of language codes for OCR (default: config languages)
            
        Returns:
            Dictionary containing extracted text and confidence
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Load and preprocess image
            image = Image.open(image_path)
            image = self._preprocess_image(image)
            
            # Use configured languages or provided ones
            lang_codes = '+'.join(languages or self.supported_languages)
            
            # Extract text with detailed information
            extracted_data = pytesseract.image_to_data(
                image, 
                lang=lang_codes, 
                output_type=pytesseract.Output.DICT
            )
            
            # Get raw text
            raw_text = pytesseract.image_to_string(image, lang=lang_codes)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in extracted_data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Clean and process text
            cleaned_text = self._clean_text(raw_text)
            
            self.logger.info(f"OCR extraction completed. Confidence: {avg_confidence:.2f}%")
            
            return {
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'confidence': avg_confidence,
                'word_count': len(cleaned_text.split()),
                'languages_used': lang_codes,
                'extraction_success': bool(cleaned_text.strip())
            }
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed for {image_path}: {e}")
            return {
                'raw_text': '',
                'cleaned_text': '',
                'confidence': 0,
                'word_count': 0,
                'languages_used': '+'.join(languages or self.supported_languages),
                'extraction_success': False,
                'error': str(e)
            }
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image object
        """
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Auto-rotate based on EXIF orientation
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                
                exif = image._getexif()
                if exif is not None:
                    orientation_value = exif.get(orientation)
                    if orientation_value == 3:
                        image = image.rotate(180, expand=True)
                    elif orientation_value == 6:
                        image = image.rotate(270, expand=True)
                    elif orientation_value == 8:
                        image = image.rotate(90, expand=True)
            except:
                pass
            
            # Resize if image is too large (for better processing speed)
            max_size = 2048
            if image.width > max_size or image.height > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            self.logger.warning(f"Image preprocessing failed: {e}")
            return image
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might be OCR artifacts
        text = re.sub(r'[^\w\s\.,\-\(\)\[\]/@#$%&*+=:;?!\'"]', '', text)
        
        # Fix common OCR mistakes for Indian text
        ocr_corrections = {
            '0': 'O',  # Zero to O in specific contexts
            '5': 'S',  # 5 to S in specific contexts
            '1': 'I',  # 1 to I in specific contexts
        }
        
        # Apply corrections cautiously
        for mistake, correction in ocr_corrections.items():
            # Only replace if it makes sense contextually
            pass  # Implement context-aware corrections if needed
        
        return text.strip()
    
    def extract_addresses_from_text(self, text: str) -> List[str]:
        """
        Extract potential addresses from text using regex patterns
        
        Args:
            text: Text to extract addresses from
            
        Returns:
            List of potential addresses
        """
        addresses = []
        
        try:
            for pattern in self.address_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Get surrounding context for better address extraction
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].strip()
                    
                    if context and context not in addresses:
                        addresses.append(context)
            
            # Remove duplicates and filter meaningful addresses
            filtered_addresses = []
            for addr in addresses:
                if len(addr.split()) >= 2:  # At least 2 words
                    filtered_addresses.append(addr)
            
            return filtered_addresses[:5]  # Return top 5 potential addresses
            
        except Exception as e:
            self.logger.error(f"Address extraction failed: {e}")
            return []
    
    def extract_gps_from_image(self, image_path: str) -> Optional[Tuple[float, float]]:
        """
        Extract GPS coordinates from image EXIF data
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                
                # Check for GPS data
                if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                    lat_ref = tags.get('GPS GPSLatitudeRef', 'N')
                    lat_values = tags['GPS GPSLatitude'].values
                    
                    lon_ref = tags.get('GPS GPSLongitudeRef', 'E')
                    lon_values = tags['GPS GPSLongitude'].values
                    
                    # Convert GPS coordinates
                    latitude = self._convert_gps_to_decimal(lat_values, str(lat_ref))
                    longitude = self._convert_gps_to_decimal(lon_values, str(lon_ref))
                    
                    if latitude is not None and longitude is not None:
                        self.logger.info(f"GPS coordinates extracted: {latitude}, {longitude}")
                        return (latitude, longitude)
                
            return None
            
        except Exception as e:
            self.logger.error(f"GPS extraction failed for {image_path}: {e}")
            return None
    
    def _convert_gps_to_decimal(self, values: List, ref: str) -> Optional[float]:
        """
        Convert GPS coordinates from degrees/minutes/seconds to decimal
        
        Args:
            values: GPS coordinate values
            ref: Reference (N/S for latitude, E/W for longitude)
            
        Returns:
            Decimal coordinate or None if conversion fails
        """
        try:
            degrees = float(values[0])
            minutes = float(values[1])
            seconds = float(values[2])
            
            decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            # Apply negative sign for South/West
            if ref.upper() in ['S', 'W']:
                decimal = -decimal
                
            return decimal
            
        except Exception as e:
            self.logger.error(f"GPS coordinate conversion failed: {e}")
            return None
    
    def validate_extracted_data(self, ocr_result: Dict) -> Dict:
        """
        Validate and provide feedback on OCR extraction quality
        
        Args:
            ocr_result: Result from extract_text_from_image
            
        Returns:
            Validation result with recommendations
        """
        validation = {
            'is_valid': False,
            'confidence_level': 'low',
            'recommendations': [],
            'has_useful_text': False
        }
        
        try:
            confidence = ocr_result.get('confidence', 0)
            text = ocr_result.get('cleaned_text', '')
            word_count = ocr_result.get('word_count', 0)
            
            # Confidence level assessment
            if confidence >= 80:
                validation['confidence_level'] = 'high'
            elif confidence >= 60:
                validation['confidence_level'] = 'medium'
            else:
                validation['confidence_level'] = 'low'
            
            # Check if text is useful
            if word_count >= 3 and len(text.strip()) >= 10:
                validation['has_useful_text'] = True
            
            # Overall validity
            validation['is_valid'] = (
                confidence >= 50 and 
                validation['has_useful_text'] and
                ocr_result.get('extraction_success', False)
            )
            
            # Generate recommendations
            if confidence < 60:
                validation['recommendations'].append(
                    "Image quality is low. Try taking a clearer, well-lit photo."
                )
            
            if word_count < 3:
                validation['recommendations'].append(
                    "Very little text detected. Ensure the image contains readable text."
                )
            
            if not validation['has_useful_text']:
                validation['recommendations'].append(
                    "No meaningful text found. Please share an image with visible text or details."
                )
            
            return validation
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            validation['recommendations'].append("Error processing image. Please try again.")
            return validation

# Global OCR processor instance
ocr_processor = OCRProcessor()

