# 🔥 CybroX-UserBot

![CybroX-UserBot](https://via.placeholder.com/800x400?text=CybroX-UserBot)

[![Open Source Love](https://badges.frapsoft.com/os/v2/open-source.png?v=103)](https://github.com/YourUsername/CybroX-UserBot)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)

A powerful, modular Telegram userbot written in Python using Pyrogram.

## 🚀 Features

- Modular architecture for easy extension
- Powerful command system
- Customizable prefix
- Multiple database support (SQLite and MongoDB)
- AI powered features
- Many built-in utilities

## 🛠️ Installation

### Required Variables
 
- `API_ID` - Get it from [my.telegram.org](https://my.telegram.org/)
- `API_HASH` - Get it from [my.telegram.org](https://my.telegram.org/)

### Optional Variables
 
- `DATABASE_URL` - MongoDB connection URL (if using MongoDB)
- `DATABASE_NAME` - Database name (defaults to cybrox_userbot)
- `DATABASE_TYPE` - Set to "sqlite3" or "mongodb" (defaults to sqlite3)
- `PM_LIMIT` - Number of messages before automatic block in PM (defaults to 3)

## 🐧 Linux Installation

```bash
# Install dependencies
sudo apt update && sudo apt install -y python3 python3-pip git

# Clone the repository
git clone https://github.com/YourUsername/CybroX-UserBot.git
cd CybroX-UserBot

# Install Python requirements
pip3 install -r requirements.txt

# Set up configuration
cp .env.dist .env
# Edit .env file with your values

# Start the bot
python3 main.py
```

## 💻 Windows Installation

```bash
# Install Git and Python from their official websites

# Clone the repository
git clone https://github.com/YourUsername/CybroX-UserBot.git
cd CybroX-UserBot

# Install Python requirements
pip install -r requirements.txt

# Set up configuration
copy .env.dist .env
# Edit .env file with your values

# Start the bot
python main.py
```

## 📜 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## 📋 Disclaimer

The use of this userbot is at your own risk. The developers are not responsible for any misuse of this software.