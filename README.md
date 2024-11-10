# AI-agent
AI agent that reads through a dataset (CSV or Google Sheets) and performs a web search to retrieve specific information for each entity in a chosen column.

AI Web Search & Data Extraction Agent
An intelligent agent that automates web searches and information extraction based on user-defined queries, powered by LLMs and web search APIs.
Features

File Upload & Google Sheets Integration

Upload CSV files or connect directly to Google Sheets
Select target columns for data processing
Preview uploaded data before processing


Dynamic Query System

Custom prompt templates with dynamic entity replacement
Support for multiple field extraction in a single query
User-friendly prompt interface


Automated Web Search

Intelligent web searching for each entity
Rate-limiting and request management
Multiple search API support (SerpAPI/ScraperAPI)


LLM-Powered Data Extraction

Advanced information parsing using Groq/OpenAI
Structured data extraction from web results
Error handling and retry mechanisms


Results Management

Interactive results dashboard
CSV export functionality
Direct Google Sheets update option

Prerequisites

Python 3.8+
pip package manager
API keys for:

Search API (SerpAPI/ScraperAPI)
LLM API (Groq/OpenAI)
Google Sheets API (optional)

Installation

Clone the repository:

bashCopygit clone https://github.com/yourusername/ai-agent-project.git
cd ai-agent-project

Create and activate a virtual environment:

bashCopypython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:

bashCopypip install -r requirements.txt

Set up environment variables:

bashCopycp .env.example .env
Edit .env file with your API keys:
CopySEARCH_API_KEY=your_search_api_key
LLM_API_KEY=your_llm_api_key
GOOGLE_SHEETS_CREDENTIALS=path_to_credentials.json
Running the Application

Start the application:

bashCopystreamlit run app.py

Open your browser and navigate to http://localhost:8501

Usage Guide
1. Data Input

Click "Upload CSV" or enter Google Sheets URL
Select the column containing entities to search for
Preview your data to ensure correct loading

2. Query Configuration

Enter your search prompt template
Use {entity} placeholder for dynamic replacement
Example: "Find the email address and location of {entity}"

3. Running Searches

Click "Start Search" to begin the process
Monitor progress in the dashboard
View real-time results as they're processed

4. Exporting Results

Download results as CSV
Update connected Google Sheet (if configured)
View detailed extraction logs

🛠️ Project Structure
Copyai-agent-project/
├── app.py                 # Main Streamlit application
├── src/
│   ├── search/           # Search API integration
│   ├── llm/              # LLM processing logic
│   ├── sheets/           # Google Sheets integration
│   └── utils/            # Helper functions
├── tests/                # Test suite
├── requirements.txt      # Project dependencies
└── README.md            # This file

API Configuration
Search API Setup

Sign up for SerpAPI/ScraperAPI
Get your API key

LLM API Setup

Create account on Groq
Generate API key


Google Sheets API Setup 

Create project in Google Cloud Console
Enable Google Sheets API
Download credentials JSON
Upload this on streamlit web application

Watch the project demo: Loom Video Link
