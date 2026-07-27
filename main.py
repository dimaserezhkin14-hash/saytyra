import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

# База данных тестовых карточек
items_db = [
    {
        "id": 1,
        "title": "Cyberpunk Beat 140 BPM",
        "author": "@art1make",
        "image": "https://picsum.photos/400/300?random=1",
        "likes": 12,
        "dislikes": 2
    },
    {
        "id": 2,
        "title": "8-Bit Chiptune Horror",
        "author": "@producer_x",
        "image": "https://picsum.photos/400/300?random=2",
        "likes": 34,
        "dislikes": 1
    },
    {
        "id": 3,
        "title": "Acid Glitch Art v2",
        "author": "@pixel_hero",
        "image": "https://picsum.photos/400/300?random=3",
        "likes": 89,
        "dislikes": 5
    }
]

class VoteRequest(BaseModel):
    item_id: int
    action: str
    user_id: int

@app.get("/")
async def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    raise HTTPException(status_code=404, detail="index.html not found")

@app.get("/api/items")
async def get_items():
    return {"items": items_db}

@app.post("/api/vote")
async def vote(data: VoteRequest):
    for item in items_db:
        if item["id"] == data.item_id:
            if data.action == "like":
                item["likes"] += 1
            elif data.action == "dislike":
                item["dislikes"] += 1
            return {"status": "ok", "likes": item["likes"], "dislikes": item["dislikes"]}
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
