# Calories Bot 🤖

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────┐
│  Python 3.11                        │
│  Telegram Bot API                   │
│  OpenAI GPT-3.5 Turbo              │
│  SQLAlchemy ORM                    │
│  SQLite Database                   │
└─────────────────────────────────────┘
```

---

## 📋 Overview

A smart Telegram bot for nutrition tracking and meal analysis. Uses AI to calculate macros, calories, and provide dietary advice based on personal metrics.

---

## ✨ Features

- **User Profiles** – Store height, weight, age, sex, and fitness goals
- **Meal Logging** – Add meals and get instant nutrition analysis
- **Daily Stats** – Track consumption vs. daily calorie targets
- **AI Assistant** – Ask nutrition questions powered by GPT
- **7-Day History** – Review your eating patterns

---

## 🚀 Quick Start

1. **Clone & Setup**
```bash
git clone <repo>
cd calories
pip install -r requirements.txt
```

2. **Configure**
Create `.env` file:
```
TELEGRAM_API_KEY=your_token_here
OPENAI_API_KEY=your_key_here
```

3. **Run**
```bash
python bot.py
```

---

## 📁 Project Structure

```
calories/
├── bot.py                 # Main bot entry point
├── db.py                  # Database models & init
├── meal_analysis.py       # Meal parsing & nutrition
├── openai_utils.py        # GPT integration
├── parameter_handlers.py  # User profile setup
├── utils.py               # Helper functions
├── bot.db                 # SQLite database
└── .env                   # API keys (git ignored)
```

---

## 🔧 Core Modules

| Module | Purpose |
|--------|---------|
| `bot.py` | Telegram conversation handlers, commands |
| `db.py` | SQLAlchemy models, session management |
| `meal_analysis.py` | Meal description parsing & macro calculation |
| `openai_utils.py` | OpenAI API calls |
| `parameter_handlers.py` | User settings input flows |

---

## 🎯 Commands

- `/start` – Launch main menu
- `/help` – View available commands
- `/stats` – Show today's nutrition + 7-day history

---

## 📝 License

MIT

