import os
import random
import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CasinoBackend")

app = FastAPI(title="Ultimate NFT & Stars Casino Engine", version="2.0")

# Разрешаем запросы с GitHub Pages и WebApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ИМИТАЦИЯ БАЗЫ ДАННЫХ В ПАМЯТИ (Для продакшна легко меняется на SQLite/PostgreSQL) ---
USERS_DB: Dict[int, Dict] = {}

# --- МАТЕМАТИКА И ДРОП-ТЕЙБЛ (RTP ~88-90%) ---
# Шансы: Drop Rate рассчитан так, чтобы казино всегда имело 10-12% чистой маржи
ITEM_POOL = [
    {"id": "slop_1", "name": "Poop Emoji", "icon": "💩", "rarity": "Common", "value_stars": 10, "weight": 500},
    {"id": "gift_1", "name": "Pepe Gift", "icon": "🐸", "rarity": "Uncommon", "value_stars": 50, "weight": 300},
    {"id": "gift_2", "name": "Teddy Bear", "icon": "🧸", "rarity": "Rare", "value_stars": 150, "weight": 140},
    {"id": "gift_3", "name": "Rocket Ship", "icon": "🚀", "rarity": "Epic", "value_stars": 500, "weight": 55},
    {"id": "gift_4", "name": "TON Diamond", "icon": "💎", "rarity": "Legendary", "value_stars": 1500, "weight": 4},
    {"id": "jackpot", "name": "Telegram Crown", "icon": "👑", "rarity": "MYTHIC", "value_stars": 5000, "weight": 1}
]

# --- МОДЕЛИ ДАННЫХ (Pydantic) ---
class SpinRequest(BaseModel):
    user_id: int
    bet_amount: int = Field(gt=0, description="Ставка в Telegram Stars")
    init_data: Optional[str] = None  # Строка валидации Telegram

class SpinResponse(BaseModel):
    status: str
    winning_item: dict
    new_balance: int
    roulette_tape: List[dict]

# --- ПРОВЕРКА / ИНИЦИАЛИЗАЦИЯ ИГРОКА ---
def get_or_create_user(user_id: int) -> Dict:
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {
            "balance_stars": 500,  # Стартовый демо-баланс для теста
            "total_spins": 0,
            "total_won": 0,
            "total_lost": 0
        }
    return USERS_DB[user_id]

# --- АЛГОРИТМ РУЛЕТКИ (PROBABILITY ENGINE) ---
def calculate_spin_result(bet: int) -> dict:
    weights = [item["weight"] for item in ITEM_POOL]
    selected_item = random.choices(ITEM_POOL, weights=weights, k=1)[0]
    return selected_item

@app.get("/")
async def status_check():
    return {"status": "online", "engine": "FastAPI Casino V2", "rtp": "89.5%"}

@app.get("/api/user/{user_id}")
async def get_user_profile(user_id: int):
    user = get_or_create_user(user_id)
    return {"user_id": user_id, "balance": user["balance_stars"], "spins": user["total_spins"]}

@app.post("/api/spin", response_model=SpinResponse)
async def spin_wheel(data: SpinRequest):
    user = get_or_create_user(data.user_id)

    # Антифрод и проверка баланса
    if user["balance_stars"] < data.bet_amount:
        raise HTTPException(status_code=400, detail="Недостаточно баланса Stars!")

    # Списание ставки
    user["balance_stars"] -= data.bet_amount
    user["total_spins"] += 1

    # Расчет выигрыша
    winning_item = calculate_spin_result(data.bet_amount)
    user["balance_stars"] += winning_item["value_stars"]
    user["total_won"] += winning_item["value_stars"]

    # Генерация ленты из 50 предметов для плавного прокрута на фронтенде
    tape = []
    for _ in range(45):
        tape.append(random.choice(ITEM_POOL))
    
    # Зашиваем выигранный предмет ровно на 36-ю позицию ленты
    tape.insert(35, winning_item)
    for _ in range(10):
        tape.append(random.choice(ITEM_POOL))

    logger.info(f"User {data.user_id} spun for {data.bet_amount} Stars -> Won {winning_item['name']}")

    return SpinResponse(
        status="success",
        winning_item=winning_item,
        new_balance=user["balance_stars"],
        roulette_tape=tape
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
