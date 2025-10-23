"""
Complaint Classification module for categorizing grievance types
"""
import re
import logging
from typing import Dict, List, Tuple, Optional
from collections import Counter
from config import Config

class ComplaintClassifier:
    """Class for classifying complaints into appropriate categories"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Expanded keyword mapping for Indian public grievances
        self.category_keywords = {
            'roads': {
                'primary': ['road', 'highway', 'street', 'pothole', 'traffic', 'bridge', 'flyover', 'underpass', 'signal', 'zebra crossing', 'divider', 'median', 'footpath', 'pavement', 'junction', 'intersection', 'roundabout', 'traffic jam', 'congestion'],
                'secondary': ['tar', 'cement', 'construction', 'repair', 'maintenance', 'broken', 'damaged', 'crack', 'accident', 'safety', 'speed breaker', 'rumble strip', 'lane', 'marking', 'signage', 'board', 'direction'],
                'hindi': ['sadak', 'marg', 'path', 'raasta', 'gaddha', 'kharab', 'toot', 'nirmaan']
            },
            'water': {
                'primary': ['water', 'drainage', 'sewer', 'pipeline', 'supply', 'tap', 'bore', 'well', 'tank', 'reservoir', 'pump', 'leak', 'overflow', 'blockage', 'contamination', 'quality'],
                'secondary': ['dirty', 'clean', 'pressure', 'connection', 'meter', 'bill', 'shortage', 'scarcity', 'flood', 'waterlogging', 'stagnant', 'mosquito', 'smell', 'odor'],
                'hindi': ['paani', 'pani', 'jal', 'nalka', 'nal', 'gandagi', 'saaf', 'kharab', 'leakage']
            },
            'electricity': {
                'primary': ['power', 'electricity', 'light', 'transformer', 'outage', 'blackout', 'pole', 'wire', 'cable', 'meter', 'bill', 'connection', 'voltage', 'current', 'supply'],
                'secondary': ['cut', 'failure', 'fluctuation', 'broken', 'hanging', 'dangerous', 'spark', 'short circuit', 'overload', 'fuse', 'mcb', 'switch', 'socket', 'energy'],
                'hindi': ['bijli', 'current', 'light', 'kharab', 'kat', 'band', 'nahi', 'problem']
            },
            'sanitation': {
                'primary': ['garbage', 'waste', 'cleaning', 'toilet', 'hygiene', 'dustbin', 'collection', 'dump', 'litter', 'sweeping', 'sanitation', 'public toilet', 'washroom', 'restroom'],
                'secondary': ['dirty', 'smell', 'stink', 'rats', 'flies', 'disease', 'health', 'unhygienic', 'disposal', 'segregation', 'compost', 'recycling', 'plastic', 'organic'],
                'hindi': ['safai', 'gandagi', 'kachra', 'kuda', 'ganda', 'saaf', 'toilet', 'badbu', 'smell']
            },
            'healthcare': {
                'primary': ['hospital', 'clinic', 'doctor', 'medicine', 'health', 'medical', 'treatment', 'patient', 'nurse', 'ambulance', 'emergency', 'pharmacy', 'dispensary'],
                'secondary': ['appointment', 'queue', 'waiting', 'staff', 'equipment', 'facility', 'service', 'care', 'consultation', 'diagnosis', 'surgery', 'bed', 'ward', 'icu'],
                'hindi': ['hospital', 'dawai', 'daktaar', 'doctor', 'ilaj', 'marij', 'bimari', 'health']
            },
            'education': {
                'primary': ['school', 'college', 'teacher', 'education', 'student', 'classroom', 'building', 'playground', 'library', 'laboratory', 'computer', 'books', 'uniform', 'fees'],
                'secondary': ['admission', 'exam', 'result', 'certificate', 'scholarship', 'transport', 'meal', 'nutrition', 'infrastructure', 'facility', 'staff', 'principal', 'management'],
                'hindi': ['school', 'college', 'teacher', 'padhai', 'bachcha', 'student', 'shiksha', 'pustak']
            },
            'transport': {
                'primary': ['bus', 'train', 'transport', 'station', 'vehicle', 'auto', 'rickshaw', 'taxi', 'metro', 'railway', 'platform', 'ticket', 'conductor', 'driver'],
                'secondary': ['route', 'schedule', 'timing', 'frequency', 'crowded', 'delay', 'fare', 'booking', 'reservation', 'waiting', 'queue', 'service', 'maintenance'],
                'hindi': ['bus', 'train', 'gaadi', 'station', 'ticket', 'safar', 'yatra', 'transport']
            },
            'public_services': {
                'primary': ['government', 'office', 'officer', 'clerk', 'document', 'certificate', 'license', 'permit', 'application', 'form', 'service', 'counter', 'queue', 'waiting'],
                'secondary': ['bribe', 'corruption', 'delay', 'harassment', 'rude', 'behavior', 'staff', 'procedure', 'process', 'system', 'online', 'portal', 'website'],
                'hindi': ['sarkaar', 'office', 'kaam', 'kagaz', 'certificate', 'mukhya', 'adhikari', 'babu']
            },
            'housing': {
                'primary': ['housing', 'flat', 'apartment', 'building', 'construction', 'builder', 'society', 'maintenance', 'lift', 'elevator', 'parking', 'security', 'guard'],
                'secondary': ['possession', 'handover', 'registry', 'payment', 'emi', 'loan', 'bank', 'facility', 'amenity', 'gym', 'club', 'garden', 'playground'],
                'hindi': ['ghar', 'makan', 'flat', 'building', 'society', 'maintenance', 'lift', 'security']
            },
            'food_safety': {
                'primary': ['food', 'restaurant', 'hotel', 'eatery', 'canteen', 'mess', 'catering', 'quality', 'hygiene', 'license', 'fssai', 'adulteration', 'poisoning'],
                'secondary': ['expired', 'stale', 'contaminated', 'insects', 'hair', 'dirt', 'unhygienic', 'kitchen', 'storage', 'preparation', 'serving', 'packaging'],
                'hindi': ['khana', 'bhojan', 'restaurant', 'hotel', 'safai', 'kharab', 'gandagi', 'quality']
            }
        }
        
        # Department mapping for CPGRAMS routing
        self.department_mapping = {
            'roads': ['Ministry of Road Transport & Highways', 'Public Works Department', 'Municipal Corporation'],
            'water': ['Ministry of Jal Shakti', 'Water Supply Department', 'Municipal Corporation'],
            'electricity': ['Ministry of Power', 'State Electricity Board', 'Power Distribution Company'],
            'sanitation': ['Ministry of Housing & Urban Affairs', 'Municipal Corporation', 'Waste Management Department'],
            'healthcare': ['Ministry of Health & Family Welfare', 'Health Department', 'Medical Services'],
            'education': ['Ministry of Education', 'Education Department', 'School Education'],
            'transport': ['Ministry of Road Transport & Highways', 'Transport Department', 'Railway Ministry'],
            'public_services': ['Department of Administrative Reforms', 'General Administration', 'Revenue Department'],
            'housing': ['Ministry of Housing & Urban Affairs', 'Housing Department', 'Urban Development'],
            'food_safety': ['Ministry of Health & Family Welfare', 'Food Safety Department', 'FSSAI']
        }
        
        # Priority levels for different complaint types
        self.priority_levels = {
            'roads': 'high',      # Safety issues
            'water': 'high',      # Essential service
            'electricity': 'high', # Essential service
            'sanitation': 'medium', # Health related
            'healthcare': 'high',   # Emergency services
            'education': 'medium',  # Long-term impact
            'transport': 'medium',  # Daily commute
            'public_services': 'low', # Administrative
            'housing': 'medium',    # Quality of life
            'food_safety': 'high'   # Health hazard
        }
    
    def classify_complaint(self, text: str, image_context: Dict = None) -> Dict:
        """
        Classify complaint text into appropriate category
        
        Args:
            text: Complaint text to classify
            image_context: Additional context from image analysis
            
        Returns:
            Dictionary containing classification results
        """
        classification_result = {
            'primary_category': 'other',
            'confidence_score': 0,
            'secondary_categories': [],
            'department_suggestions': [],
            'priority_level': 'low',
            'keywords_found': [],
            'category_scores': {}
        }
        
        try:
            if not text or not text.strip():
                return classification_result
            
            text_lower = text.lower()
            category_scores = {}
            all_keywords_found = []
            
            # Score each category based on keyword matches
            for category, keywords in self.category_keywords.items():
                score = 0
                category_keywords = []
                
                # Primary keywords (higher weight)
                for keyword in keywords.get('primary', []):
                    if keyword.lower() in text_lower:
                        score += 3
                        category_keywords.append(keyword)
                
                # Secondary keywords (medium weight)
                for keyword in keywords.get('secondary', []):
                    if keyword.lower() in text_lower:
                        score += 2
                        category_keywords.append(keyword)
                
                # Hindi/Local language keywords (medium weight)
                for keyword in keywords.get('hindi', []):
                    if keyword.lower() in text_lower:
                        score += 2.5
                        category_keywords.append(keyword)
                
                # Apply phrase matching for better context
                score += self._apply_phrase_matching(text_lower, category)
                
                category_scores[category] = score
                all_keywords_found.extend(category_keywords)
            
            # Sort categories by score
            sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Determine primary category
            if sorted_categories[0][1] > 0:
                primary_category = sorted_categories[0][0]
                confidence = min((sorted_categories[0][1] / max(len(text.split()) * 0.3, 1)) * 100, 100)
                
                classification_result.update({
                    'primary_category': primary_category,
                    'confidence_score': round(confidence, 2),
                    'priority_level': self.priority_levels.get(primary_category, 'low'),
                    'department_suggestions': self.department_mapping.get(primary_category, []),
                    'keywords_found': list(set(all_keywords_found))
                })
                
                # Add secondary categories (scores > 30% of primary)
                threshold = sorted_categories[0][1] * 0.3
                for category, score in sorted_categories[1:]:
                    if score > threshold and score > 0:
                        classification_result['secondary_categories'].append({
                            'category': category,
                            'score': score,
                            'departments': self.department_mapping.get(category, [])
                        })
            
            classification_result['category_scores'] = category_scores
            
            # Apply image context if available
            if image_context:
                classification_result = self._apply_image_context(classification_result, image_context)
            
            self.logger.info(f"Complaint classified as '{classification_result['primary_category']}' with confidence {classification_result['confidence_score']}")
            
            return classification_result
            
        except Exception as e:
            self.logger.error(f"Complaint classification failed: {e}")
            return classification_result
    
    def _apply_phrase_matching(self, text: str, category: str) -> float:
        """
        Apply phrase-based matching for better context understanding
        
        Args:
            text: Text to analyze
            category: Category to check against
            
        Returns:
            Additional score based on phrase matches
        """
        phrase_patterns = {
            'roads': [
                r'road.*(?:repair|fix|broken|pothole|damage)',
                r'traffic.*(?:jam|signal|light|problem)',
                r'bridge.*(?:broken|repair|construction)',
                r'highway.*(?:problem|issue|maintenance)'
            ],
            'water': [
                r'water.*(?:supply|problem|leak|dirty|contaminated)',
                r'drainage.*(?:block|overflow|problem)',
                r'pipe.*(?:burst|leak|broken)',
                r'tap.*(?:not.*work|no.*water|dry)'
            ],
            'electricity': [
                r'power.*(?:cut|outage|problem|failure)',
                r'electricity.*(?:bill|connection|problem)',
                r'light.*(?:not.*work|problem|flickering)',
                r'transformer.*(?:blast|problem|noise)'
            ],
            'sanitation': [
                r'garbage.*(?:collection|disposal|problem)',
                r'toilet.*(?:dirty|broken|not.*clean)',
                r'waste.*(?:management|disposal|collection)',
                r'cleaning.*(?:not.*done|poor|inadequate)'
            ]
        }
        
        score = 0
        patterns = phrase_patterns.get(category, [])
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 1.5
        
        return score
    
    def _apply_image_context(self, classification: Dict, image_context: Dict) -> Dict:
        """
        Apply image analysis context to improve classification
        
        Args:
            classification: Current classification result
            image_context: Context from image analysis (location, visual elements)
            
        Returns:
            Updated classification result
        """
        try:
            # If location context suggests a specific type of area
            location_info = image_context.get('location', {})
            if location_info:
                # Adjust based on location type
                if 'highway' in str(location_info).lower() or 'nh' in str(location_info).lower():
                    if classification['primary_category'] in ['other', 'roads']:
                        classification['primary_category'] = 'roads'
                        classification['confidence_score'] = min(classification['confidence_score'] + 15, 100)
                
                elif 'hospital' in str(location_info).lower() or 'clinic' in str(location_info).lower():
                    if classification['primary_category'] in ['other', 'healthcare']:
                        classification['primary_category'] = 'healthcare'
                        classification['confidence_score'] = min(classification['confidence_score'] + 15, 100)
            
            # Visual context (if available in future versions)
            visual_elements = image_context.get('visual_elements', [])
            for element in visual_elements:
                if element in ['road_sign', 'traffic_signal', 'vehicle']:
                    if classification['primary_category'] == 'other':
                        classification['primary_category'] = 'roads'
                        classification['confidence_score'] = min(classification['confidence_score'] + 10, 100)
                elif element in ['water_body', 'pipe', 'tap']:
                    if classification['primary_category'] == 'other':
                        classification['primary_category'] = 'water'
                        classification['confidence_score'] = min(classification['confidence_score'] + 10, 100)
            
            return classification
            
        except Exception as e:
            self.logger.error(f"Error applying image context: {e}")
            return classification
    
    def get_complaint_template(self, category: str) -> Dict:
        """
        Get structured template for specific complaint category
        
        Args:
            category: Complaint category
            
        Returns:
            Dictionary containing template information
        """
        templates = {
            'roads': {
                'required_fields': ['location', 'issue_type', 'severity'],
                'optional_fields': ['traffic_impact', 'safety_concern', 'duration'],
                'suggested_description': 'Please describe the road condition issue, exact location, and how it affects traffic or safety.',
                'urgency_indicators': ['accident prone', 'safety hazard', 'traffic jam', 'blocking road']
            },
            'water': {
                'required_fields': ['location', 'issue_type', 'duration'],
                'optional_fields': ['water_quality', 'supply_timing', 'pressure_issue'],
                'suggested_description': 'Please describe the water-related issue, location, and duration of the problem.',
                'urgency_indicators': ['no water supply', 'contaminated water', 'major leak', 'sewage overflow']
            },
            'electricity': {
                'required_fields': ['location', 'issue_type', 'duration'],
                'optional_fields': ['safety_concern', 'equipment_damage', 'frequency'],
                'suggested_description': 'Please describe the electrical issue, location, and duration of the problem.',
                'urgency_indicators': ['power outage', 'hanging wire', 'sparking', 'transformer issue']
            },
            'sanitation': {
                'required_fields': ['location', 'issue_type'],
                'optional_fields': ['health_impact', 'odor_level', 'frequency'],
                'suggested_description': 'Please describe the sanitation issue, location, and health impact if any.',
                'urgency_indicators': ['health hazard', 'disease outbreak', 'major spillage', 'pest infestation']
            }
        }
        
        default_template = {
            'required_fields': ['location', 'issue_type'],
            'optional_fields': ['description', 'impact'],
            'suggested_description': 'Please provide detailed description of the issue and its location.',
            'urgency_indicators': []
        }
        
        return templates.get(category, default_template)
    
    def suggest_improvements(self, text: str, classification: Dict) -> List[str]:
        """
        Suggest improvements to complaint text for better processing
        
        Args:
            text: Original complaint text
            classification: Classification results
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        try:
            # Check text length
            if len(text.split()) < 10:
                suggestions.append("Consider adding more details about the issue for better resolution.")
            
            # Check for location information
            if 'location' not in text.lower() and 'near' not in text.lower():
                suggestions.append("Include specific location details (area, landmark, or address).")
            
            # Check for urgency/severity
            urgency_words = ['urgent', 'emergency', 'immediately', 'asap', 'critical']
            if not any(word in text.lower() for word in urgency_words):
                if classification.get('priority_level') == 'high':
                    suggestions.append("Consider mentioning if this is an urgent matter requiring immediate attention.")
            
            # Check for timeline
            timeline_words = ['days', 'weeks', 'months', 'since', 'from', 'ongoing']
            if not any(word in text.lower() for word in timeline_words):
                suggestions.append("Mention when the problem started or how long it has been ongoing.")
            
            # Category-specific suggestions
            category = classification.get('primary_category', 'other')
            template = self.get_complaint_template(category)
            
            # Check for safety concerns in roads/electricity categories
            if category in ['roads', 'electricity'] and 'safety' not in text.lower():
                suggestions.append("Mention any safety concerns related to this issue.")
            
            # Check for health impact in sanitation/water categories
            if category in ['sanitation', 'water'] and 'health' not in text.lower():
                suggestions.append("Describe any health impact or concerns related to this issue.")
            
            return suggestions[:3]  # Return top 3 suggestions
            
        except Exception as e:
            self.logger.error(f"Error generating suggestions: {e}")
            return ["Please provide more details about the issue."]
    
    def format_for_submission(self, text: str, classification: Dict, location_info: Dict) -> Dict:
        """
        Format complaint for official submission
        
        Args:
            text: Complaint text
            classification: Classification results
            location_info: Location information
            
        Returns:
            Formatted complaint data for submission
        """
        try:
            formatted_complaint = {
                'subject': self._generate_subject(classification, location_info),
                'description': self._format_description(text, classification, location_info),
                'category': classification.get('primary_category', 'other'),
                'priority': classification.get('priority_level', 'low'),
                'department': classification.get('department_suggestions', [])[0] if classification.get('department_suggestions') else 'General Administration',
                'location': self._format_location(location_info),
                'keywords': classification.get('keywords_found', [])
            }
            
            return formatted_complaint
            
        except Exception as e:
            self.logger.error(f"Error formatting complaint for submission: {e}")
            return {
                'subject': 'Public Grievance',
                'description': text,
                'category': 'other',
                'priority': 'low',
                'department': 'General Administration',
                'location': 'Not specified',
                'keywords': []
            }
    
    def _generate_subject(self, classification: Dict, location_info: Dict) -> str:
        """Generate appropriate subject line for complaint"""
        category = classification.get('primary_category', 'other')
        location = location_info.get('final_address', 'Unspecified Location')
        
        # Keep location brief for subject
        if location and len(location) > 50:
            location_parts = location.split(',')
            location = location_parts[0] if location_parts else location[:47] + "..."
        
        subject_templates = {
            'roads': f"Road Infrastructure Issue - {location}",
            'water': f"Water Supply/Drainage Issue - {location}",
            'electricity': f"Power/Electrical Issue - {location}",
            'sanitation': f"Sanitation/Waste Management Issue - {location}",
            'healthcare': f"Healthcare Service Issue - {location}",
            'education': f"Education/School Issue - {location}",
            'transport': f"Public Transport Issue - {location}",
            'public_services': f"Government Service Issue - {location}",
            'housing': f"Housing/Building Issue - {location}",
            'food_safety': f"Food Safety Issue - {location}"
        }
        
        return subject_templates.get(category, f"Public Grievance - {location}")
    
    def _format_description(self, text: str, classification: Dict, location_info: Dict) -> str:
        """Format complaint description with structured information"""
        formatted_parts = []
        
        # Add classification info
        category = classification.get('primary_category', 'other').replace('_', ' ').title()
        formatted_parts.append(f"Category: {category}")
        
        # Add priority
        priority = classification.get('priority_level', 'low').title()
        formatted_parts.append(f"Priority Level: {priority}")
        
        # Add location details
        location = location_info.get('final_address')
        coordinates = location_info.get('final_coordinates')
        if location:
            formatted_parts.append(f"Location: {location}")
        if coordinates:
            lat, lon = coordinates
            formatted_parts.append(f"GPS Coordinates: {lat:.6f}, {lon:.6f}")
        
        # Add main complaint text
        formatted_parts.append("\nComplaint Details:")
        formatted_parts.append(text)
        
        # Add keywords for reference
        keywords = classification.get('keywords_found', [])
        if keywords:
            formatted_parts.append(f"\nRelevant Keywords: {', '.join(keywords[:10])}")
        
        return '\n'.join(formatted_parts)
    
    def _format_location(self, location_info: Dict) -> str:
        """Format location information for submission"""
        location = location_info.get('final_address', 'Not specified')
        method = location_info.get('method_used', 'unknown')
        confidence = location_info.get('confidence', 'low')
        
        location_text = location
        if method != 'unknown':
            location_text += f" (Detected via: {method}, Confidence: {confidence})"
        
        return location_text

# Global complaint classifier instance
complaint_classifier = ComplaintClassifier()

