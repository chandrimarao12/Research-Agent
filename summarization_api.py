
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os

# app = Flask(__name__)
# CORS(app)
# from flask_cors import CORS

app = Flask(__name__)
CORS(app)
class SummarizeRequest:
    def __init__(self, query, max_links=5):
        self.query = query
        self.max_links = max_links

def fetch_google_results(query, api_key, cx):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        return results.get("items", [])
    else:
        raise Exception(f"Google API Error: {response.status_code} - {response.text}")

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

def summarize_text(text):
    return text[:500] + "..." if len(text) > 500 else text

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

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    query = data.get("query")
    max_links = data.get("max_links", 5)
    GOOGLE_API_KEY = 'your- api'
    CX = 'cx'
    try:
        summary = summarize_google_links(query, GOOGLE_API_KEY, CX, max_links)
        return jsonify({"query": query, "summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port, debug=True)