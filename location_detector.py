"""
Location Detection module for multi-method location identification
"""
import re
import logging
from typing import Dict, Optional, Tuple, List
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import json

class LocationDetector:
    """Class for detecting and validating location information"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.geocoder = Nominatim(user_agent="grievance_bot", timeout=10)
        
        # Indian location patterns
        self.location_patterns = {
            'pincode': r'\b\d{6}\b',
            'states': r'\b(?:Andhra Pradesh|AP|Arunachal Pradesh|Assam|Bihar|Chhattisgarh|CG|Goa|Gujarat|GJ|Haryana|HR|Himachal Pradesh|HP|Jharkhand|JH|Karnataka|KA|Kerala|KL|Madhya Pradesh|MP|Maharashtra|MH|Manipur|MN|Meghalaya|ML|Mizoram|MZ|Nagaland|NL|Odisha|OR|Punjab|PB|Rajasthan|RJ|Sikkim|SK|Tamil Nadu|TN|Telangana|TS|Tripura|TR|Uttar Pradesh|UP|Uttarakhand|UK|West Bengal|WB|Delhi|DL|NCR|Puducherry|PY|Chandigarh|CH|Dadra and Nagar Haveli|DN|Daman and Diu|DD|Lakshadweep|LD|Jammu and Kashmir|JK|Ladakh|LA)\b',
            'cities': r'\b(?:Mumbai|Delhi|Bangalore|Bengaluru|Hyderabad|Ahmedabad|Chennai|Kolkata|Pune|Jaipur|Lucknow|Kanpur|Nagpur|Indore|Thane|Bhopal|Visakhapatnam|Vadodara|Firozabad|Ludhiana|Rajkot|Agra|Siliguri|Nashik|Faridabad|Patiala|Ghaziabad|Kalyan|Dombivali|Howrah|Ranchi|Allahabad|Coimbatore|Jabalpur|Gwalior|Vijayawada|Jodhpur|Madurai|Raipur|Kota|Chandigarh|Guwahati|Solapur|Hubballi|Dharwad|Tiruchirappalli|Salem|Meerut|Thiruvananthapuram|Bhiwandi|Saharanpur|Gorakhpur|Guntur|Bikaner|Amravati|Noida|Jamshedpur|Bhilai|Warangal|Cuttack|Firozabad|Kochi|Bhavnagar|Dehradun|Durgapur|Asansol|Nanded|Kolhapur|Ajmer|Akola|Gulbarga|Jamnagar|Ujjain|Loni|Siliguri|Jhansi|Ulhasnagar|Nellore|Jammu|Sangli|Miraj|Kupwad|Belgaum|Mangalore|Ambattur|Tirunelveli|Malegaon|Gaya|Jalgaon|Udaipur|Maheshtala)\b',
            'address_keywords': r'\b(?:Road|Street|Lane|Gali|Marg|Path|Cross|Main|Ring|Bypass|Highway|NH|SH|Avenue|Park|Garden|Square|Circle|Chowk|Gate|Nagar|Colony|Sector|Block|Phase|Plot|House|Building|Apartment|Flat|Society|Complex|Enclave|Layout|Extension|Area|Zone|District|Taluka|Mandal|Ward|Village|Town|City|Market|Bazaar|Mall|Station|Airport|Port|Bridge|Temple|Mosque|Church|School|College|Hospital|Clinic|Bank|Office|Government|Municipal|Corporation|Panchayat)\b',
            'landmarks': r'\b(?:Near|Opp|Opposite|Behind|Front|Adjacent|Next to|Beside|Close to|Around|At|Before|After)\s+[\w\s]{1,50}\b'
        }
        
        # Major Indian cities with their coordinates (for validation)
        self.major_cities = {
            'mumbai': (19.0760, 72.8777),
            'delhi': (28.7041, 77.1025),
            'bangalore': (12.9716, 77.5946),
            'bengaluru': (12.9716, 77.5946),
            'hyderabad': (17.3850, 78.4867),
            'ahmedabad': (23.0225, 72.5714),
            'chennai': (13.0827, 80.2707),
            'kolkata': (22.5726, 88.3639),
            'pune': (18.5204, 73.8567),
            'jaipur': (26.9124, 75.7873),
            'lucknow': (26.8467, 80.9462),
            'kanpur': (26.4499, 80.3319),
            'nagpur': (21.1458, 79.0882),
            'indore': (22.7196, 75.8577),
            'thane': (19.2183, 72.9781),
            'bhopal': (23.2599, 77.4126),
            'visakhapatnam': (17.6868, 83.2185),
            'vadodara': (22.3072, 73.1812),
            'ghaziabad': (28.6692, 77.4538),
            'ludhiana': (30.9010, 75.8573),
            'agra': (27.1767, 78.0081),
            'nashik': (19.9975, 73.7898),
            'faridabad': (28.4089, 77.3178),
            'rajkot': (22.3039, 70.8022),
            'meerut': (28.9845, 77.7064),
            'kalyan': (19.2437, 73.1355),
            'dombivali': (19.2183, 73.0869),
            'howrah': (22.5958, 88.2636),
            'ranchi': (23.3441, 85.3096),
            'allahabad': (25.4358, 81.8463),
            'coimbatore': (11.0168, 76.9558),
            'jabalpur': (23.1815, 79.9864),
            'gwalior': (26.2183, 78.1828)
        }
    
    def detect_location_from_text(self, text: str) -> Dict:
        """
        Detect location information from extracted text
        
        Args:
            text: Text to analyze for location information
            
        Returns:
            Dictionary containing detected location information
        """
        location_data = {
            'addresses': [],
            'pincode': None,
            'state': None,
            'city': None,
            'landmarks': [],
            'confidence_score': 0,
            'raw_matches': {}
        }
        
        try:
            text_lower = text.lower()
            
            # Extract pincodes
            pincode_matches = re.findall(self.location_patterns['pincode'], text)
            if pincode_matches:
                # Validate Indian pincode range (110001-855126)
                valid_pincodes = [p for p in pincode_matches if 110001 <= int(p) <= 855126]
                if valid_pincodes:
                    location_data['pincode'] = valid_pincodes[0]
                    location_data['confidence_score'] += 30
                    location_data['raw_matches']['pincode'] = valid_pincodes
            
            # Extract states
            state_matches = re.findall(self.location_patterns['states'], text, re.IGNORECASE)
            if state_matches:
                location_data['state'] = state_matches[0]
                location_data['confidence_score'] += 25
                location_data['raw_matches']['states'] = state_matches
            
            # Extract cities
            city_matches = re.findall(self.location_patterns['cities'], text, re.IGNORECASE)
            if city_matches:
                location_data['city'] = city_matches[0]
                location_data['confidence_score'] += 25
                location_data['raw_matches']['cities'] = city_matches
            
            # Extract address keywords and construct potential addresses
            address_keywords = re.findall(self.location_patterns['address_keywords'], text, re.IGNORECASE)
            if address_keywords:
                location_data['confidence_score'] += 10
                location_data['raw_matches']['address_keywords'] = address_keywords
            
            # Extract landmarks
            landmark_matches = re.findall(self.location_patterns['landmarks'], text, re.IGNORECASE)
            if landmark_matches:
                location_data['landmarks'] = landmark_matches[:3]  # Top 3 landmarks
                location_data['confidence_score'] += 10
                location_data['raw_matches']['landmarks'] = landmark_matches
            
            # Construct potential full addresses
            potential_addresses = self._construct_addresses(text, location_data)
            location_data['addresses'] = potential_addresses
            
            # Normalize confidence score (0-100)
            location_data['confidence_score'] = min(location_data['confidence_score'], 100)
            
            self.logger.info(f"Location detection completed. Confidence: {location_data['confidence_score']}")
            return location_data
            
        except Exception as e:
            self.logger.error(f"Location detection failed: {e}")
            return location_data
    
    def _construct_addresses(self, text: str, location_data: Dict) -> List[str]:
        """
        Construct potential full addresses from detected location components
        
        Args:
            text: Original text
            location_data: Detected location components
            
        Returns:
            List of potential addresses
        """
        addresses = []
        
        try:
            # Split text into sentences/lines for address extraction
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            sentences = [sent.strip() for sent in text.split('.') if sent.strip()]
            
            # Combine lines and sentences for analysis
            text_segments = list(set(lines + sentences))
            
            for segment in text_segments:
                segment = segment.strip()
                if len(segment) < 10 or len(segment) > 200:  # Skip very short or very long segments
                    continue
                
                # Check if segment contains location indicators
                location_indicators = 0
                segment_lower = segment.lower()
                
                # Check for address keywords
                for pattern_name, pattern in self.location_patterns.items():
                    if re.search(pattern, segment, re.IGNORECASE):
                        location_indicators += 1
                
                # Check for numbers (house numbers, sector numbers, etc.)
                if re.search(r'\b\d+\b', segment):
                    location_indicators += 1
                
                # If segment has enough location indicators, consider it an address
                if location_indicators >= 2:
                    addresses.append(segment)
            
            # Remove duplicates and sort by length (longer addresses first)
            unique_addresses = list(set(addresses))
            unique_addresses.sort(key=len, reverse=True)
            
            return unique_addresses[:5]  # Return top 5 potential addresses
            
        except Exception as e:
            self.logger.error(f"Address construction failed: {e}")
            return []
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates using geocoding
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            # Add "India" to the query for better results
            search_query = f"{address}, India"
            
            location = self.geocoder.geocode(search_query)
            if location:
                lat, lon = location.latitude, location.longitude
                
                # Validate coordinates are within India bounds
                if self._is_in_india(lat, lon):
                    self.logger.info(f"Geocoded address '{address}' to {lat}, {lon}")
                    return (lat, lon)
                else:
                    self.logger.warning(f"Geocoded location outside India bounds: {lat}, {lon}")
            
            return None
            
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            self.logger.error(f"Geocoding service error for '{address}': {e}")
            return None
        except Exception as e:
            self.logger.error(f"Geocoding failed for '{address}': {e}")
            return None
    
    def _is_in_india(self, lat: float, lon: float) -> bool:
        """
        Check if coordinates are within India's boundaries
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            True if coordinates are in India
        """
        # Approximate India bounding box
        india_bounds = {
            'lat_min': 6.0,
            'lat_max': 37.0,
            'lon_min': 68.0,
            'lon_max': 98.0
        }
        
        return (
            india_bounds['lat_min'] <= lat <= india_bounds['lat_max'] and
            india_bounds['lon_min'] <= lon <= india_bounds['lon_max']
        )
    
    def validate_coordinates(self, lat: float, lon: float) -> Dict:
        """
        Validate GPS coordinates and provide context
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Validation result with location context
        """
        validation = {
            'is_valid': False,
            'is_in_india': False,
            'nearest_city': None,
            'estimated_location': None,
            'accuracy': 'unknown'
        }
        
        try:
            # Basic coordinate validation
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                return validation
            
            validation['is_valid'] = True
            validation['is_in_india'] = self._is_in_india(lat, lon)
            
            if validation['is_in_india']:
                # Find nearest major city
                min_distance = float('inf')
                nearest_city = None
                
                for city, (city_lat, city_lon) in self.major_cities.items():
                    distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
                    if distance < min_distance:
                        min_distance = distance
                        nearest_city = city
                
                validation['nearest_city'] = nearest_city
                
                # Estimate accuracy based on distance to nearest major city
                if min_distance < 0.1:  # Very close to major city
                    validation['accuracy'] = 'high'
                elif min_distance < 0.5:  # Within metropolitan area
                    validation['accuracy'] = 'medium'
                else:  # Far from major cities
                    validation['accuracy'] = 'low'
                
                # Try reverse geocoding for location context
                try:
                    location = self.geocoder.reverse((lat, lon), timeout=5)
                    if location:
                        validation['estimated_location'] = location.address
                except:
                    pass
            
            return validation
            
        except Exception as e:
            self.logger.error(f"Coordinate validation failed: {e}")
            return validation
    
    def get_manual_location_prompts(self) -> Dict:
        """
        Get prompts for manual location input
        
        Returns:
            Dictionary with location input prompts
        """
        return {
            'address_prompt': (
                "📍 Please provide the location details:\n\n"
                "You can share:\n"
                "• Complete address\n"
                "• Area name with pincode\n"
                "• Landmark with nearby area\n"
                "• Your location (if issue is at your current location)\n\n"
                "Example: 'Near XYZ Mall, ABC Nagar, Mumbai 400001'"
            ),
            'location_button_text': "📍 Share Current Location",
            'skip_location_text': "⏭️ Skip Location (I'll add it in complaint description)",
            'validation_failed_text': (
                "❌ Could not validate this location. Please check and try again, or skip if you'll add location details in the complaint description."
            )
        }
    
    def combine_location_methods(self, gps_coords: Optional[Tuple[float, float]], 
                               text_location: Dict, manual_address: str = None) -> Dict:
        """
        Combine results from multiple location detection methods
        
        Args:
            gps_coords: GPS coordinates from image metadata
            text_location: Location data from OCR text
            manual_address: Manually provided address
            
        Returns:
            Combined location information
        """
        combined = {
            'final_coordinates': None,
            'final_address': None,
            'confidence': 'low',
            'sources': [],
            'method_used': 'none'
        }
        
        try:
            # Priority order: GPS > Manual > OCR text
            
            # 1. Try GPS coordinates first
            if gps_coords:
                lat, lon = gps_coords
                gps_validation = self.validate_coordinates(lat, lon)
                
                if gps_validation['is_valid'] and gps_validation['is_in_india']:
                    combined['final_coordinates'] = gps_coords
                    combined['final_address'] = gps_validation.get('estimated_location')
                    combined['confidence'] = 'high'
                    combined['sources'].append('gps_metadata')
                    combined['method_used'] = 'gps'
                    
                    self.logger.info("Using GPS coordinates as primary location source")
                    return combined
            
            # 2. Try manual address if provided
            if manual_address and manual_address.strip():
                manual_coords = self.geocode_address(manual_address)
                if manual_coords:
                    combined['final_coordinates'] = manual_coords
                    combined['final_address'] = manual_address
                    combined['confidence'] = 'high'
                    combined['sources'].append('manual_input')
                    combined['method_used'] = 'manual'
                    
                    self.logger.info("Using manual address as primary location source")
                    return combined
                else:
                    # Manual address provided but couldn't geocode
                    combined['final_address'] = manual_address
                    combined['confidence'] = 'medium'
                    combined['sources'].append('manual_input')
                    combined['method_used'] = 'manual'
            
            # 3. Try OCR-detected addresses
            if text_location.get('addresses'):
                best_address = None
                best_coords = None
                
                for address in text_location['addresses']:
                    coords = self.geocode_address(address)
                    if coords:
                        best_address = address
                        best_coords = coords
                        break
                
                if best_coords:
                    combined['final_coordinates'] = best_coords
                    combined['final_address'] = best_address
                    combined['confidence'] = 'medium'
                    combined['sources'].append('ocr_text')
                    combined['method_used'] = 'ocr'
                    
                    self.logger.info("Using OCR-detected address as location source")
                    return combined
            
            # 4. Fall back to partial location data from OCR
            if text_location.get('pincode') or text_location.get('city'):
                fallback_address = []
                if text_location.get('city'):
                    fallback_address.append(text_location['city'])
                if text_location.get('state'):
                    fallback_address.append(text_location['state'])
                if text_location.get('pincode'):
                    fallback_address.append(text_location['pincode'])
                
                if fallback_address:
                    combined['final_address'] = ', '.join(fallback_address)
                    combined['confidence'] = 'low'
                    combined['sources'].append('ocr_partial')
                    combined['method_used'] = 'ocr_partial'
                    
                    # Try to geocode the partial address
                    partial_coords = self.geocode_address(combined['final_address'])
                    if partial_coords:
                        combined['final_coordinates'] = partial_coords
                        combined['confidence'] = 'medium'
            
            return combined
            
        except Exception as e:
            self.logger.error(f"Location combination failed: {e}")
            return combined

# Global location detector instance
location_detector = LocationDetector()

