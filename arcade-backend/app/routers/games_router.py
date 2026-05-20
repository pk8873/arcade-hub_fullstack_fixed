"""Games + leaderboard routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.game_model import GameScore
from app.models.user_model import User
from app.schemas import LeaderboardRow, ScoreOut, ScoreSubmit
from app.security import get_current_user, require_verified
from app.services.wallet_service import credit

router = APIRouter()

# Whitelist of supported games (extend as you add more)
SUPPORTED_GAMES = {"fruit_slice", "memory_match", "tic_tac_toe", "2048"}

# Reward formula: 1 coin per 100 points, capped per submission
def _reward_for(score: int) -> int:
    return min(score // 100, 200)


@router.get("/list")
def list_games():
    return [
        {"key": "fruit_slice", "title": "Fruit Slice", "tagline": "Slice fruit, dodge bombs."},
    ]


@router.post("/score", response_model=ScoreOut)
def submit_score(
    payload: ScoreSubmit,
    user: User = Depends(require_verified),
    db: Session = Depends(get_db),
):
    if payload.game_key not in SUPPORTED_GAMES:
        raise HTTPException(400, "Unknown game")
    # Basic anti-cheat: if duration provided, enforce a max points-per-second
    if payload.duration_seconds and payload.duration_seconds > 0:
        pps = payload.score / payload.duration_seconds
        if pps > 500:
            raise HTTPException(400, "Score rejected (rate too high)")
    row = GameScore(
        user_id=user.id,
        game_key=payload.game_key,
        score=payload.score,
        duration_seconds=payload.duration_seconds,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    reward = _reward_for(payload.score)
    if reward > 0:
        credit(db, user, reward, "game_reward", f"{payload.game_key} score {payload.score}")
    return row


@router.get("/leaderboard/{game_key}", response_model=list[LeaderboardRow])
def leaderboard(game_key: str, db: Session = Depends(get_db), limit: int = 20):
    if game_key not in SUPPORTED_GAMES:
        raise HTTPException(400, "Unknown game")
    # Best score per user
    sub = (
        db.query(GameScore.user_id, func.max(GameScore.score).label("best"))
        .filter(GameScore.game_key == game_key)
        .group_by(GameScore.user_id)
        .subquery()
    )
    rows = (
        db.query(User.username, sub.c.best, func.max(GameScore.created_at))
        .join(sub, sub.c.user_id == User.id)
        .join(GameScore, (GameScore.user_id == User.id) & (GameScore.score == sub.c.best) & (GameScore.game_key == game_key))
        .group_by(User.username, sub.c.best)
        .order_by(sub.c.best.desc())
        .limit(min(limit, 100))
        .all()
    )
    return [LeaderboardRow(username=u, score=s, created_at=c) for (u, s, c) in rows]


@router.get("/my-scores", response_model=list[ScoreOut])
def my_scores(user: User = Depends(get_current_user), db: Session = Depends(get_db), limit: int = 50):
    return (
        db.query(GameScore)
        .filter(GameScore.user_id == user.id)
        .order_by(GameScore.created_at.desc())
        .limit(min(limit, 200))
        .all()
    )
