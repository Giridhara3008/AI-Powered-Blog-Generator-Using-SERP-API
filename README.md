## AI-Powered Blog Generator Using SERP API

This project is an AI-powered blog post generator built with **Flask**, **OpenAI GPT-4**, **SerpAPI**, and **BeautifulSoup**. It automates SEO research and generates structured, high-quality blog posts with affiliate link placeholders.

##  Features

**SEO Research with SerpAPI**
Pulls "People Also Ask", related searches, and top competitor headings.
  
**Blog Post Generation with OpenAI**
Creates a well-structured post with title, intro, 3–5 H2s, conclusion, and affiliate placeholders.
  
**Web Interface**
Simple Flask frontend to submit keywords and view generated posts.
  
**Daily Post Automation**
Uses APScheduler to auto-generate one blog post daily from a list of predefined keywords.
##  Tech Stack
- Python 3.9+
- Flask
- OpenAI GPT-4
- SerpAPI
- BeautifulSoup
- APScheduler
- Markdown
- Requests
##  Installation
### 1. Clone the Repo
bash
git clone https://github.com/yourusername/ai-blog-generator.git
cd ai-blog-generator

## Project Structure
ai-blog-generator/
 templates/
  index.html       # Input form
  post.html        # Display generated post
 app.py               # Main Flask app with routing, logic, scheduler
 .env                 # API keys (not tracked)
 requirements.txt     # Python dependencies
 README.md
 ## Steps to do the project 
 Install all requirements.txt and set up python virtual environment using venv.
 Built all required codes in app.py and run in the localhost.
 ### For running use the link 
 http://127.0.0.1:5000

 ## Conclusion
 This project demonstrates how automation, AI, and SEO tools can come together to create a powerful content generation system. By integrating OpenAI for text generation and SerpAPI for live SEO data, we built a blog generator that produces highly relevant and optimized blog posts with minimal manual input.
 ## Knowledge gained
 learned how to combine AI with live SEO data to build a smart, automated blogging tool. More importantly, you gained the ability to engineer systems that solve real-world problems using modern technologies.







