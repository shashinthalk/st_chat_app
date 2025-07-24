import requests
import logging
from typing import List, Dict, Optional
import time

# Configure logging
logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    """Service to interact with the external knowledge base API"""
    
    def __init__(self):
        self.api_url = "https://n8n.shashinthalk.cc/webhook/fetch-knowledge-base-data"
        self.jwt_token = "a>6rj{pvGUpdaZfy$(#2Ss)"
        self.headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json",
            "User-Agent": "Flask-QA-API/1.0"
        }
        self.timeout = 15  # Increased timeout
        self.cache = {}
        self.cache_expiry = 300  # 5 minutes
        self.last_cache_time = 0
        
        # Mock data for testing/fallback (based on your provided example)
        self.mock_data = [
            {
                "_id": "6880bed079737a9e77620472",
                "question": "can u develop kotlin api backend",
                "answers": {
                    "title": "Kotlin API Backend Development",
                    "subtitle": "Expertise in Building Scalable and Secure APIs",
                    "about": "As a Full Stack Engineer with experience in Kotlin, I can help you develop a robust and scalable API backend using Kotlin. My expertise includes building RESTful APIs using Kotlin, Spring Boot, and other modern web technologies. I have a strong background in software development, plugin development, domain/hosting management, and client communication. My educational background includes a Bachelor of Information and Communication Technology (Hons) from the University of Kelaniya, Sri Lanka, and several certifications, such as Advanced React Development by Meta, Python for Data Science, AI, & Development by IBM, and a Certificate Course in Java Programming from the University of Kelaniya. I am currently based in Salzburg, Austria, and open to full-time opportunities within Austria or the EU.",
                    "projects": [
                        {
                            "title": "Kotlin API Backend",
                            "description": "A scalable and secure API backend built using Kotlin and Spring Boot",
                            "technologies": ["Kotlin", "Spring Boot"],
                            "link": "#"
                        }
                    ],
                    "whyWorkWithMe": [
                        "I bring more than 3 years of full stack development experience across freelance, agency, and product teams",
                        "I'm highly skilled in modern web technologies including React.js, Spring Boot, Kotlin, Python, PHP, and Webflow",
                        "I've successfully delivered 100+ projects internationally, both as a freelancer and team member",
                        "I hold a Bachelor's degree in ICT specialized in Software Systems and multiple certifications",
                        "I'm currently based in Salzburg and open to full-time opportunities within Austria or the EU"
                    ],
                    "callToAction": {
                        "heading": "Ready to Get Started?",
                        "message": "If you're ready to move forward with your project, feel free to get in touch. I'd be happy to discuss your goals and how I can help.",
                        "buttonText": "Contact Me",
                        "buttonLink": "/contact"
                    }
                }
            },
            {
                "_id": "68815c7179737a9e77620473",
                "question": "tell me about your self",
                "answers": {
                    "title": "About Nishan Shashintha",
                    "subtitle": "Full Stack Engineer Based in Salzburg, Austria",
                    "about": "Hi, I'm Nishan Shashintha, a Full Stack Engineer based in Salzburg, Austria. With over 3 years of full stack web development experience, I specialize in a wide range of modern web technologies including React.js, Kotlin, Spring Boot, Python, WordPress, PHP, Webflow, Laravel, Docker, AWS, MongoDB, SQL, and NoSQL. Currently, I work as a Full Stack Web Developer at Transpire Consultants, a Melbourne-based company with a remote team. In the past, I've worked at Datasprig, Sotros Infotech, Acecam, and as a successful freelancer on Fiverr with 100+ completed projects for international clients. I hold a Bachelor of Information and Communication Technology (Hons) from the University of Kelaniya, Sri Lanka, and have multiple certifications including Advanced React Development by Meta, Python for Data Science, AI & Development by IBM, and a Certificate Course in Java Programming from the University of Kelaniya. I am fluent in English (B2), German (A1), and my native language, Sinhala. I am currently looking for a Full Stack Engineering role in Austria, ideally within a product-focused or tech-driven company that values quality code, teamwork, and innovation.",
                    "projects": [
                        {
                            "title": "N/A",
                            "description": "N/A",
                            "technologies": [],
                            "link": "#"
                        }
                    ],
                    "whyWorkWithMe": [
                        "I bring more than 3 years of full stack development experience across freelance, agency, and product teams",
                        "I'm highly skilled in modern web technologies including React.js, Spring Boot, Kotlin, Python, PHP, and Webflow",
                        "I've successfully delivered 100+ projects internationally, both as a freelancer and team member",
                        "I hold a Bachelor's degree in ICT specialized in Software Systems and multiple certifications",
                        "I'm currently based in Salzburg and open to full-time opportunities within Austria or the EU"
                    ],
                    "callToAction": {
                        "heading": "Ready to Get Started?",
                        "message": "If you're ready to move forward with your project, feel free to get in touch. I'd be happy to discuss your goals and how I can help.",
                        "buttonText": "Contact Me",
                        "buttonLink": "/contact"
                    }
                }
            },
            {
                "_id": "68815ca179737a9e77620474",
                "question": "education and career experience",
                "answers": {
                    "title": "Education and Career Experience",
                    "subtitle": "Background and Expertise",
                    "about": "I have over 3 years of full stack web development experience across freelance, agency, and product-based environments. Currently, I work as a Full Stack Web Developer at Transpire Consultants, a Melbourne-based company with a remote team, where I focus on delivering React and Node.js applications, managing WordPress and Webflow sites, and deploying scalable backend services. Previously, I have worked at Datasprig, Sotros Infotech, and Acecam, and have been a successful freelancer on Fiverr with 100+ completed projects for international clients. I am highly skilled in modern web technologies including React.js, Kotlin, Spring Boot, Python, WordPress, PHP, Webflow, Laravel, Docker, AWS, MongoDB, SQL, and NoSQL, and have a strong track record in plugin development, domain/hosting management, and client communications.",
                    "projects": None,
                    "whyWorkWithMe": None,
                    "callToAction": {
                        "heading": "Ready to Get Started?",
                        "message": "If you're ready to move forward with your project, feel free to get in touch. I'd be happy to discuss your goals and how I can help.",
                        "buttonText": "Contact Me",
                        "buttonLink": "/contact"
                    }
                }
            },
            {
                "_id": "68815ea479737a9e77620481",
                "question": "can u design a photo",
                "answers": {
                    "title": "Outside of Expertise",
                    "subtitle": "Designing a photo is beyond my scope",
                    "about": "",
                    "projects": [],
                    "whyWorkWithMe": [
                        "As a Full Stack Engineer, I specialize in web development and design"
                    ],
                    "callToAction": {
                        "heading": "Let's Focus on Web Development",
                        "message": "If you need help with a web development project, I'd be happy to discuss how I can assist you.",
                        "buttonText": "Contact Me",
                        "buttonLink": "/contact"
                    }
                }
            }
        ]
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        return (
            self.cache and 
            time.time() - self.last_cache_time < self.cache_expiry
        )
    
    def fetch_knowledge_base(self, use_mock=False) -> List[Dict]:
        """
        Fetch knowledge base data from external API
        Returns cached data if available and not expired
        Falls back to mock data if API fails
        """
        # Return cached data if valid
        if self._is_cache_valid():
            logger.info("Returning cached knowledge base data")
            return self.cache.get('data', [])
        
        # Use mock data if explicitly requested
        if use_mock:
            logger.info("Using mock knowledge base data")
            self.cache = {
                'data': self.mock_data,
                'status': 'mock',
                'count': len(self.mock_data)
            }
            self.last_cache_time = time.time()
            return self.mock_data
        
        try:
            logger.info(f"Fetching knowledge base data from {self.api_url}")
            
            response = requests.get(
                self.api_url,
                headers=self.headers,
                timeout=self.timeout
            )
            
            # Log response details for debugging
            logger.info(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response format
                if isinstance(data, list):
                    # Cache the successful response
                    self.cache = {
                        'data': data,
                        'status': 'success',
                        'count': len(data)
                    }
                    self.last_cache_time = time.time()
                    
                    logger.info(f"Successfully fetched {len(data)} knowledge base entries")
                    return data
                else:
                    logger.error(f"Unexpected response format: {type(data)}")
                    # Fall back to mock data
                    return self._fallback_to_mock()
            
            elif response.status_code == 401:
                logger.error("Authentication failed - invalid JWT token")
                return self._fallback_to_mock()
            
            elif response.status_code == 403:
                logger.error(f"Forbidden - JWT token issue: {response.text}")
                return self._fallback_to_mock()
            
            elif response.status_code == 404:
                logger.error("Knowledge base API endpoint not found")
                return self._fallback_to_mock()
            
            else:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return self._fallback_to_mock()
                
        except requests.exceptions.Timeout:
            logger.error(f"API request timed out after {self.timeout} seconds")
            return self._fallback_to_mock()
            
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to knowledge base API")
            return self._fallback_to_mock()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return self._fallback_to_mock()
            
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            return self._fallback_to_mock()
            
        except Exception as e:
            logger.error(f"Unexpected error fetching knowledge base: {str(e)}")
            return self._fallback_to_mock()
    
    def _fallback_to_mock(self) -> List[Dict]:
        """Fallback to mock data when API fails"""
        logger.info("Falling back to mock knowledge base data")
        self.cache = {
            'data': self.mock_data,
            'status': 'fallback',
            'count': len(self.mock_data)
        }
        self.last_cache_time = time.time()
        return self.mock_data
    
    def search_knowledge_base(self, question: str) -> Optional[Dict]:
        """
        Search for a matching question in the knowledge base
        Returns the best match or None if no match found
        """
        if not question or not question.strip():
            return None
        
        # Try API first, then fallback to mock if needed
        knowledge_data = self.fetch_knowledge_base(use_mock=False)
        
        if not knowledge_data:
            logger.warning("No knowledge base data available for search")
            return None
        
        question_lower = question.strip().lower()
        
        # Keywords for smart matching
        ai_keywords = ['ai', 'artificial intelligence', 'artificial', 'intelligence']
        ml_keywords = ['ml', 'machine learning', 'machine', 'learning']
        kotlin_keywords = ['kotlin', 'api', 'backend', 'development', 'develop']
        about_keywords = ['about', 'yourself', 'who are you', 'tell me about', 'self']
        education_keywords = ['education', 'career', 'experience', 'background']
        design_keywords = ['design', 'photo', 'image', 'graphic']
        
        # Direct matching first
        for entry in knowledge_data:
            if not entry.get('question'):
                continue
                
            entry_question_lower = entry['question'].lower()
            
            # Exact match
            if question_lower == entry_question_lower:
                logger.info(f"Found exact match for: {question}")
                return entry
            
            # Substring match
            if question_lower in entry_question_lower or entry_question_lower in question_lower:
                logger.info(f"Found substring match for: {question}")
                return entry
        
        # Smart keyword matching
        for entry in knowledge_data:
            if not entry.get('question'):
                continue
                
            entry_question_lower = entry['question'].lower()
            
            # About/self questions
            if (any(keyword in question_lower for keyword in about_keywords) and 
                any(keyword in entry_question_lower for keyword in about_keywords)):
                logger.info(f"Found 'about' keyword match for: {question}")
                return entry
            
            # Education/career questions
            if (any(keyword in question_lower for keyword in education_keywords) and 
                any(keyword in entry_question_lower for keyword in education_keywords)):
                logger.info(f"Found 'education' keyword match for: {question}")
                return entry
            
            # Kotlin/development questions
            if (any(keyword in question_lower for keyword in kotlin_keywords) and 
                any(keyword in entry_question_lower for keyword in kotlin_keywords)):
                logger.info(f"Found 'kotlin' keyword match for: {question}")
                return entry
            
            # Design questions
            if (any(keyword in question_lower for keyword in design_keywords) and 
                any(keyword in entry_question_lower for keyword in design_keywords)):
                logger.info(f"Found 'design' keyword match for: {question}")
                return entry
        
        logger.info(f"No match found for question: {question}")
        return None
    
    def get_cache_info(self) -> Dict:
        """Get information about the current cache status"""
        return {
            'cached': bool(self.cache),
            'cache_age_seconds': time.time() - self.last_cache_time if self.last_cache_time else 0,
            'cache_expires_in': max(0, self.cache_expiry - (time.time() - self.last_cache_time)) if self.last_cache_time else 0,
            'cached_entries': len(self.cache.get('data', [])) if self.cache else 0,
            'cache_status': self.cache.get('status', 'none') if self.cache else 'none'
        }
    
    def clear_cache(self):
        """Clear the cache to force fresh data fetch"""
        self.cache = {}
        self.last_cache_time = 0
        logger.info("Knowledge base cache cleared")
    
    def test_api_connection(self) -> Dict:
        """Test the API connection and return detailed status"""
        try:
            response = requests.get(
                self.api_url,
                headers=self.headers,
                timeout=self.timeout
            )
            
            return {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_text': response.text[:200],
                'headers': dict(response.headers),
                'error': None
            }
            
        except Exception as e:
            return {
                'status_code': None,
                'success': False,
                'response_text': None,
                'headers': {},
                'error': str(e)
            }

# Global instance
knowledge_service = KnowledgeBaseService() 