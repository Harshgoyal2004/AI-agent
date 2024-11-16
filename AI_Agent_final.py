import streamlit as st
import pandas as pd
import requests
from groq import Groq
from typing import List, Dict, Optional, Tuple
import os
from io import StringIO
import json
import time
import logging
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Direct API key initialization
GROQ_API_KEY = "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"  # Replace with your Groq API key
SERPAPI_KEY = "fa51a39a5d5812e91e5c2d4d51744dff908f7c92ed8410ae0348ca904d4b096f"    # Replace with your SerpAPI key

def validate_service_account_credentials(credentials_json: dict) -> bool:
    """Validate that the service account credentials JSON contains all required fields."""
    required_fields = [
        'type',
        'project_id',
        'private_key_id',
        'private_key',
        'client_email',
        'client_id',
        'auth_uri',
        'token_uri',
        'auth_provider_x509_cert_url',
        'client_x509_cert_url'
    ]
    
    missing_fields = [field for field in required_fields if field not in credentials_json]
    
    if missing_fields:
        raise ValueError(
            f"Invalid service account credentials format. Missing required fields: {', '.join(missing_fields)}"
        )
    
    return True

def initialize_groq_client() -> Groq:
    """Initialize Groq client with API key"""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        # Test the client with a simple completion
        test_response = client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model="mixtral-8x7b-32768",
            temperature=0.1,
            max_tokens=10
        )
        logger.info("Groq client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Error initializing Groq client: {str(e)}")
        raise

def initialize_sheets_client(credentials_json: dict) -> tuple:
    """Initialize Google Sheets client with service account credentials"""
    try:
        credentials = ServiceAccountCredentials.from_service_account_info(
            credentials_json,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        logger.info("Google Sheets client initialized successfully")
        return service
    except Exception as e:
        logger.error(f"Error initializing Google Sheets client: {str(e)}")
        raise

def read_google_sheet(service, spreadsheet_id: str, range_name: str = 'Sheet1') -> pd.DataFrame:
    """Read data from Google Sheets and return as DataFrame"""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            raise ValueError("No data found in the specified sheet")
            
        df = pd.DataFrame(values[1:], columns=values[0])
        logger.info(f"Successfully read {len(df)} rows from Google Sheets")
        return df
    except Exception as e:
        logger.error(f"Error reading from Google Sheets: {str(e)}")
        raise

def create_new_spreadsheet(service) -> str:
    """Create a new Google Spreadsheet and return its ID"""
    try:
        spreadsheet = {
            'properties': {
                'title': f'AI Extracted Information - {time.strftime("%Y-%m-%d %H:%M:%S")}'
            }
        }
        spreadsheet = service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        logger.info(f"Created new spreadsheet with ID: {spreadsheet_id}")
        return spreadsheet_id
    except Exception as e:
        logger.error(f"Error creating new spreadsheet: {str(e)}")
        raise

def export_to_sheets(service, spreadsheet_id: str, df: pd.DataFrame) -> str:
    """Export DataFrame to Google Sheets and return the sheet URL"""
    try:
        # Prepare the values
        values = [df.columns.tolist()]  # Header row
        values.extend(df.values.tolist())  # Data rows

        body = {
            'values': values
        }

        # Update the sheet
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Sheet1!A1',
            valueInputOption='RAW',
            body=body
        ).execute()

        # Generate sheet URL
        sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        logger.info(f"Data exported to spreadsheet: {sheet_url}")
        return sheet_url
    except Exception as e:
        logger.error(f"Error exporting to sheets: {str(e)}")
        raise

def process_with_llm(client: Groq, entity: str, search_results: List[Dict], prompt_template: str) -> str:
    """Process search results with LLM to extract relevant information"""
    try:
        context = "\n\n".join([
            f"Title: {result['title']}\nSnippet: {result['snippet']}\nURL: {result['link']}"
            for result in search_results
        ])

        system_prompt = """You are an AI assistant that extracts specific information from web search results.
        Analyze the provided search results and extract the requested information.
        If the information is not found, indicate that it's not available.
        Provide your response in a clear, structured format."""

        user_prompt = f"""
        Entity: {entity}
        Search Query: {prompt_template.replace('{entity}', entity)}
        
        Search Results:
        {context}
        
        Please extract the requested information from these search results.
        """

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="mixtral-8x7b-32768",
            temperature=0.1,
            max_tokens=500
        )

        extracted_info = response.choices[0].message.content
        logger.info(f"Successfully processed entity: {entity}")
        return extracted_info
    except Exception as e:
        logger.error(f"Error processing with LLM: {str(e)}")
        return f"Error processing: {str(e)}"

class WebSearchAgent:
    def __init__(self):
        self.serpapi_key = SERPAPI_KEY
        
    def search(self, query: str) -> List[Dict]:
        """Perform a web search using SerpAPI"""
        logger.info(f"Searching for: {query}")
        base_url = "https://serpapi.com/search.json"
        params = {
            "api_key": self.serpapi_key,
            "q": query,
            "engine": "google",
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            results = response.json()
            
            if "organic_results" in results:
                return [
                    {
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "link": result.get("link", "")
                    }
                    for result in results["organic_results"][:3]
                ]
            return []
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []

def main():
    st.set_page_config(page_title="AI Information Extractor", layout="wide")
    st.title("AI Information Extractor")
    
    # Initialize Groq client
    try:
        groq_client = initialize_groq_client()
        logger.info("Groq client initialized successfully")
    except Exception as e:
        st.error(f"Error initializing Groq client: {str(e)}")
        return
    
    # Upload Google Sheets credentials
    st.subheader("Google Sheets Configuration")
    sheets_credentials_file = st.file_uploader(
        "Upload Google Sheets credentials JSON file", 
        type="json",
        help="Upload your Google Service Account credentials JSON file"
    )
    
    # Data Input Selection
    st.subheader("Data Input")
    input_method = st.radio(
        "Choose input method",
        ["Upload CSV", "Google Sheets", "Manual Entry"],
        help="Select how you want to input your data"
    )
    
    df = None
    
    if input_method == "Upload CSV":
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"File uploaded successfully! Found {len(df)} rows.")
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
                
    elif input_method == "Google Sheets":
        if sheets_credentials_file:
            try:
                credentials_json = json.load(sheets_credentials_file)
                validate_service_account_credentials(credentials_json)
                sheets_service = initialize_sheets_client(credentials_json)
                
                spreadsheet_id = st.text_input(
                    "Enter Google Sheets ID",
                    help="Enter the ID from your Google Sheets URL"
                )
                
                if spreadsheet_id:
                    try:
                        df = read_google_sheet(sheets_service, spreadsheet_id)
                        st.success(f"Data loaded successfully! Found {len(df)} rows.")
                    except Exception as e:
                        st.error(f"Error reading Google Sheet: {str(e)}")
            except Exception as e:
                st.error(f"Error with Google Sheets credentials: {str(e)}")
        else:
            st.warning("Please upload Google Sheets credentials to use this option.")
            
    elif input_method == "Manual Entry":
        st.info("Manual entry feature coming soon!")
    
    if df is not None:
        # Display data preview
        st.subheader("Data Preview")
        st.dataframe(df.head())
        
        # Column selection
        columns = df.columns.tolist()
        entity_column = st.selectbox("Select the main entity column", columns)
        
        # Query input
        st.subheader("Search Configuration")
        prompt_template = st.text_area(
            "Enter your search prompt template",
            "Get the email address and website for {entity}"
        )
        
        # Export options selection
        export_option = st.radio(
            "Choose export method",
            ["CSV", "Google Sheets"],
            help="Select how you want to export the final results"
        )
        
        if st.button("Extract Information"):
            st.info("Starting extraction process...")
            search_agent = WebSearchAgent()
            results = []
            
            # Create progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            results_container = st.container()
            
            try:
                for idx, entity in enumerate(df[entity_column]):
                    status_text.text(f"Processing {entity} ({idx + 1}/{len(df)})...")
                    
                    search_query = prompt_template.replace("{entity}", str(entity))
                    search_results = search_agent.search(search_query)
                    
                    if not search_results:
                        st.warning(f"No search results found for {entity}")
                    
                    extracted_info = process_with_llm(groq_client, entity, search_results, prompt_template)
                    
                    results.append({
                        entity_column: entity,
                        "Extracted Information": extracted_info,
                        "Number of Sources": len(search_results)
                    })
                    
                    progress_bar.progress((idx + 1) / len(df))
                    
                    with results_container:
                        temp_df = pd.DataFrame(results)
                        st.dataframe(temp_df)
                    
                    time.sleep(1)  # Rate limiting
                
                # Final results
                st.success("Extraction completed!")
                results_df = pd.DataFrame(results)
                
                # Export based on selected option
                if export_option == "CSV":
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="Download Results CSV",
                        data=csv,
                        file_name="extracted_results.csv",
                        mime="text/csv"
                    )
                else:  # Google Sheets
                    if sheets_credentials_file:
                        try:
                            with st.spinner("Exporting to Google Sheets..."):
                                credentials_json = json.load(sheets_credentials_file)
                                sheets_service = initialize_sheets_client(credentials_json)
                                spreadsheet_id = create_new_spreadsheet(sheets_service)
                                sheet_url = export_to_sheets(sheets_service, spreadsheet_id, results_df)
                                st.success(f"Data exported successfully! View your spreadsheet [here]({sheet_url})")
                        except Exception as e:
                            logger.error(f"Error during Google Sheets export: {str(e)}")
                            st.error(f"Error during export: {str(e)}")
                            st.warning("Falling back to CSV download...")
                            csv = results_df.to_csv(index=False)
                            st.download_button(
                                label="Download Results CSV",
                                data=csv,
                                file_name="extracted_results.csv",
                                mime="text/csv"
                            )
                    else:
                        st.error("Please upload Google Sheets credentials to export to Google Sheets")
                        
            except Exception as e:
                logger.error(f"Error during extraction: {str(e)}")
                st.error(f"Error during extraction: {str(e)}")

if __name__ == "__main__":
    main()
