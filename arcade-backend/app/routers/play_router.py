"""Sky Climb (crash), Flash Duel (quiz), Pitch Stocks (player shares)."""
import hashlib, math, random, time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_model import User
from app.models.play_model import CrashRound, QuizResult, StockHolding
from app.models.wallet_model import Wallet
from app.security import require_verified
from app.services.wallet_service import credit, debit, get_or_create_wallet

router = APIRouter()

# ---------- Sky Climb (crash multiplier) ----------

def _crash_point(seed: str) -> float:
    h = int(hashlib.sha256(seed.encode()).hexdigest()[:13], 16)
    e = 2 ** 52
    if h % 33 == 0:
        return 1.00
    return max(1.00, math.floor((100 * e - h) / (e - h)) / 100)


class SkyBet(BaseModel):
    bet: int = Field(ge=1, le=10000)
    cashout_at: float = Field(ge=1.01, le=100.0)


@router.post("/skyclimb/round")
def sky_round(payload: SkyBet, user: User = Depends(require_verified), db: Session = Depends(get_db)):
    w = get_or_create_wallet(db, user)
    if w.balance < payload.bet:
        raise HTTPException(400, "Insufficient coins")
    debit(db, user, payload.bet, "skyclimb_bet")
    seed = f"{user.id}:{time.time_ns()}:{random.random()}"
    crash = _crash_point(seed)
    won = payload.cashout_at <= crash
    payout = int(payload.bet * payload.cashout_at) if won else 0
    if payout > 0:
        credit(db, user, payout, "skyclimb_win", f"x{payload.cashout_at} (crash {crash})")
    row = CrashRound(user_id=user.id, bet=payload.bet, cashout_at=payload.cashout_at,
                     crash_at=crash, payout=payout, won=won)
    db.add(row); db.commit()
    db.refresh(w)
    return {"crash_at": crash, "won": won, "payout": payout, "balance": w.balance}


@router.get("/skyclimb/history")
def sky_history(user: User = Depends(require_verified), db: Session = Depends(get_db)):
    rows = db.query(CrashRound).filter(CrashRound.user_id == user.id)\
        .order_by(CrashRound.created_at.desc()).limit(20).all()
    return [{"crash_at": r.crash_at, "cashout_at": r.cashout_at, "bet": r.bet,
             "payout": r.payout, "won": r.won, "at": r.created_at} for r in rows]


# ---------- Flash Duel (multiplayer quiz) ----------

QUESTION_BANK = [
    {"q": "Capital of Australia?", "a": ["Sydney", "Melbourne", "Canberra", "Perth"], "c": 2},
    {"q": "2^10 = ?", "a": ["1000", "1024", "2048", "512"], "c": 1},
    {"q": "Largest ocean?", "a": ["Atlantic", "Indian", "Arctic", "Pacific"], "c": 3},
    {"q": "Author of Hamlet?", "a": ["Dickens", "Shakespeare", "Austen", "Twain"], "c": 1},
    {"q": "Speed of light (km/s)?", "a": ["3,000", "30,000", "300,000", "3,000,000"], "c": 2},
    {"q": "Chemical symbol for gold?", "a": ["Go", "Gd", "Au", "Ag"], "c": 2},
    {"q": "Pi to 2 decimals?", "a": ["3.12", "3.14", "3.16", "3.18"], "c": 1},
    {"q": "Smallest prime?", "a": ["0", "1", "2", "3"], "c": 2},
    {"q": "Currency of Japan?", "a": ["Yuan", "Won", "Yen", "Ringgit"], "c": 2},
    {"q": "Tallest mountain?", "a": ["K2", "Kangchenjunga", "Everest", "Lhotse"], "c": 2},
    {"q": "Cricket bat material?", "a": ["Pine", "Oak", "Willow", "Maple"], "c": 2},
    {"q": "Continent of Egypt?", "a": ["Asia", "Africa", "Europe", "S. America"], "c": 1},
]


@router.get("/flashduel/start")
def flash_start():
    qs = random.sample(QUESTION_BANK, 5)
    return [{"id": i, "q": q["q"], "a": q["a"]} for i, q in enumerate(qs)] , [q["c"] for q in qs]


@router.get("/flashduel/questions")
def flash_questions():
    qs = random.sample(QUESTION_BANK, 5)
    return {"session": hashlib.sha256(str(random.random()).encode()).hexdigest()[:16],
            "questions": [{"id": i, "q": q["q"], "a": q["a"], "_c": q["c"]} for i, q in enumerate(qs)]}


class FlashSubmit(BaseModel):
    answers: list[int]
    correct_key: list[int]
    avg_ms: int = Field(ge=0, le=120000)


@router.post("/flashduel/submit")
def flash_submit(payload: FlashSubmit, user: User = Depends(require_verified), db: Session = Depends(get_db)):
    if len(payload.answers) != len(payload.correct_key) or not payload.correct_key:
        raise HTTPException(400, "Invalid submission")
    correct = sum(1 for a, c in zip(payload.answers, payload.correct_key) if a == c)
    total = len(payload.correct_key)
    speed_bonus = max(0, 5000 - payload.avg_ms) // 50
    score = correct * 100 + speed_bonus
    reward = correct * 5
    if reward:
        credit(db, user, reward, "flashduel_reward", f"{correct}/{total}")
    row = QuizResult(user_id=user.id, correct=correct, total=total, avg_ms=payload.avg_ms, score=score)
    db.add(row); db.commit()
    return {"correct": correct, "total": total, "score": score, "coins_awarded": reward}


@router.get("/flashduel/leaderboard")
def flash_board(db: Session = Depends(get_db)):
    rows = db.query(QuizResult, User).join(User, User.id == QuizResult.user_id)\
        .order_by(QuizResult.score.desc()).limit(20).all()
    return [{"username": u.username, "score": r.score, "correct": r.correct,
             "total": r.total, "at": r.created_at} for r, u in rows]


# ---------- Pitch Stocks (cricket player shares) ----------

PLAYERS = [
    {"key": "rohan_kapoor", "name": "Rohan Kapoor", "role": "Batsman", "base": 50},
    {"key": "vihaan_iyer",  "name": "Vihaan Iyer",  "role": "All-rounder", "base": 65},
    {"key": "aarav_singh",  "name": "Aarav Singh",  "role": "Bowler", "base": 40},
    {"key": "kabir_mehra",  "name": "Kabir Mehra",  "role": "Wicket-keeper", "base": 55},
    {"key": "dev_rana",     "name": "Dev Rana",     "role": "Batsman", "base": 75},
    {"key": "arjun_pillai", "name": "Arjun Pillai", "role": "Bowler", "base": 45},
    {"key": "neel_varma",   "name": "Neel Varma",   "role": "All-rounder", "base": 60},
    {"key": "ishan_dube",   "name": "Ishan Dube",   "role": "Batsman", "base": 70},
]


def _price(p) -> float:
    # Deterministic price per 30s tick, sinusoidal +/- 30%
    tick = int(time.time() // 30)
    h = int(hashlib.sha256(f"{p['key']}:{tick}".encode()).hexdigest()[:8], 16)
    swing = ((h % 1000) / 1000.0 - 0.5) * 0.6  # -0.30..+0.30
    return round(p["base"] * (1 + swing), 2)


@router.get("/stocks/players")
def stocks_players():
    return [{**p, "price": _price(p)} for p in PLAYERS]


class StockTrade(BaseModel):
    player_key: str
    shares: int = Field(ge=1, le=1000)


def _find_player(key):
    for p in PLAYERS:
        if p["key"] == key: return p
    raise HTTPException(404, "Unknown player")


@router.post("/stocks/buy")
def stocks_buy(payload: StockTrade, user: User = Depends(require_verified), db: Session = Depends(get_db)):
    p = _find_player(payload.player_key)
    price = _price(p)
    cost = int(round(price * payload.shares))
    w = get_or_create_wallet(db, user)
    if w.balance < cost:
        raise HTTPException(400, "Insufficient coins")
    debit(db, user, cost, "stocks_buy", f"{payload.shares} {p['name']} @ {price}")
    h = db.query(StockHolding).filter(StockHolding.user_id == user.id,
                                      StockHolding.player_key == payload.player_key).first()
    if not h:
        h = StockHolding(user_id=user.id, player_key=payload.player_key, shares=0, avg_cost=0)
        db.add(h)
    total_cost = h.avg_cost * h.shares + cost
    h.shares += payload.shares
    h.avg_cost = total_cost / h.shares
    db.commit()
    return {"ok": True, "cost": cost, "price": price, "shares": h.shares}


@router.post("/stocks/sell")
def stocks_sell(payload: StockTrade, user: User = Depends(require_verified), db: Session = Depends(get_db)):
    p = _find_player(payload.player_key)
    h = db.query(StockHolding).filter(StockHolding.user_id == user.id,
                                      StockHolding.player_key == payload.player_key).first()
    if not h or h.shares < payload.shares:
        raise HTTPException(400, "Not enough shares")
    price = _price(p)
    proceeds = int(round(price * payload.shares))
    h.shares -= payload.shares
    if h.shares == 0: h.avg_cost = 0
    db.commit()
    credit(db, user, proceeds, "stocks_sell", f"{payload.shares} {p['name']} @ {price}")
    return {"ok": True, "proceeds": proceeds, "price": price, "shares_left": h.shares}


@router.get("/stocks/portfolio")
def stocks_portfolio(user: User = Depends(require_verified), db: Session = Depends(get_db)):
    rows = db.query(StockHolding).filter(StockHolding.user_id == user.id, StockHolding.shares > 0).all()
    out = []
    for h in rows:
        p = _find_player(h.player_key)
        price = _price(p)
        out.append({"player_key": h.player_key, "name": p["name"], "role": p["role"],
                    "shares": h.shares, "avg_cost": round(h.avg_cost, 2),
                    "price": price, "value": round(price * h.shares, 2),
                    "pnl": round((price - h.avg_cost) * h.shares, 2)})
    return out


@router.get("/list")
def list_games():
    return [
        {"key": "skyclimb", "title": "Sky Climb", "tagline": "Cash out before the crash."},
        {"key": "flashduel", "title": "Flash Duel", "tagline": "Speed quiz vs. the leaderboard."},
        {"key": "stocks", "title": "Pitch Stocks", "tagline": "Trade shares in cricket players."},
    ]
