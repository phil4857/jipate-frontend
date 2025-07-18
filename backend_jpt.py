backend_jpt.py

from fastapi import FastAPI, Form, HTTPException, Depends from fastapi.middleware.cors import CORSMiddleware from pydantic import BaseModel from datetime import datetime, timedelta import uuid

app = FastAPI()

Enable CORS (for frontend communication)

app.add_middleware( CORSMiddleware, allow_origins=[""], allow_credentials=True, allow_methods=[""], allow_headers=["*"], )

In-memory storage

users = {} investments = [] pending_users = [] pending_investments = [] referrals = {} earnings = {}

Models

class User(BaseModel): username: str password: str referred_by: str = None

class Investment(BaseModel): username: str amount: float

@app.get("/") def root(): return {"message": "Welcome to Jipate Bonus"}

@app.post("/register") def register(username: str = Form(...), password: str = Form(...), referred_by: str = Form(None)): if username in users: raise HTTPException(status_code=400, detail="User already exists")

joining_fee = 1000
today = datetime.now().strftime('%A')
if today == "Sunday":
    joining_fee *= 0.95  # 5% discount

users[username] = {"password": password, "approved": False, "balance": 0, "joined": datetime.now()}
pending_users.append(username)

if referred_by and referred_by in users:
    referrals[username] = referred_by

return {"message": f"User registered successfully. Fee: {joining_fee}"}

@app.post("/login") def login(username: str = Form(...), password: str = Form(...)): user = users.get(username) if not user or user["password"] != password: raise HTTPException(status_code=401, detail="Invalid credentials") if not user["approved"]: raise HTTPException(status_code=403, detail="User not approved yet") return {"message": "Login successful"}

@app.post("/invest") def invest(username: str = Form(...), amount: float = Form(...)): if username not in users or not users[username]["approved"]: raise HTTPException(status_code=403, detail="User not approved") pending_investments.append({"username": username, "amount": amount, "date": datetime.now()}) return {"message": "Investment submitted and pending approval"}

@app.post("/admin/approve_user") def approve_user(username: str = Form(...)): if username in pending_users: users[username]["approved"] = True pending_users.remove(username) return {"message": f"{username} approved"} raise HTTPException(status_code=404, detail="User not found or already approved")

@app.post("/admin/approve_investment") def approve_investment(username: str = Form(...)): for inv in pending_investments: if inv["username"] == username: investments.append(inv) users[username]["balance"] += inv["amount"] # Referral bonus if username in referrals: referrer = referrals[username] users[referrer]["balance"] += inv["amount"] * 0.05 pending_investments.remove(inv) return {"message": f"Investment approved for {username}"} raise HTTPException(status_code=404, detail="Investment not found")

@app.get("/earnings/daily") def daily_earnings(): today = datetime.now().strftime('%Y-%m-%d') if today in earnings: return {"message": "Earnings already distributed today"}

for user, data in users.items():
    if data["approved"]:
        daily_earning = data["balance"] * 0.10
        users[user]["balance"] += daily_earning
earnings[today] = True
return {"message": "Daily earnings distributed"}

@app.post("/withdraw") def withdraw(username: str = Form(...), amount: float = Form(...)): if username not in users or not users[username]["approved"]: raise HTTPException(status_code=403, detail="User not approved") if users[username]["balance"] < amount: raise HTTPException(status_code=400, detail="Insufficient balance") users[username]["balance"] -= amount return {"message": f"Withdrawal of {amount} successful"}

@app.get("/admin/view_users") def view_users(): return users

