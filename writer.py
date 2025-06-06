import os
import time
from dotenv import load_dotenv
from google import genai
import requests

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-1.5-flash"
genai_client = genai.Client(api_key=API_KEY)

def upload_to_pastegg(content: str, title="SEO文章") -> str:
    payload = {
        "name": title,
        "files": [
            {
                "name": "article.html",
                "content": {
                    "format": "text",
                    "value": content
                }
            }
        ]
    }
    res = requests.post("https://api.paste.gg/v1/pastes", json=payload)
    if res.status_code == 201:
        return res.json()["result"]["url"]
    else:
        return f"PasteGG Upload Failed: {res.status_code} - {res.text}"

def generate_content(prompt: str) -> str:
    res = genai_client.models.generate_content(model=MODEL, contents=prompt)
    time.sleep(10)
    return res.text.strip()

def generate_title(keyword: str) -> str:
    prompt = f"請根據關鍵字「{keyword}」，撰寫一行吸引人的 SEO 部落格文章標題，請直接給我標題就好。"
    return generate_content(prompt)

def generate_pre(keyword: str) -> str:
    prompt = f"針對「{keyword}」，請撰寫一段引言，不要多餘解釋。"
    return f"<h2>引言</h2>\n<p>{generate_content(prompt)}</p>"

def generate_outline(keyword: str) -> list:
    prompt = f"針對「{keyword}」，請產生一份部落格文章的目錄，限4個小標題，用 | 分隔，勿解釋。"
    raw = generate_content(prompt)
    return [part.strip() for part in raw.split("|") if part.strip()]

def generate_section(subtitle: str, keyword: str) -> str:
    prompt = f"請針對「{subtitle}」撰寫 200 字段落，主題「{keyword}」，用繁體中文。"
    return f"<h2>{subtitle}</h2>\n<p>{generate_content(prompt)}</p>"

def generate_qa(context: str) -> str:
    prompt = f"根據以下內容撰寫 3 個常見問題與簡答，格式為 Q:... A:...\n\n{context}"
    lines = generate_content(prompt).splitlines()
    return "<h2>常見問題 Q&A</h2>\n" + "\n".join([f"<p>{line}</p>" for line in lines])

def generate_conclusion(context: str) -> str:
    prompt = f"根據以下內容撰寫一段總結，強調主題價值。\n\n{context}"
    return f"<h2>結論</h2>\n<p>{generate_content(prompt)}</p>"

def generate_full_article(keyword: str) -> tuple[str, str]:
    title = generate_title(keyword)
    pre = generate_pre(keyword)
    outline = generate_outline(keyword)

    sections = []
    for sub in outline:
        sections.append(generate_section(sub, keyword))

    context = "\n".join(sections)
    qa = generate_qa(context)
    conclusion = generate_conclusion(context)

    html = f"<h1>{title}</h1>\n{pre}\n{''.join(sections)}\n{qa}\n{conclusion}"
    return title, html