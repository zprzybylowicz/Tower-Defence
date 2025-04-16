# Tower-Defence
A Python/PyQt5 Tower Defense game with single‑player, local-coop, networked play, persistent saves (JSON/XML/MongoDB) and live streaming over TCP/IP.
Tower Defense

A Python-based Tower Defense game built with PyQt5, featuring single-player, local cooperative, and networked play. The game supports saving and resuming progress via JSON, XML, and MongoDB, and even allows live streaming of the game window to a remote client over TCP/IP.

Features

Game Modes

Single Player

Local Cooperative Play (2 players on one machine)

Networked Play: host streams the game window; clients view live updates

Resume from save (JSON, XML, MongoDB)

Gameplay

Multiple levels with unique enemy paths

Place and upgrade towers on a grid-based map

Choose between different tower types (e.g., Fire, Sniper)

Enemy variety: Random, Strategic, Aggressive AI behaviors

Gold economy and upgrade mechanics

History and Persistence

Automatically save game history and final stats to JSON, XML, and MongoDB

Resume a paused or interrupted game at any time

Networking & Streaming

Host mode: streams the entire game window as JPEG frames over TCP/IP

Client mode: connects to host IP and displays live game stream

Configurable streaming port

Customization

Select enemy skins in real time

Drag-and-drop tower placement via shop GUI

Requirements

Python 3.7+

PyQt5

pymongo (for MongoDB integration)

MongoDB server (if using MongoDB saves)

Installation

Clone the repository:

git clone https://github.com/yourusername/tower-defense.git
cd tower-defense

Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate       # Windows

Install dependencies:

pip install -r requirements.txt

Usage

Launching the Game

Run the launcher:

python launcher.py

Select a mode:

1 Player: Standard single-player game.

2 Players Locally: Split-screen or shared controls.

Networked Game: Host streams to clients. Enter 0.0.0.0:8080 to host, or enter the host IP on client.

Resume: Load from JSON, XML, or MongoDB.

Networked Streaming

Host: Start in "Networked Game" mode and ensure your firewall allows the chosen port.

Client: Run python client.py, enter the host IP (e.g., 192.168.0.178:8080) in the GUI.

File Structure

├── game.py            # Main game logic & UI
├── launcher.py        # Mode selection dialog
├── network.py         # Streaming server implementation
├── client.py          # Streaming client viewer
├── game_state.py      # JSON save/load helper
├── xml_history.py     # XML save/load helper
├── mongo_history.py   # MongoDB save/load helper
├── map_generator.py   # Procedural path generation
├── shop.py            # Tower shop GUI
├── tower.py           # Tower classes and shooting logic
├── enemy_base.py      # Enemy classes and movement logic
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation

Contributing

Contributions are welcome! Please open issues and submit pull requests on GitHub.

License

This project is licensed under the MIT License. See LICENSE for details.

