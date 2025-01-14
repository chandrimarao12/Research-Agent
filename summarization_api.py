from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for your frontend origin
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://127.0.0.1:5500"],  # Replace with your frontend's address
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Define the request model
class SummarizeRequest(BaseModel):
    query: str
    max_links: Optional[int] = 5  # Default to 5 links


# Function to fetch Google search results using Custom Search API
def fetch_google_results(query, api_key, cx):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        return results.get("items", [])
    else:
        raise Exception(f"Google API Error: {response.status_code} - {response.text}")


# Function to extract text content from a URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = soup.find_all("p")
            text = " ".join([para.get_text() for para in paragraphs])
            return text
        else:
            return ""
    except Exception as e:
        return ""


# Summarization function (dummy implementation for now)
def summarize_text(text):
    return text[:500] + "..." if len(text) > 500 else text


# Main function to summarize content from top search links
def summarize_google_links(query, google_api_key, cx, max_links=5):
    try:
        search_results = fetch_google_results(query, google_api_key, cx)
        combined_text = ""
        for idx, item in enumerate(search_results[:max_links], start=1):
            link = item.get("link")
            content = extract_text_from_url(link)
            combined_text += content + "\n\n"
        return summarize_text(combined_text)
    except Exception as e:
        return f"An error occurred: {e}"


# API endpoint
@app.post("/summarize")
def summarize(request: SummarizeRequest):
    GOOGLE_API_KEY =  'AIzaSyDEDfs7wkpb8inNdAgK08668D5AVMNWymI'
    CX = '43c411ae363c24c9f' # Replace with your CX ID
    try:
        summary = summarize_google_links(
            query=request.query, google_api_key=GOOGLE_API_KEY, cx=CX, max_links=request.max_links
        )
        return {"query": request.query, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
