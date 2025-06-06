import os
import time
from dotenv import load_dotenv
from google import genai
from datetime import datetime
from typing import Set

load_dotenv()
genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-1.5-flash"

def notify(keyword):
    with open("notify.log", "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now().isoformat()}] 完成：{keyword}\n")

def generate_title(keyword):
    prompt = f"請根據關鍵字「{keyword}」，撰寫一行吸引人的 SEO 部落格文章標題，請直接給我標題就好，不要多餘解釋或開場語。"
    res = genai_client.models.generate_content(model=MODEL, contents=prompt)
    time.sleep(10)
    return res.text.strip()

def generate_pre(keyword):
    prompt = f"針對「{keyword}」，請產生一份部落格文章的引言，不要多餘解釋或開場語。"
    res = genai_client.models.generate_content(model=MODEL, contents=prompt)
    time.sleep(10)
    return f"<h2>引言</h2>\n<p>{res.text.strip()}</p>"

def generate_outline(keyword):
    prompt = f"針對「{keyword}」，請產生一份部落格文章的目錄清單，限4個小標題。請只回傳小標題本身，不要多餘解釋或開場語。請用 | 符號分隔各個小標題"
    res = genai_client.models.generate_content(model=MODEL, contents=prompt)
    time.sleep(10)
    return [part.strip() for part in res.text.strip().split("|") if part.strip()]

def generate_section(subtitle, keyword):
    prompt = f"請針對部落格文章中的段落「{subtitle}」撰寫約200字的內容，主題為「{keyword}」，請使用繁體中文，不要多餘解釋或開場語。"
    res = genai_client.models.generate_content(model=MODEL, contents=prompt)
    time.sleep(10)
    return f"<h2>{subtitle}</h2>\n<p>{res.text.strip()}</p>"

def generate_qa(context):
    prompt = f"根據以下文章內容，請撰寫 3 個與主題相關的常見問題與簡要回答，格式為 Q:... A:...，不要多餘解釋或開場語\n\n{context}"
    res = genai_client.models.generate_content(model=MODEL, contents=prompt)
    time.sleep(10)
    return "<h2>常見問題 Q&A</h2>\n" + "\n".join([f"<p>{line}</p>" for line in res.text.strip().splitlines()])

def generate_conclusion(context):
    prompt = f"根據以下文章內容，請撰寫一段總結結論，強調主題價值與推薦。，不要多餘解釋或開場語\n\n{context}"
    res = genai_client.models.generate_content(model=MODEL, contents=prompt)
    time.sleep(10)
    return f"<h2>結論</h2>\n<p>{res.text.strip()}</p>"

def generate_full_article(keyword):
    print(f"\n🚀 產生文章：「{keyword}」")
    title = generate_title(keyword)
    pre = generate_pre(keyword)
    outline = generate_outline(keyword)
    sections = []
    for sub in outline:
        print(f"✍️ 撰寫段落：「{sub}」")
        sections.append(generate_section(sub, keyword))
    context = "\n".join(sections)
    qa = generate_qa(context)
    conclusion = generate_conclusion(context)
    full_html = f"<h1>{title}</h1>\n" + pre + "\n".join(sections) + "\n" + qa + "\n" + conclusion
    notify(keyword)
    return full_html, outline

def crawl_article_tree(keyword: str, max_depth: int = 2, current_depth: int = 0, visited: Set[str] = None):
    if visited is None:
        visited = set()
    if current_depth >= max_depth or keyword in visited:
        return {}

    visited.add(keyword)
    article_html, outline = generate_full_article(keyword)

    filename = f"article_d{current_depth}_{keyword}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(article_html)

    result = {}
    for sub in outline:
        if sub not in visited:
            result[sub] = crawl_article_tree(sub, max_depth, current_depth + 1, visited)
    return result
