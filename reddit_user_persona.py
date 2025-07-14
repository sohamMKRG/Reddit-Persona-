import praw
import openai
import re
import json
import os
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# Load environment variables
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Setup APIs
openai.api_key = OPENAI_API_KEY
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

def extract_username(profile_url):
    match = re.search(r'reddit\.com/user/([^/]+)/?', profile_url)
    return match.group(1) if match else None

def scrape_user_content(username, limit=50):
    redditor = reddit.redditor(username)
    posts, comments = [], []
    try:
        for submission in redditor.submissions.new(limit=limit):
            posts.append({
                "title": submission.title,
                "body": submission.selftext,
                "subreddit": str(submission.subreddit),
                "url": submission.url
            })
        for comment in redditor.comments.new(limit=limit):
            comments.append({
                "body": comment.body,
                "subreddit": str(comment.subreddit),
                "url": f"https://www.reddit.com{comment.permalink}"
            })
    except Exception as e:
        print(f"Error fetching user data: {e}")
    return posts, comments

def generate_prompt(posts, comments):
    combined = ""
    count = 1
    for post in posts:
        if post["body"]:
            combined += f"[{count}] Post: {post['title']}\nBody: {post['body']}\nSubreddit: {post['subreddit']}\nURL: {post['url']}\n\n"
            count += 1
    for comment in comments:
        combined += f"[{count}] Comment: {comment['body']}\nSubreddit: {comment['subreddit']}\nURL: {comment['url']}\n\n"
        count += 1

    return f"""
Based on the following Reddit posts and comments, create a user persona as JSON with these fields:
- username
- age
- occupation
- status
- location
- tier
- archetype
- traits (list)
- motivations (dict with 6 keys and values 1-5)
- personality (dict of 8 MBTI-style traits with values 1-5)
- behavior (list of 3-5 habits)
- frustrations (list of 3)
- goals (list of 3)
- quote

Only output valid JSON.

### Reddit Content:
{combined}
"""

def generate_persona(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return json.loads(response['choices'][0]['message']['content'])

def generate_persona_pdf(persona):
    filename = f"{persona['username']}_persona.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    margin = 50

    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.orange)
    c.drawString(margin, height - 60, persona["username"])

    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    facts = [
        f"Age: {persona['age']}",
        f"Occupation: {persona['occupation']}",
        f"Status: {persona['status']}",
        f"Location: {persona['location']}",
        f"Tier: {persona['tier']}",
        f"Archetype: {persona['archetype']}",
    ]
    for i, fact in enumerate(facts):
        c.drawString(margin, height - 90 - i * 15, fact)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, height - 200, "Traits:")
    c.setFont("Helvetica", 11)
    c.drawString(margin + 60, height - 200, ", ".join(persona["traits"]))

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, height - 230, "Motivations:")
    bar_y = height - 245
    for i, (key, val) in enumerate(persona["motivations"].items()):
        c.setFont("Helvetica", 10)
        c.drawString(margin + 10, bar_y - i * 15, key)
        c.setFillColor(colors.grey)
        c.rect(margin + 100, bar_y - 5 - i * 15, 80, 8, fill=0)
        c.setFillColor(colors.orange)
        c.rect(margin + 100, bar_y - 5 - i * 15, val * 16, 8, fill=1)
        c.setFillColor(colors.black)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, height - 360, "Personality:")
    bar_y = height - 375
    for i, (key, val) in enumerate(persona["personality"].items()):
        c.setFont("Helvetica", 10)
        c.drawString(margin + 10, bar_y - i * 15, key)
        c.setFillColor(colors.grey)
        c.rect(margin + 100, bar_y - 5 - i * 15, 80, 8, fill=0)
        c.setFillColor(colors.orange)
        c.rect(margin + 100, bar_y - 5 - i * 15, val * 16, 8, fill=1)
        c.setFillColor(colors.black)

    def draw_bullets(title, items, y_start):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_start, title)
        y = y_start - 15
        c.setFont("Helvetica", 10)
        for item in items:
            c.drawString(margin + 10, y, u"\u2022 " + item)
            y -= 13

    draw_bullets("Behaviour & Habits:", persona["behavior"], height - 500)
    draw_bullets("Frustrations:", persona["frustrations"], height - 620)
    draw_bullets("Goals & Needs:", persona["goals"], height - 720)

    c.setFillColorRGB(1, 0.4, 0.2)
    c.rect(margin, height - 770, width - 2 * margin, 30, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(margin + 10, height - 760, f'“{persona["quote"]}”')

    c.save()
    print(f"✅ PDF saved: {filename}")

def main():
    url = input("Enter Reddit profile URL: ").strip()
    username = extract_username(url)
    if not username:
        print("Invalid URL.")
        return

    print(f"📦 Fetching data for: {username}")
    posts, comments = scrape_user_content(username)
    if not posts and not comments:
        print("No content found.")
        return

    print("🧠 Generating prompt...")
    prompt = generate_prompt(posts, comments)
    print("🤖 Calling OpenAI to generate persona...")
    persona_data = generate_persona(prompt)
    generate_persona_pdf(persona_data)

if __name__ == "__main__":
    main()
