# Tower Defense

A Python/PyQt5 Tower Defense game featuring single‑player, local co‑op, networked play, persistent saves (JSON/XML/MongoDB), and live TCP/IP streaming.

## Features

- **Game Modes**  
  - Single Player  
  - Local Co‑op (2 players on one machine)  
  - Networked Play (host streams the game window; clients view live updates)  
  - Resume from save (JSON, XML, MongoDB)

- **Gameplay**  
  - Multiple levels with unique enemy paths  
  - Place and upgrade towers on a grid  
  - Choose tower types (Fire, Sniper, etc.)  
  - Enemy varieties: Random, Strategic, Aggressive  
  - Gold economy and upgrade mechanics

- **History & Persistence**  
  - Save game history and stats to JSON, XML, and MongoDB  
  - Resume paused or interrupted games at any time

- **Networking & Streaming**  
  - Host mode: streams the full game window as JPEG frames over TCP/IP  
  - Client mode: connects to host IP and displays live stream  
  - Configurable port

- **Customization**  
  - Real‑time enemy skin selection  
  - Drag‑and‑drop tower placement via shop GUI

## Requirements

- Python 3.7+  
- PyQt5  
- pymongo (for MongoDB integration)  
- MongoDB server (if using MongoDB saves)

## Installation

```bash
git clone https://github.com/<your‑username>/tower-defense.git
cd tower-defense

python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
