from fastapi import FastAPI, Query
from writer import generate_full_article, upload_to_hastebin

app = FastAPI()

@app.get("/run")
def run_article(keyword: str = Query(..., description="輸入關鍵字")):
    try:
        title, html = generate_full_article(keyword)
        url = upload_to_pastegg(html)
        return {
            "keyword": keyword,
            "title": title,
            "status": "success",
            "url": url
        }
    except Exception as e:
        return {
            "keyword": keyword,
            "status": "error",
            "message": str(e)
        }