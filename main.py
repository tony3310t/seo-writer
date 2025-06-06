from fastapi import FastAPI, Query
from writer import crawl_article_tree

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "AI SEO Writer is ready."}

@app.get("/run")
def run_task(
    keyword: str = Query(..., description="主關鍵字"),
    depth: int = Query(2, description="遞迴延伸層數")
):
    crawl_article_tree(keyword, max_depth=depth)
    return {
        "status": "done",
        "keyword": keyword,
        "depth": depth,
        "message": f"已完成 SEO 文章遞迴產生（{keyword}，延伸 {depth} 層）"
    }
