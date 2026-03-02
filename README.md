# Python 2.7 Chess: Networked Multiplayer

A fully functional, multiplayer Chess game built using **Python 2.7**. This project features a central Server to manage game states and turns, and a graphical Client built with `Tkinter` for the gameplay interface.

## 📋 Features
* **Multiplayer over LAN:** Play against another person over a local network.
* **Turn Management:** The server synchronizes moves and assigns colors (White/Black) randomly.
* **Graphical User Interface (GUI):** A clean interface using `Tkinter` and `Pillow`.
* **Move Validation:** Supports complex piece logic, including preventing moves that would leave your King in check.
* **Visual Aids:** Highlighting of selected pieces and optional "Show Possible Moves" in red.
* **Asynchronous Networking:** Uses `select.select` to handle multiple socket connections without freezing the GUI.

---

## 🛠 System Requirements
This project is designed for **Python 2.7**. 

### Dependencies:
1. **Pillow (PIL):** Required for rendering the chess piece images.
   ```bash
   pip install Pillow

Configuration

Before running the game, you need to point the Client to the Server's IP address:

1. Open client.py in your text editor.
2. Locate the line: IP = 'NONE'.
3. Replace the IP address with the local IP of the computer running server.py.
