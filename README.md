# AI Information Extractor

## Project Description
The AI Information Extractor is a powerful Streamlit-based application that automates the process of gathering and analyzing information from web searches using AI. It combines web search capabilities with LLM processing to extract specific information about entities from search results.

Key Features:
- Import data from CSV files or Google Sheets
- Automated web searching using SerpAPI
- AI-powered information extraction using Groq's Mixtral model
- Export results to CSV or Google Sheets
- Real-time progress tracking
- Detailed logging and error handling

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Google Cloud Platform account (for Google Sheets integration)
- Groq API key
- SerpAPI key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-information-extractor.git
cd ai-information-extractor
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

### Requirements.txt
```
streamlit
pandas
requests
groq
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
```

## Usage Guide

### Starting the Application
Run the Streamlit application:
```bash
streamlit run app.py
```

### Google Sheets Setup

1. Create a Google Cloud Project:
   - Go to Google Cloud Console
   - Create a new project
   - Enable Google Sheets API

2. Create Service Account Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Create Service Account
   - Download JSON credentials file
   - Share your Google Sheet with the service account email

3. Using Google Sheets Integration:
   - Upload credentials JSON file in the app
   - Choose between importing from or exporting to Google Sheets
   - For imports: Paste your Google Sheet URL
   - For exports: Select Google Sheets as export option

### Setting Up Search Queries

1. Data Preparation:
   - Prepare your input data with entities you want to research
   - Format can be CSV or Google Sheets
   - Ensure your data has clear column headers

2. Configure Search:
   - Select the column containing your target entities
   - Create a search prompt template using {entity} placeholder
   - Example: "Get the email address and website for {entity}"

3. Run Extraction:
   - Click "Extract Information" to start the process
   - Monitor progress in real-time
   - View intermediate results as they're processed

## API Keys and Environment Variables

### Required API Keys:
1. Groq API Key:
   - Sign up at https://console.groq.com
   - Replace `your_groq_api_key_here` in the code with your key
   - Or set environment variable: `GROQ_API_KEY`

2. SerpAPI Key:
   - Sign up at https://serpapi.com
   - Replace `your_serpapi_key_here` in the code with your key
   - Or set environment variable: `SERPAPI_KEY`

### Environment Variables Setup:
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
SERPAPI_KEY=your_serpapi_key_here
```

## Optional Features

### 1. Advanced Google Sheets Integration
- Sheet selection dropdown
- Custom range selection
- Multiple sheet support
- Automatic sheet creation for exports

### 2. Progress Tracking
- Real-time progress bar
- Status updates for each entity
- Intermediate results display
- Detailed logging

### 3. Error Handling
- Comprehensive error messages
- Fallback options for failed operations
- Debug mode for troubleshooting

### 4. Export Options
- CSV download
- Google Sheets export
- Rich formatting in exported sheets

## Acknowledgments
- Groq for providing the LLM API
- SerpAPI for search capabilities
- Google Sheets API for data integration
