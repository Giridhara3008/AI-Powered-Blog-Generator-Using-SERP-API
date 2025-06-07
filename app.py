import os
import requests
import markdown
from bs4 import BeautifulSoup
from flask import Flask, render_template, request as flask_request
from openai import OpenAI
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from serpapi import GoogleSearch

# --- SETUP ---
load_dotenv()
app = Flask(__name__)

# Initialize clients
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
def markdown_to_html(markdown_text: str) -> str:
    """
    Converts a Markdown formatted string to an HTML string.
    """
    return markdown.markdown(markdown_text, extensions=['fenced_code', 'tables'])

# --- CORE FUNCTIONS ---

def perform_seo_research(keyword: str):
    """
    Performs simplified SEO research by getting PAA, related searches,
    and competitor H2 headings.
    """
    print(f"🔬 Performing SEO research for keyword: {keyword}")
    
    # Step 1: Get Google SERP data using SerpApi
    search_params = {
        "q": keyword,
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "gl": "us",
        "hl": "en",
    }
    search = GoogleSearch(search_params)
    results = search.get_dict()

    people_also_ask = results.get("related_questions", [])
    related_searches = [q.get("query") for q in results.get("related_searches", [])]
    
    # Step 2: Analyze top 3 competitor headings
    competitor_headings = []
    top_organic_results = results.get("organic_results", [])[:3]

    print(f"Analyzing top {len(top_organic_results)} competitors...")
    for result in top_organic_results:
        try:
            url = result.get("link")
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all H2 tags and add their text to our list
            for h2 in soup.find_all('h2'):
                competitor_headings.append(h2.get_text(strip=True))
        except requests.RequestException as e:
            print(f"Could not fetch {url}. Reason: {e}")

    # Remove duplicates
    unique_headings = list(set(competitor_headings))

    return {
        "people_also_ask": [q.get("question") for q in people_also_ask],
        "related_searches": related_searches,
        "competitor_headings": unique_headings,
    }

def generate_blog_post(keyword: str, research_data: dict):
    """
    Calls OpenAI to generate a blog post based on the SEO research.
    """
    print(f"🤖 Generating blog post with OpenAI for keyword: {keyword}")

    # Step 3: Build the "Super Prompt"
    prompt = f"""
    You are an expert SEO content writer. Your task is to write a blog post with a stuctured html.

    Primary Keyword: "{keyword}"

    Structure Requirements:
    - Create a compelling, SEO-friendly title.
    - Write a brief introduction that hooks the reader.
    - Write 3-5 main sections using H2 headings.
    - Write a concluding summary.
    - The tone should be helpful, informative, and slightly casual.

    Content Requirements:
    - The post must be comprehensive and well-researched.
    - Directly answer the following "People Also Ask" questions within the content:
      - {', '.join(research_data['people_also_ask'])}
    
    - Draw inspiration from the following topics and headings found on competing pages. Try to cover similar themes to ensure the article is comprehensive:
      - {', '.join(research_data['competitor_headings'])}
      
    - Naturally include some of these related keywords:
      - {', '.join(research_data['related_searches'])}

    Affiliate Link Placeholder:
    - Where it makes sense to recommend a product or service, insert a placeholder in this exact format: [Product Name - Affiliate Link Here]. Insert at least 2-3 of these placeholders.

    Now, please write the blog post draft.
    """

    response = client.chat.completions.create(
        model="gpt-4o", # Or "gpt-3.5-turbo" for faster/cheaper results
        messages=[
            {"role": "system", "content": "You are an expert SEO content writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

def run_full_generation_process(keyword: str):
    """A wrapper function to run the whole process."""
    try:
        research = perform_seo_research(keyword)
        post_content = generate_blog_post(keyword, research)
        
        # In a real app, you would save this to a database
        print("\n--- GENERATED BLOG POST ---\n")
        print(post_content)
        print("\n--- END OF POST ---\n")
        return post_content
    except Exception as e:
        print(f"An error occurred during generation for '{keyword}': {e}")
        return None

# --- DAILY SCHEDULER ---

# List of keywords for the daily cron job
PREDEFINED_KEYWORDS = [
    "best coffee maker for home",
    "how to start a vegetable garden",
    "beginners guide to python programming"
]
# We'll use a simple index to cycle through keywords daily
keyword_index = 0

def daily_post_job():
    """The function that will be called by the scheduler."""
    global keyword_index
    print("\n🚀 Kicking off daily automated post generation...")
    
    # Get the next keyword from the list, cycling back to the start if needed
    keyword = PREDEFINED_KEYWORDS[keyword_index % len(PREDEFINED_KEYWORDS)]
    keyword_index += 1
    
    run_full_generation_process(keyword)


# --- FLASK ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if flask_request.method == 'POST':
        keyword = flask_request.form['keyword']
        if keyword:
            research_data = perform_seo_research(keyword)
            post_content = generate_blog_post(keyword, research_data)
            return render_template('post.html', post=post_content, keyword=keyword)
    return render_template('index.html')


if __name__ == '__main__':
    # Setup and start the scheduler
    scheduler = BackgroundScheduler()
    # Schedule daily_post_job to run once a day. For testing, you can change 'days' to 'seconds'
    scheduler.add_job(daily_post_job, 'interval', days=1) 
    scheduler.start()
    
    print("Scheduler started. It will generate a post once per day.")
    print("Starting Flask app... Open http://127.0.0.1:5000 in your browser.")
    
    # Run the Flask app
    # use_reloader=False is important to prevent the scheduler from running twice
    app.run(debug=True, use_reloader=False)