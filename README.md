# 🧠 Reddit Persona

This project (`Reddit Persona`) extracts a detailed **user persona** from any public Reddit profile by analyzing their posts and comments using OpenAI’s GPT API.

Outputs include:
- 📄 A `.txt` file with structured persona data (JSON-style)
- 🧾 A `.pdf` file formatted for presentation or reports
- 🔍 Each insight includes source citations from Reddit

---

## 🚀 Features

- 🔍 Scrapes public Reddit comments & posts
- 🧠 Uses OpenAI to generate a structured persona
- 📌 Includes citations for each personality insight
- 📄 Saves both `.txt` and `.pdf` outputs
- ⚙️ Easily configured via a `.env` file

---

## 🛠️ Setup Instructions

### 1. ✅ Prerequisites

- Python 3.8+
- Reddit API credentials (create at https://www.reddit.com/prefs/apps)
- OpenAI API key (https://platform.openai.com/account/api-keys)

---

### 2. 🔧 Install Dependencies

```bash
git clone https://github.com/sohamMKRG/Reddit-Persona-.git
pip install -r requirements.txt
