import logging
import json
from typing import Dict

# Configure logging
logger = logging.getLogger(__name__)

class LLMService:
    """
    Dummy service to simulate LLM responses for testing.
    This bypasses any real API calls to avoid dependencies and errors.
    """
    
    def extract_company_info(self, text: str) -> Dict:
        """
        Simulates the extraction of company information from text using an LLM.
        
        Args:
            text (str): The input text to process.
            
        Returns:
            Dict: A dictionary with dummy company information.
        """
        logger.info(f"DUMMY LLM: Simulating extraction for text: '{text[:50]}...'")
        
        # This is the dummy data that will be returned every time
        # You can add more variety here if needed for specific tests
        dummy_data = {
            'name': 'Dummy Corp',
            'industry': 'Technology',
            'location': 'San Francisco, CA',
            'tier': 'tier1',
            'description': 'A dummy company created for testing purposes.',
            'contact_info': 'contact@dummycorp.com',
        }
        
        # You can add logic to simulate different outputs based on the input text
        if "google" in text.lower():
            dummy_data['name'] = 'Google'
            dummy_data['tier'] = 'tier1'
            dummy_data['description'] = 'Tech giant specializing in search and cloud services.'
        elif "microsoft" in text.lower():
            dummy_data['name'] = 'Microsoft'
            dummy_data['tier'] = 'tier1'
            dummy_data['description'] = 'Software and technology company.'
            
        # Simulate a small delay to mimic network latency
        # This is optional but can make the front-end experience feel more realistic
        import time
        time.sleep(1)
        
        logger.info(f"DUMMY LLM: Returning simulated company data: {dummy_data['name']}")
        return dummy_data