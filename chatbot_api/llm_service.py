import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# If API key is not set, we'll provide a fallback summary function
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None
    print("Warning: OPENAI_API_KEY not found. Will use fallback summary generation.")

def generate_summary(data_context, query):
    """
    Generate an intelligent summary of real estate data using OpenAI API
    
    Args:
        data_context (dict): Dictionary containing real estate data context
        query (str): User's query
    
    Returns:
        str: An intelligent summary of the data
    """
    # If OpenAI client isn't initialized, use fallback summary
    if client is None:
        return generate_fallback_summary(data_context, query)
        
    try:
        # Extract key information from data context
        area_info = data_context.get('area_info', 'No specific area')
        price_info = data_context.get('price_info', 'No price data available')
        demand_info = data_context.get('demand_info', 'No demand data available')
        trend_info = data_context.get('trend_info', 'No trend data available')
        
        # Create a prompt for the OpenAI model
        prompt = f"""
        You are a real estate analysis assistant. Generate a comprehensive and insightful summary
        based on the following data:

        User Query: {query}
        Area: {area_info}
        Price Information: {price_info}
        Demand Information: {demand_info}
        Trends: {trend_info}

        Provide a natural-sounding, intelligent analysis that a real estate professional might give.
        Include insights about pricing trends, demand patterns, and investment potential where relevant.
        Keep the summary concise (2-3 sentences) but insightful.
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a real estate analysis expert providing concise, insightful summaries."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        # Get the summary from the response
        summary = response.choices[0].message.content.strip()
        
        return summary
    
    except Exception as e:
        print(f"Error generating summary with OpenAI: {str(e)}")
        return generate_fallback_summary(data_context, query)

def generate_fallback_summary(data_context, query):
    """
    Generate a fallback summary when OpenAI API is not available
    
    Args:
        data_context (dict): Dictionary containing real estate data context
        query (str): User's query
    
    Returns:
        str: A fallback summary of the data
    """
    # Extract key information from data context
    area_info = data_context.get('area_info', 'No specific area')
    price_info = data_context.get('price_info', 'No price data available')
    demand_info = data_context.get('demand_info', 'No demand data available')
    trend_info = data_context.get('trend_info', 'No trend data available')
    
    # Generate a simple summary based on the data context
    summary = f"Analysis for {area_info}: "
    if price_info != 'No price data available':
        summary += f"{price_info}. "
    if demand_info != 'No demand data available':
        summary += f"{demand_info}. "
    if trend_info != 'No trend data available':
        summary += f"{trend_info}."
    
    return summary
