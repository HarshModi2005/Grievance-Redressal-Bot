"""
Department Identifier for CPGRAMS Integration
Identifies the correct government department and API endpoint for complaints
"""
import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class DepartmentLevel(Enum):
    """Department hierarchy levels"""
    CENTRAL = "central"
    STATE = "state"
    DISTRICT = "district"
    LOCAL = "local"

@dataclass
class DepartmentInfo:
    """Information about a government department"""
    name: str
    code: str
    level: DepartmentLevel
    cpgrams_endpoint: str
    ministry_parent: Optional[str] = None
    description: str = ""
    keywords: List[str] = None
    priority_score: float = 0.0
    contact_info: Dict[str, str] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.contact_info is None:
            self.contact_info = {}

class DepartmentIdentifier:
    """
    Identifies the most appropriate government department for a complaint
    based on AI analysis and keyword matching
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_departments()
    
    def _initialize_departments(self):
        """Initialize comprehensive department database"""
        
        # Central Government Departments
        self.departments = {
            # Roads and Transportation
            "MORTH": DepartmentInfo(
                name="Ministry of Road Transport & Highways",
                code="MORTH",
                level=DepartmentLevel.CENTRAL,
                cpgrams_endpoint="/cpgrams/departments/MORTH/submit",
                description="National highways, road transport policy, vehicle regulations",
                keywords=[
                    "national highway", "nh", "state highway", "expressway", "toll", "overbridge",
                    "underpass", "flyover", "road transport", "vehicle registration", "driving license",
                    "road safety", "highway construction", "road maintenance", "traffic rules",
                    "motor vehicle", "transport policy", "road infrastructure"
                ],
                priority_score=8.5,
                contact_info={
                    "website": "https://morth.nic.in",
                    "helpline": "1033",
                    "email": "feedback-morth@gov.in"
                }
            ),
            
            # Water Resources
            "MOJS": DepartmentInfo(
                name="Ministry of Jal Shakti",
                code="MOJS", 
                level=DepartmentLevel.CENTRAL,
                cpgrams_endpoint="/cpgrams/departments/MOJS/submit",
                description="Water supply, irrigation, river development, groundwater",
                keywords=[
                    "water supply", "drinking water", "irrigation", "groundwater", "river",
                    "dam", "reservoir", "canal", "water quality", "water treatment",
                    "bore well", "hand pump", "water scarcity", "drought", "flood control",
                    "watershed", "rainwater harvesting", "water conservation", "river cleaning"
                ],
                priority_score=9.0,
                contact_info={
                    "website": "https://jalshakti.gov.in",
                    "helpline": "1916",
                    "email": "secy-mowr@nic.in"
                }
            ),
            
            # Power and Electricity
            "MOP": DepartmentInfo(
                name="Ministry of Power",
                code="MOP",
                level=DepartmentLevel.CENTRAL,
                cpgrams_endpoint="/cpgrams/departments/MOP/submit",
                description="Electricity generation, transmission, distribution, renewable energy",
                keywords=[
                    "electricity", "power", "transformer", "power cut", "load shedding",
                    "electric pole", "high tension", "low tension", "power supply",
                    "electricity bill", "meter", "solar", "renewable energy", "grid",
                    "substation", "electric wire", "power outage", "voltage fluctuation"
                ],
                priority_score=8.8,
                contact_info={
                    "website": "https://powermin.gov.in",
                    "helpline": "1912",
                    "email": "powermin@gov.in"
                }
            ),
            
            # Urban Development
            "MOHUA": DepartmentInfo(
                name="Ministry of Housing & Urban Affairs",
                code="MOHUA",
                level=DepartmentLevel.CENTRAL,
                cpgrams_endpoint="/cpgrams/departments/MOHUA/submit",
                description="Urban planning, smart cities, housing, sanitation",
                keywords=[
                    "smart city", "urban development", "housing", "slum", "sanitation",
                    "sewerage", "solid waste", "garbage", "municipal", "city planning",
                    "urban infrastructure", "affordable housing", "pmay", "swachh bharat",
                    "waste management", "urban transport", "metro", "bus rapid transit"
                ],
                priority_score=8.2,
                contact_info={
                    "website": "https://mohua.gov.in",
                    "helpline": "14434",
                    "email": "mohua@gov.in"
                }
            ),
            
            # Health and Family Welfare
            "MOHFW": DepartmentInfo(
                name="Ministry of Health & Family Welfare",
                code="MOHFW",
                level=DepartmentLevel.CENTRAL,
                cpgrams_endpoint="/cpgrams/departments/MOHFW/submit",
                description="Public health, hospitals, medical services, disease control",
                keywords=[
                    "hospital", "health center", "phc", "chc", "medical", "doctor",
                    "medicine", "vaccine", "immunization", "ambulance", "emergency",
                    "health insurance", "ayushman bharat", "medical college",
                    "disease", "epidemic", "health scheme", "maternal health",
                    "child health", "nutrition", "anganwadi", "asha worker"
                ],
                priority_score=9.2,
                contact_info={
                    "website": "https://mohfw.gov.in",
                    "helpline": "104",
                    "email": "mohfw@gov.in"
                }
            ),
            
            # Education
            "MOE": DepartmentInfo(
                name="Ministry of Education",
                code="MOE",
                level=DepartmentLevel.CENTRAL,
                cpgrams_endpoint="/cpgrams/departments/MOE/submit",
                description="School education, higher education, skill development",
                keywords=[
                    "school", "college", "university", "education", "teacher", "student",
                    "admission", "scholarship", "examination", "degree", "certificate",
                    "mid day meal", "sarva shiksha", "higher education", "technical education",
                    "skill development", "vocational training", "research", "ugc", "aicte"
                ],
                priority_score=7.8,
                contact_info={
                    "website": "https://education.gov.in",
                    "helpline": "8800440559",
                    "email": "minister.edu@gov.in"
                }
            ),
            
            # Food and Public Distribution
            "MOFPD": DepartmentInfo(
                name="Ministry of Consumer Affairs, Food & Public Distribution",
                code="MOFPD",
                level=DepartmentLevel.CENTRAL,
                cpgrams_endpoint="/cpgrams/departments/MOFPD/submit",
                description="Food safety, public distribution system, consumer protection",
                keywords=[
                    "ration card", "pds", "food grain", "fair price shop", "food safety",
                    "fssai", "food quality", "consumer protection", "weights measures",
                    "cooking gas", "lpg", "kerosene", "sugar", "wheat", "rice",
                    "food adulteration", "food license", "consumer court", "food subsidy"
                ],
                priority_score=8.0,
                contact_info={
                    "website": "https://consumeraffairs.nic.in",
                    "helpline": "1800-11-4000",
                    "email": "caf@nic.in"
                }
            ),
            
            # Railways
            "RAILWAYS": DepartmentInfo(
                name="Ministry of Railways",
                code="RAILWAYS",
                level=DepartmentLevel.CENTRAL,
                cpgrams_endpoint="/cpgrams/departments/RAILWAYS/submit",
                description="Railway transport, stations, trains, railway infrastructure",
                keywords=[
                    "train", "railway", "station", "platform", "track", "signal",
                    "railway crossing", "reservation", "ticket", "passenger",
                    "goods train", "railway bridge", "railway line", "metro rail",
                    "suburban train", "express train", "railway safety", "railway police",
                    "railway hospital", "railway quarters", "railway canteen"
                ],
                priority_score=8.3,
                contact_info={
                    "website": "https://indianrailways.gov.in",
                    "helpline": "139",
                    "email": "railwayboard@gov.in"
                }
            ),
            
            # Telecommunications
            "DOT": DepartmentInfo(
                name="Department of Telecommunications",
                code="DOT",
                level=DepartmentLevel.CENTRAL,
                cpgrams_endpoint="/cpgrams/departments/DOT/submit",
                description="Telecom services, mobile networks, internet connectivity",
                keywords=[
                    "mobile", "phone", "telecom", "internet", "broadband", "wifi",
                    "network", "signal", "tower", "connectivity", "data",
                    "sim card", "mobile number", "landline", "fiber", "digital india",
                    "bsnl", "mtnl", "telecom operator", "call drop", "network issue"
                ],
                priority_score=7.5,
                contact_info={
                    "website": "https://dot.gov.in",
                    "helpline": "198",
                    "email": "dot@gov.in"
                }
            ),
            
            # Banking and Finance
            "MOFIN": DepartmentInfo(
                name="Ministry of Finance",
                code="MOFIN",
                level=DepartmentLevel.CENTRAL,
                cpgrams_endpoint="/cpgrams/departments/MOFIN/submit",
                description="Banking, insurance, taxation, financial services",
                keywords=[
                    "bank", "atm", "loan", "insurance", "tax", "income tax",
                    "gst", "pension", "pf", "epf", "financial", "money",
                    "account", "deposit", "withdrawal", "credit card", "debit card",
                    "jan dhan", "mudra", "pradhan mantri", "subsidy", "benefit"
                ],
                priority_score=7.2,
                contact_info={
                    "website": "https://finmin.nic.in",
                    "helpline": "14448",
                    "email": "finmin@gov.in"
                }
            ),
            
            # Agriculture
            "MOAFW": DepartmentInfo(
                name="Ministry of Agriculture & Farmers Welfare",
                code="MOAFW",
                level=DepartmentLevel.CENTRAL,
                cpgrams_endpoint="/cpgrams/departments/MOAFW/submit",
                description="Agriculture, farming, crop insurance, farmer welfare",
                keywords=[
                    "agriculture", "farming", "farmer", "crop", "seed", "fertilizer",
                    "pesticide", "irrigation", "kisan", "msp", "procurement",
                    "crop insurance", "pm kisan", "soil", "land", "agriculture loan",
                    "krishi", "animal husbandry", "dairy", "fisheries", "horticulture"
                ],
                priority_score=7.9,
                contact_info={
                    "website": "https://agricoop.gov.in",
                    "helpline": "155261",
                    "email": "agricoop@gov.in"
                }
            ),
            
            # State/Local Level Departments
            "PWD": DepartmentInfo(
                name="Public Works Department",
                code="PWD",
                level=DepartmentLevel.STATE,
                cpgrams_endpoint="/cpgrams/departments/PWD/submit",
                description="State roads, government buildings, infrastructure",
                keywords=[
                    "state road", "district road", "village road", "government building",
                    "public works", "construction", "maintenance", "bridge", "culvert",
                    "pwd", "road repair", "building repair", "infrastructure"
                ],
                priority_score=8.1,
                contact_info={
                    "helpline": "1077",
                    "email": "pwd@state.gov.in"
                }
            ),
            
            "MUNICIPAL": DepartmentInfo(
                name="Municipal Corporation/Council",
                code="MUNICIPAL",
                level=DepartmentLevel.LOCAL,
                cpgrams_endpoint="/cpgrams/departments/MUNICIPAL/submit",
                description="Local civic services, water, sanitation, local roads",
                keywords=[
                    "municipal", "corporation", "council", "panchayat", "ward",
                    "local", "civic", "street light", "garbage collection",
                    "sewerage", "drainage", "water supply", "property tax",
                    "birth certificate", "death certificate", "trade license"
                ],
                priority_score=8.7,
                contact_info={
                    "helpline": "1073",
                    "email": "municipal@local.gov.in"
                }
            ),
            
            "POLICE": DepartmentInfo(
                name="State Police Department",
                code="POLICE",
                level=DepartmentLevel.STATE,
                cpgrams_endpoint="/cpgrams/departments/POLICE/submit",
                description="Law and order, crime prevention, traffic management",
                keywords=[
                    "police", "crime", "theft", "robbery", "traffic", "challan",
                    "fir", "complaint", "law order", "security", "patrol",
                    "traffic signal", "traffic police", "women safety", "cyber crime",
                    "police station", "constable", "inspector", "violence"
                ],
                priority_score=9.5,
                contact_info={
                    "helpline": "100",
                    "email": "police@state.gov.in"
                }
            ),
            
            # Special Categories
            "POLLUTION": DepartmentInfo(
                name="Pollution Control Board",
                code="POLLUTION",
                level=DepartmentLevel.STATE,
                cpgrams_endpoint="/cpgrams/departments/POLLUTION/submit",
                description="Environmental protection, pollution control, waste management",
                keywords=[
                    "pollution", "environment", "air quality", "water pollution",
                    "noise pollution", "industrial waste", "smoke", "dust",
                    "chemical", "factory", "emission", "environmental clearance",
                    "green belt", "tree cutting", "forest", "wildlife"
                ],
                priority_score=8.4,
                contact_info={
                    "helpline": "1800-11-0909",
                    "email": "pcb@state.gov.in"
                }
            )
        }
        
        # Create keyword to department mapping for quick lookup
        self.keyword_dept_mapping = {}
        for dept_code, dept_info in self.departments.items():
            for keyword in dept_info.keywords:
                if keyword not in self.keyword_dept_mapping:
                    self.keyword_dept_mapping[keyword] = []
                self.keyword_dept_mapping[keyword].append((dept_code, dept_info.priority_score))
        
        # Sort by priority score
        for keyword in self.keyword_dept_mapping:
            self.keyword_dept_mapping[keyword].sort(key=lambda x: x[1], reverse=True)
    
    def identify_department(self, complaint_text: str, ai_analysis: Dict = None, location_info: Dict = None) -> Dict[str, Any]:
        """
        Identify the most appropriate department for a complaint
        
        Args:
            complaint_text: The complaint description
            ai_analysis: AI analysis results from image/text processing
            location_info: Location information if available
            
        Returns:
            Dictionary with department identification results
        """
        try:
            # Normalize text for analysis
            text_lower = complaint_text.lower()
            
            # Extract keywords and phrases
            keywords_found = self._extract_keywords(text_lower)
            
            # Score departments based on keyword matches
            dept_scores = self._score_departments(keywords_found, text_lower)
            
            # Apply AI analysis boost if available
            if ai_analysis:
                dept_scores = self._apply_ai_analysis_boost(dept_scores, ai_analysis)
            
            # Apply location-based adjustments
            if location_info:
                dept_scores = self._apply_location_adjustments(dept_scores, location_info)
            
            # Get top departments
            top_departments = sorted(dept_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            
            if not top_departments:
                # Fallback to general department
                return self._get_fallback_department()
            
            primary_dept = top_departments[0]
            dept_info = self.departments[primary_dept[0]]
            
            # Build comprehensive response
            result = {
                'success': True,
                'primary_department': {
                    'name': dept_info.name,
                    'code': dept_info.code,
                    'level': dept_info.level.value,
                    'cpgrams_endpoint': dept_info.cpgrams_endpoint,
                    'description': dept_info.description,
                    'confidence_score': min(primary_dept[1], 100.0),
                    'contact_info': dept_info.contact_info,
                    'ministry_parent': dept_info.ministry_parent
                },
                'alternative_departments': [],
                'routing_info': {
                    'api_endpoint': f"https://api.cpgrams.gov.in{dept_info.cpgrams_endpoint}",
                    'submission_method': 'POST',
                    'required_fields': self._get_required_fields(dept_info),
                    'estimated_response_time': self._get_response_time(dept_info)
                },
                'keywords_matched': keywords_found,
                'analysis_details': {
                    'total_departments_evaluated': len(dept_scores),
                    'matching_method': 'keyword_ai_hybrid',
                    'location_factor_applied': location_info is not None,
                    'ai_boost_applied': ai_analysis is not None
                }
            }
            
            # Add alternative departments
            for alt_dept, score in top_departments[1:]:
                alt_info = self.departments[alt_dept]
                result['alternative_departments'].append({
                    'name': alt_info.name,
                    'code': alt_info.code,
                    'level': alt_info.level.value,
                    'confidence_score': min(score, 100.0),
                    'cpgrams_endpoint': alt_info.cpgrams_endpoint
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in department identification: {e}")
            return self._get_fallback_department()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from complaint text"""
        keywords_found = []
        
        # Direct keyword matching
        for keyword in self.keyword_dept_mapping:
            if keyword in text:
                keywords_found.append(keyword)
        
        # Pattern-based matching
        patterns = {
            'road_issues': r'\b(pothole|crack|broken.*road|road.*repair|traffic.*jam)\b',
            'water_issues': r'\b(no.*water|water.*problem|leak|pipe.*burst|drainage)\b',
            'electricity_issues': r'\b(power.*cut|no.*electricity|transformer|wire.*problem)\b',
            'garbage_issues': r'\b(garbage|waste|dirty|cleaning|dustbin)\b',
            'health_issues': r'\b(hospital|doctor|medical|health.*problem|emergency)\b'
        }
        
        for category, pattern in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                keywords_found.append(category)
        
        return list(set(keywords_found))  # Remove duplicates
    
    def _score_departments(self, keywords_found: List[str], full_text: str) -> Dict[str, float]:
        """Score departments based on keyword matches"""
        dept_scores = {}
        
        for keyword in keywords_found:
            if keyword in self.keyword_dept_mapping:
                for dept_code, base_score in self.keyword_dept_mapping[keyword]:
                    if dept_code not in dept_scores:
                        dept_scores[dept_code] = 0.0
                    
                    # Add keyword match score
                    dept_scores[dept_code] += base_score * 2.0
        
        # Text context analysis for additional scoring
        context_patterns = {
            'MORTH': [r'national.*highway', r'nh\s*\d+', r'state.*highway'],
            'MOJS': [r'drinking.*water', r'water.*supply', r'bore.*well'],
            'MOP': [r'power.*supply', r'electricity.*bill', r'load.*shedding'],
            'MOHFW': [r'government.*hospital', r'primary.*health', r'medical.*emergency'],
            'MUNICIPAL': [r'street.*light', r'garbage.*collection', r'municipal.*corporation']
        }
        
        for dept_code, patterns in context_patterns.items():
            if dept_code not in dept_scores:
                dept_scores[dept_code] = 0.0
            
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    dept_scores[dept_code] += 15.0  # Context bonus
        
        return dept_scores
    
    def _apply_ai_analysis_boost(self, dept_scores: Dict[str, float], ai_analysis: Dict) -> Dict[str, float]:
        """Apply AI analysis results to boost department scores"""
        try:
            # Get AI-suggested category
            ai_category = ai_analysis.get('category', '').lower()
            ai_department = ai_analysis.get('suggested_department', '').lower()
            
            # Category to department mapping
            category_dept_mapping = {
                'roads': ['MORTH', 'PWD', 'MUNICIPAL'],
                'water': ['MOJS', 'MUNICIPAL'],
                'electricity': ['MOP'],
                'sanitation': ['MOHUA', 'MUNICIPAL'],
                'healthcare': ['MOHFW'],
                'education': ['MOE'],
                'transport': ['MORTH', 'RAILWAYS'],
                'food_safety': ['MOFPD'],
                'agriculture': ['MOAFW'],
                'police': ['POLICE'],
                'environment': ['POLLUTION']
            }
            
            # Boost departments based on AI category
            if ai_category in category_dept_mapping:
                for dept_code in category_dept_mapping[ai_category]:
                    if dept_code in dept_scores:
                        dept_scores[dept_code] += 25.0  # AI category boost
                    else:
                        dept_scores[dept_code] = 25.0
            
            # Additional boost if AI directly suggests department
            for dept_code, dept_info in self.departments.items():
                if ai_department in dept_info.name.lower():
                    dept_scores[dept_code] = dept_scores.get(dept_code, 0) + 30.0
            
            return dept_scores
            
        except Exception as e:
            self.logger.error(f"Error applying AI analysis boost: {e}")
            return dept_scores
    
    def _apply_location_adjustments(self, dept_scores: Dict[str, float], location_info: Dict) -> Dict[str, float]:
        """Apply location-based adjustments to department scores"""
        try:
            location_text = (location_info.get('final_address') or '').lower()
            
            # Boost local departments for local issues
            if any(term in location_text for term in ['ward', 'colony', 'society', 'street', 'lane']):
                local_depts = ['MUNICIPAL', 'PWD']
                for dept in local_depts:
                    if dept in dept_scores:
                        dept_scores[dept] += 10.0  # Local context boost
            
            # Boost state departments for state-level locations
            if any(term in location_text for term in ['district', 'taluka', 'block', 'mandal']):
                state_depts = ['PWD', 'POLICE', 'POLLUTION']
                for dept in state_depts:
                    if dept in dept_scores:
                        dept_scores[dept] += 8.0
            
            # Boost central departments for national infrastructure
            if any(term in location_text for term in ['national highway', 'nh', 'expressway']):
                if 'MORTH' in dept_scores:
                    dept_scores['MORTH'] += 15.0
            
            return dept_scores
            
        except Exception as e:
            self.logger.error(f"Error applying location adjustments: {e}")
            return dept_scores
    
    def _get_required_fields(self, dept_info: DepartmentInfo) -> List[str]:
        """Get required fields for department submission"""
        base_fields = [
            'complaint_description',
            'complainant_name',
            'complainant_mobile',
            'complainant_address',
            'incident_location',
            'category',
            'priority'
        ]
        
        # Department-specific additional fields
        dept_specific_fields = {
            'MORTH': ['highway_number', 'km_post'],
            'MOJS': ['water_source_type', 'quality_issue'],
            'MOP': ['power_connection_number', 'outage_duration'],
            'MOHFW': ['hospital_name', 'emergency_level'],
            'RAILWAYS': ['train_number', 'station_name'],
            'POLICE': ['incident_type', 'urgency_level']
        }
        
        additional = dept_specific_fields.get(dept_info.code, [])
        return base_fields + additional
    
    def _get_response_time(self, dept_info: DepartmentInfo) -> str:
        """Get estimated response time for department"""
        response_times = {
            DepartmentLevel.LOCAL: "3-7 days",
            DepartmentLevel.DISTRICT: "7-15 days", 
            DepartmentLevel.STATE: "15-30 days",
            DepartmentLevel.CENTRAL: "30-60 days"
        }
        
        # Emergency departments get faster response
        emergency_depts = ['POLICE', 'MOHFW']
        if dept_info.code in emergency_depts:
            return "24-48 hours"
        
        return response_times.get(dept_info.level, "30 days")
    
    def _get_fallback_department(self) -> Dict[str, Any]:
        """Return fallback department when identification fails"""
        return {
            'success': True,
            'primary_department': {
                'name': 'General Administration Department',
                'code': 'GENERAL',
                'level': 'state',
                'cpgrams_endpoint': '/cpgrams/departments/GENERAL/submit',
                'description': 'General public grievances and administrative issues',
                'confidence_score': 30.0,
                'contact_info': {
                    'helpline': '1076',
                    'email': 'grievance@gov.in'
                }
            },
            'alternative_departments': [],
            'routing_info': {
                'api_endpoint': 'https://api.cpgrams.gov.in/cpgrams/departments/GENERAL/submit',
                'submission_method': 'POST',
                'required_fields': ['complaint_description', 'complainant_name', 'location'],
                'estimated_response_time': '30 days'
            },
            'keywords_matched': [],
            'analysis_details': {
                'total_departments_evaluated': 0,
                'matching_method': 'fallback',
                'confidence_note': 'Could not identify specific department, routing to general administration'
            }
        }
    
    def get_department_info(self, dept_code: str) -> Optional[DepartmentInfo]:
        """Get detailed information about a specific department"""
        return self.departments.get(dept_code)
    
    def list_all_departments(self) -> Dict[str, DepartmentInfo]:
        """Get all available departments"""
        return self.departments.copy()
    
    def search_departments(self, query: str) -> List[Tuple[str, DepartmentInfo, float]]:
        """Search departments by name or keywords"""
        results = []
        query_lower = query.lower()
        
        for dept_code, dept_info in self.departments.items():
            score = 0.0
            
            # Name matching
            if query_lower in dept_info.name.lower():
                score += 50.0
            
            # Keyword matching
            for keyword in dept_info.keywords:
                if query_lower in keyword or keyword in query_lower:
                    score += 10.0
            
            # Description matching
            if query_lower in dept_info.description.lower():
                score += 20.0
            
            if score > 0:
                results.append((dept_code, dept_info, score))
        
        return sorted(results, key=lambda x: x[2], reverse=True)

# Global department identifier instance
department_identifier = DepartmentIdentifier()
