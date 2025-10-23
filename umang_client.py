"""
UMANG API Client for submitting grievances through official channels
"""
import requests
import json
import base64
import hashlib
import hmac
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from urllib.parse import urljoin
from config import Config

class UMANGApiClient:
    """Client for interacting with UMANG APIs for grievance submission"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = Config.UMANG_API_BASE_URL
        self.client_id = Config.UMANG_CLIENT_ID
        self.client_secret = Config.UMANG_CLIENT_SECRET
        
        # API endpoints
        self.endpoints = {
            'auth': '/oauth/token',
            'grievance_submit': '/cpgrams/grievance/submit',
            'grievance_status': '/cpgrams/grievance/status',
            'grievance_track': '/cpgrams/grievance/track',
            'departments': '/cpgrams/departments',
            'categories': '/cpgrams/categories'
        }
        
        # Session management
        self.access_token = None
        self.token_expires_at = None
        self.session = requests.Session()
        
        # Default headers
        self.session.headers.update({
            'User-Agent': 'GrievanceBot/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def authenticate(self) -> bool:
        """
        Authenticate with UMANG API using OAuth 2.0
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            if not self.client_id or not self.client_secret:
                self.logger.error("UMANG client credentials not configured")
                return False
            
            auth_url = urljoin(self.base_url, self.endpoints['auth'])
            
            # Prepare authentication request
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'cpgrams_write cpgrams_read'
            }
            
            # Make authentication request
            response = self.session.post(
                auth_url,
                data=auth_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
                
                # Calculate expiration time
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer
                
                # Update session headers
                self.session.headers['Authorization'] = f'Bearer {self.access_token}'
                
                self.logger.info("UMANG API authentication successful")
                return True
            else:
                self.logger.error(f"UMANG authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"UMANG authentication error: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """
        Check if current authentication is valid
        
        Returns:
            True if authenticated and token is valid
        """
        return (
            self.access_token is not None and
            self.token_expires_at is not None and
            datetime.now() < self.token_expires_at
        )
    
    def ensure_authenticated(self) -> bool:
        """
        Ensure valid authentication, refresh if needed
        
        Returns:
            True if authenticated successfully
        """
        if not self.is_authenticated():
            return self.authenticate()
        return True
    
    def submit_grievance(self, grievance_data: Dict) -> Dict:
        """
        Submit a grievance through UMANG/CPGRAMS API
        
        Args:
            grievance_data: Dictionary containing grievance information
            
        Returns:
            Dictionary containing submission result
        """
        try:
            if not self.ensure_authenticated():
                return {
                    'success': False,
                    'error': 'Authentication failed',
                    'reference_id': None
                }
            
            # Prepare grievance payload
            payload = self._prepare_grievance_payload(grievance_data)
            
            # Submit grievance
            submit_url = urljoin(self.base_url, self.endpoints['grievance_submit'])
            
            response = self.session.post(
                submit_url,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                
                submission_result = {
                    'success': True,
                    'reference_id': result.get('grievance_id') or result.get('reference_id'),
                    'tracking_number': result.get('tracking_number'),
                    'status': result.get('status', 'submitted'),
                    'message': result.get('message', 'Grievance submitted successfully'),
                    'expected_resolution_days': result.get('expected_resolution_days', 30),
                    'assigned_department': result.get('assigned_department'),
                    'submission_timestamp': datetime.now().isoformat()
                }
                
                self.logger.info(f"Grievance submitted successfully: {submission_result['reference_id']}")
                return submission_result
                
            else:
                error_msg = f"Submission failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'reference_id': None
                }
                
        except Exception as e:
            error_msg = f"Grievance submission error: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'reference_id': None
            }
    
    def _prepare_grievance_payload(self, grievance_data: Dict) -> Dict:
        """
        Prepare grievance data payload for UMANG API
        
        Args:
            grievance_data: Raw grievance data
            
        Returns:
            Formatted payload for API submission
        """
        try:
            # Map categories to CPGRAMS category codes
            category_mapping = {
                'roads': 'TRANSPORT_ROADS',
                'water': 'WATER_SANITATION',
                'electricity': 'POWER_ENERGY',
                'sanitation': 'HEALTH_SANITATION',
                'healthcare': 'HEALTH_MEDICAL',
                'education': 'EDUCATION',
                'transport': 'TRANSPORT_PUBLIC',
                'public_services': 'GOVT_SERVICES',
                'housing': 'URBAN_HOUSING',
                'food_safety': 'HEALTH_FOOD_SAFETY',
                'other': 'GENERAL'
            }
            
            # Priority mapping
            priority_mapping = {
                'high': 'HIGH',
                'medium': 'MEDIUM',
                'low': 'LOW'
            }
            
            payload = {
                'grievance': {
                    'subject': grievance_data.get('subject', 'Public Grievance'),
                    'description': grievance_data.get('description', ''),
                    'category': category_mapping.get(grievance_data.get('category'), 'GENERAL'),
                    'priority': priority_mapping.get(grievance_data.get('priority'), 'MEDIUM'),
                    'location': {
                        'address': grievance_data.get('location', ''),
                        'coordinates': {
                            'latitude': grievance_data.get('latitude'),
                            'longitude': grievance_data.get('longitude')
                        } if grievance_data.get('latitude') and grievance_data.get('longitude') else None,
                        'pincode': self._extract_pincode(grievance_data.get('location', '')),
                        'state': self._extract_state(grievance_data.get('location', '')),
                        'district': self._extract_district(grievance_data.get('location', ''))
                    },
                    'citizen': {
                        'name': grievance_data.get('citizen_name', 'Anonymous'),
                        'mobile': grievance_data.get('citizen_mobile'),
                        'email': grievance_data.get('citizen_email'),
                        'address': grievance_data.get('citizen_address')
                    },
                    'department_preference': grievance_data.get('department'),
                    'keywords': grievance_data.get('keywords', []),
                    'attachments': self._prepare_attachments(grievance_data.get('attachments', [])),
                    'source': 'TELEGRAM_BOT',
                    'submission_timestamp': datetime.now().isoformat(),
                    'language': 'en'  # Default to English, can be made configurable
                }
            }
            
            # Remove None values
            payload = self._clean_payload(payload)
            
            return payload
            
        except Exception as e:
            self.logger.error(f"Error preparing grievance payload: {e}")
            raise
    
    def _extract_pincode(self, location_text: str) -> Optional[str]:
        """Extract pincode from location text"""
        import re
        pincode_match = re.search(r'\b\d{6}\b', location_text)
        return pincode_match.group() if pincode_match else None
    
    def _extract_state(self, location_text: str) -> Optional[str]:
        """Extract state from location text"""
        states = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
            'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
            'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
            'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
            'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Delhi'
        ]
        
        location_lower = location_text.lower()
        for state in states:
            if state.lower() in location_lower:
                return state
        return None
    
    def _extract_district(self, location_text: str) -> Optional[str]:
        """Extract district from location text - basic implementation"""
        # This would need a comprehensive district database
        # For now, return None - can be enhanced later
        return None
    
    def _prepare_attachments(self, attachments: list) -> list:
        """
        Prepare attachment data for API submission
        
        Args:
            attachments: List of attachment file paths or data
            
        Returns:
            List of attachment objects for API
        """
        prepared_attachments = []
        
        try:
            for attachment in attachments:
                if isinstance(attachment, str):  # File path
                    try:
                        with open(attachment, 'rb') as f:
                            file_data = f.read()
                            file_b64 = base64.b64encode(file_data).decode('utf-8')
                            
                            prepared_attachments.append({
                                'filename': attachment.split('/')[-1],
                                'content_type': self._get_content_type(attachment),
                                'data': file_b64,
                                'size': len(file_data)
                            })
                    except Exception as e:
                        self.logger.error(f"Error preparing attachment {attachment}: {e}")
                
                elif isinstance(attachment, dict):  # Already prepared attachment
                    prepared_attachments.append(attachment)
            
            return prepared_attachments
            
        except Exception as e:
            self.logger.error(f"Error preparing attachments: {e}")
            return []
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension"""
        extension = filename.split('.')[-1].lower()
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain'
        }
        return content_types.get(extension, 'application/octet-stream')
    
    def _clean_payload(self, payload: Dict) -> Dict:
        """Remove None values from payload recursively"""
        if isinstance(payload, dict):
            return {k: self._clean_payload(v) for k, v in payload.items() if v is not None}
        elif isinstance(payload, list):
            return [self._clean_payload(item) for item in payload if item is not None]
        else:
            return payload
    
    def track_grievance(self, reference_id: str) -> Dict:
        """
        Track grievance status using reference ID
        
        Args:
            reference_id: Grievance reference ID
            
        Returns:
            Dictionary containing grievance status information
        """
        try:
            if not self.ensure_authenticated():
                return {
                    'success': False,
                    'error': 'Authentication failed',
                    'status': None
                }
            
            track_url = urljoin(self.base_url, self.endpoints['grievance_track'])
            params = {'reference_id': reference_id}
            
            response = self.session.get(track_url, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                return {
                    'success': True,
                    'reference_id': reference_id,
                    'status': result.get('status'),
                    'current_stage': result.get('current_stage'),
                    'assigned_officer': result.get('assigned_officer'),
                    'department': result.get('department'),
                    'last_updated': result.get('last_updated'),
                    'remarks': result.get('remarks'),
                    'expected_closure': result.get('expected_closure_date'),
                    'timeline': result.get('timeline', [])
                }
            else:
                error_msg = f"Tracking failed: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'status': None
                }
                
        except Exception as e:
            error_msg = f"Grievance tracking error: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'status': None
            }
    
    def get_departments(self) -> Dict:
        """
        Get list of available departments from CPGRAMS
        
        Returns:
            Dictionary containing department information
        """
        try:
            if not self.ensure_authenticated():
                return {
                    'success': False,
                    'error': 'Authentication failed',
                    'departments': []
                }
            
            dept_url = urljoin(self.base_url, self.endpoints['departments'])
            
            response = self.session.get(dept_url, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'departments': result.get('departments', [])
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to fetch departments: {response.status_code}",
                    'departments': []
                }
                
        except Exception as e:
            self.logger.error(f"Error fetching departments: {e}")
            return {
                'success': False,
                'error': str(e),
                'departments': []
            }
    
    def get_categories(self) -> Dict:
        """
        Get list of available complaint categories
        
        Returns:
            Dictionary containing category information
        """
        try:
            if not self.ensure_authenticated():
                return {
                    'success': False,
                    'error': 'Authentication failed',
                    'categories': []
                }
            
            cat_url = urljoin(self.base_url, self.endpoints['categories'])
            
            response = self.session.get(cat_url, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'categories': result.get('categories', [])
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to fetch categories: {response.status_code}",
                    'categories': []
                }
                
        except Exception as e:
            self.logger.error(f"Error fetching categories: {e}")
            return {
                'success': False,
                'error': str(e),
                'categories': []
            }

class MockUMANGClient(UMANGApiClient):
    """Mock UMANG client for testing and development"""
    
    def __init__(self):
        super().__init__()
        self.mock_reference_counter = 1000
        self.mock_grievances = {}
    
    def authenticate(self) -> bool:
        """Mock authentication - always succeeds"""
        self.access_token = "mock_access_token"
        self.token_expires_at = datetime.now() + timedelta(hours=1)
        self.logger.info("Mock UMANG authentication successful")
        return True
    
    def submit_grievance(self, grievance_data: Dict) -> Dict:
        """Mock grievance submission"""
        try:
            # Generate mock reference ID
            reference_id = f"MOCK-CPGRAMS-{self.mock_reference_counter:06d}"
            self.mock_reference_counter += 1
            
            # Store mock grievance
            self.mock_grievances[reference_id] = {
                'data': grievance_data,
                'status': 'UNDER_PROCESS',
                'submitted_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            result = {
                'success': True,
                'reference_id': reference_id,
                'tracking_number': f"TRK{reference_id[-6:]}",
                'status': 'submitted',
                'message': 'Mock grievance submitted successfully',
                'expected_resolution_days': 30,
                'assigned_department': grievance_data.get('department', 'Mock Department'),
                'submission_timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Mock grievance submitted: {reference_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Mock submission error: {e}")
            return {
                'success': False,
                'error': str(e),
                'reference_id': None
            }
    
    def track_grievance(self, reference_id: str) -> Dict:
        """Mock grievance tracking"""
        try:
            if reference_id in self.mock_grievances:
                mock_data = self.mock_grievances[reference_id]
                
                return {
                    'success': True,
                    'reference_id': reference_id,
                    'status': mock_data['status'],
                    'current_stage': 'Under Review',
                    'assigned_officer': 'Mock Officer',
                    'department': 'Mock Department',
                    'last_updated': mock_data['last_updated'],
                    'remarks': 'Grievance is being processed',
                    'expected_closure': (datetime.now() + timedelta(days=25)).isoformat(),
                    'timeline': [
                        {
                            'stage': 'Submitted',
                            'timestamp': mock_data['submitted_at'],
                            'remarks': 'Grievance submitted successfully'
                        },
                        {
                            'stage': 'Acknowledged',
                            'timestamp': mock_data['submitted_at'],
                            'remarks': 'Grievance acknowledged by department'
                        }
                    ]
                }
            else:
                return {
                    'success': False,
                    'error': 'Reference ID not found',
                    'status': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': None
            }

# Create appropriate client instance based on configuration
def create_umang_client() -> UMANGApiClient:
    """Create UMANG client instance (real or mock based on configuration)"""
    if Config.UMANG_CLIENT_ID and Config.UMANG_CLIENT_SECRET:
        return UMANGApiClient()
    else:
        return MockUMANGClient()

# Global UMANG client instance
umang_client = create_umang_client()

