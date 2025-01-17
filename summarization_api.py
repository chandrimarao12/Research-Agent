


from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import openai
import os

app = Flask(__name__)
CORS(app)

# Class to parse request data
class SummarizeRequest:
    def __init__(self, query, max_links=5):
        self.query = query
        self.max_links = max_links

# Function to fetch Google search results using Custom Search API
def fetch_google_results(query, api_key, cx):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        return results.get("items", [])
    else:
        raise Exception(f"Google API Error: {response.status_code} - {response.text}")

# Function to extract textual content from a URL
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=5)  # Timeout to prevent hanging
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = soup.find_all("p")
            text = " ".join([para.get_text() for para in paragraphs])
            
            return text
        else:
            return ""
    except Exception as e:
        return f"Failed to fetch content from {url}: {e}"

def summarize_with_openai(query,text, api_key, model="gpt-3.5-turbo"):
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text.according to the given query"},
                {"role": "user", "content": f"Summarize the following text according to the query: {query} ,{text}"}
            ]
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Summarization failed: {e}"

        

def summarize_google_links(query, google_api_key, cx, openai_api_key, max_links=5):
    try:
        search_results = fetch_google_results(query, google_api_key, cx)
        results_with_urls = []
        combined_text = ""
        
        for idx, item in enumerate(search_results[:max_links], start=1):
            link = item.get("link")
            content = extract_text_from_url(link)
            results_with_urls.append({"url": link, "text": content})
            combined_text += content + "\n\n"
        print("len: ",len(combined_text))
        if len(combined_text)>16370:
            combined_text=combined_text[:16385]
        summary = summarize_with_openai(query, combined_text, openai_api_key)
        return results_with_urls, summary
    except Exception as e:
        return f"An error occurred: {e}"


@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    query = data.get("query")
    max_links = data.get("max_links", 5)

    GOOGLE_API_KEY = os.getenv('GOOGLE_API')
    CX = os.getenv('CX')
    OPENAI_API_KEY =os.getenv('OPENAI_API')
    print(data.get("max_links"))
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    

    try:
        results_with_urls, summary = summarize_google_links(query, GOOGLE_API_KEY, CX, OPENAI_API_KEY, max_links)
        return jsonify({"query": query, "summary": summary, "results": results_with_urls})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
   
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
