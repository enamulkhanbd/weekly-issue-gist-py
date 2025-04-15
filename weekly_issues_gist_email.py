from dotenv import load_dotenv
load_dotenv()

import requests
from datetime import datetime
import smtplib
from email.message import EmailMessage
import os

# CONFIGURATION
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
REPO = "enamulkhanbd/weekly-issue-gist-py"
DEVELOPER_EMAIL = ["fuhadhasan472@gmail.com, fuhadhasan479@gmail.com"]
SENDER_EMAIL = "hometv.ipa@gmail.com"
SENDER_EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']  # Use App Password for Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def get_last_week_issues():
    # one_week_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).isoformat() + "Z"
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
    url = f"https://api.github.com/repos/{REPO}/issues"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"since": today_start, "state": "all"}

    response = requests.get(url, headers=headers, params=params)

    response.raise_for_status()
    return response.json()

def create_gist(issues):
    content = "\n\n".join([
        f"#{i['number']} - {i['title']}\n{(i['body'] or '').strip()}\nStatus: {i['state']}\nUpdated: {i['updated_at']}\nURL: {i['html_url']}"
        for i in issues if 'pull_request' not in i  # exclude PRs
    ])
    
    if not content:
        content = "No issues updated in the past week."

    payload = {
        "description": "Weekly GitHub Issue Summary",
        "public": True,
        "files": {
            "weekly_issues.md": {
                "content": content
            }
        }
    }
    response = requests.post("https://api.github.com/gists", json=payload, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    response.raise_for_status()
    return response.json()["html_url"]

def send_email(gist_url):
    msg = EmailMessage()
    msg["Subject"] = "📝 Weekly GitHub Issue Summary"
    msg["From"] = SENDER_EMAIL
    msg["To"] = DEVELOPER_EMAIL
    msg.set_content(f"Hello Dev,\n\nHere's the weekly GitHub issue summary:\n\n{gist_url}\n\nCheers!")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_EMAIL_PASSWORD)
        server.send_message(msg)

def main():
    issues = get_last_week_issues()
    gist_url = create_gist(issues)
    send_email(gist_url)
    print(f"Gist created: {gist_url}")

if __name__ == "__main__":
    main()
