import openai
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # Configure OpenAI API key
        openai.api_key = settings.OPENAI_API_KEY

    def generate_startup_summary(self, startup_data):
        """Generate a summary of the startup based on available data"""
        try:
            prompt = self._create_summary_prompt(startup_data)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  
                messages=[
                    {"role": "system", "content": "You are an expert startup analyst providing concise, insightful summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.5
            )
            return response['choices'][0]['message']['content'].strip()  
        except Exception as e:
            logger.error(f"Error generating startup summary: {str(e)}")
            return "Unable to generate summary at this time."
    
    def classify_industry(self, startup_data):
        """Classify the startup into industry verticals"""
        try:
            prompt = self._create_classification_prompt(startup_data)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages=[
                    {"role": "system", "content": "You are an expert at classifying startups into industry verticals."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.3
            )
            return response['choices'][0]['message']['content'].strip()  
        except Exception as e:
            logger.error(f"Error classifying industry: {str(e)}")
            return "Other"
    
    def _create_summary_prompt(self, startup_data):
        """Create prompt for summary generation"""
        prompt = f"""
        Based on the following information about a startup, provide a concise summary (3-4 sentences):
        
        Name: {startup_data.get('item_name', 'N/A')}
        Description: {startup_data.get('description', 'N/A')}
        Tagline: {startup_data.get('tagline', 'N/A')}
        Location: {startup_data.get('location', 'N/A')}
        Markets: {startup_data.get('markets', 'N/A')}
        Funding: {startup_data.get('total_funding_currency', '')} {startup_data.get('total_funding_amount', 'N/A')}
        Revenue Model: {startup_data.get('revenue_model', 'N/A')}
        Differentiators: {startup_data.get('differentiators', 'N/A')}
        Founded: {startup_data.get('founded_date', 'N/A')}
        """
        return prompt
    
    def _create_classification_prompt(self, startup_data):
        """Create prompt for industry classification"""
        prompt = f"""
        Based on the following information about a startup, classify it into ONE of these verticals: B2B, B2C, B2G, Marketplace, or other appropriate category.
        Return ONLY the category name without explanation.
        
        Name: {startup_data.get('item_name', 'N/A')}
        Description: {startup_data.get('description', 'N/A')}
        Tagline: {startup_data.get('tagline', 'N/A')}
        Markets: {startup_data.get('markets', 'N/A')}
        Revenue Model: {startup_data.get('revenue_model', 'N/A')}
        Clients: {startup_data.get('clients', 'N/A')}
        """
        return prompt
