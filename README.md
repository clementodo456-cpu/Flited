# 🤖 Telegram Task Manager Bot (@flitedstbot)

A complete, production-ready Telegram Task Manager Bot built using Python and `python-telegram-bot`.

---

## 🚀 Features
* ➕ **Task Creation Conversation:** Set title, description, priority, category, due date/time, and recurrence.
* 📅 **Flexible Date Parsing:** Supports `today`, `tomorrow`, `20 Aug 2026`, `25/08/2026`.
* ⏰ **Automated Reminders:** Background JobQueue delivers reminders right when tasks are due.
* 📋 **Task Management:** View Active, Today, Upcoming, Completed, and Search tasks.
* 📊 **Productivity Statistics:** Real-time stats with task completion ratios.
* ⚙️ **Timezone Configuration:** Full support for global timezones.

---

## 🛠 Prerequisites & Local Setup

### 1. Create Telegram Bot via BotFather
1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Send `/newbot`.
3. Name your bot and assign the username `flitedstbot` (or your preferred username).
4. Copy the API **BOT_TOKEN**.

### 2. Local Installation
```bash
# Clone the repository
git clone [https://github.com/your-username/flitedstbot.git](https://github.com/your-username/flitedstbot.git)
cd flitedstbot

# Create virtual environment
python -m venv venv
source venv/bin/venv/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment Variables
cp .env.example .env
