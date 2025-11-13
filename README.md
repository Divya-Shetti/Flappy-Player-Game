# 🐦 Flappy Player Game

A classic Flappy Bird-style game built using the **Pygame** library in Python. Dodge the pipes and aim for the high score!

---

## ✨ Features

* **Classic Flappy Bird Gameplay:** Tap/press space to fly and avoid obstacles.
* **Persistent High Score:** Saves your best score locally in a `highscore.txt` file.
* **Animated Player:** The player character features a flapping animation.
* **Dynamic Graphics:** Includes a scrolling background and ground to simulate movement.
* **Game Over/Reset:** Easy to restart the game with a reset button after a collision.

---

## 🛠️ Installation

### Prerequisites

You need **Python 3.x** installed on your system. This project also uses a virtual environment named `myenv`.

### Project Setup

1.  **Activate the Virtual Environment (myenv):**
    ```bash
    # On Windows
    .\myenv\Scripts\activate
    # On macOS/Linux
    source myenv/bin/activate
    ```
2.  **Install Pygame:**
    ```bash
    pip install pygame
    ```
3.  **Clone the repository** or download the project files.
4.  **Ensure image assets are present:** The game relies on a directory named `img/` containing the following files:
    * `bg3.jpg` (Background image)
    * `ground4.jpg` (Ground image)
    * `reset.png` (Reset button image)
    * `luffy1.png` through `luffy8.png` (Player animation frames)

### Running the Game

Execute the main Python script:

```bash
python main.py
```

### 🎮 How to Play

### Controls

| Action | Key/Input |
| :--- | :--- |
| **Start/Jump** | **SPACEBAR** or **Left Mouse Button Click** |

### Goal

The game starts when you make your first jump. Navigate your player through the gap between the pipes without hitting the pipes or the ground.

### Scoring

* You gain **10 points** for successfully passing through a single pair of pipes.
* Your current score is displayed at the top center.
* The high score is displayed in the top right corner.

---

## ⚙️ Game Details

### Core Classes

| Class | Description |
| :--- | :--- |
| `Bird` | Represents the player character (**Flappy Player**). Handles gravity, jumping, collision rectangle, and flapping animations. |
| `Pipe` | Represents the obstacle pipes. Handles movement and self-deletion when moving off-screen. |
| `Button`| A simple class for the reset button functionality after game over. |

### Configuration Variables

You can adjust these variables within the code to change gameplay difficulty:

* `fps = 50`: Frames updated per second.
* `scroll_speed = 3`: Horizontal speed of the pipes and ground.
* `pipe_gap = 230`: Vertical space between the top and bottom pipe (larger is easier).
* `pipe_frequency = 2000`: Time in milliseconds (2 seconds) between new pipe pair generation (larger is easier).

---

## 🤝 Contribution

Feel free to fork the project and make improvements! Ideas for future development include:

* Adding sound effects.
* Implementing difficulty scaling (increasing `scroll_speed` and decreasing `pipe_gap` over time).
* Adding different player sprites.
