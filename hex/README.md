# Hex Game (Python/Pygame)

A fully functional implementation of the strategy board game **Hex**, built using Python and the Pygame library. This version features a procedural hexagonal grid, custom boundary rendering, and an automated victory-path detection system.

## 🎮 Features
* **Three Game Modes:** * **Human vs Human:** Local multiplayer.
    * **Human vs AI:** Play against a randomized AI opponent.
    * **AI vs AI:** Watch two computer players compete.
* **Visual Goal Indicators:** Refined zigzag boundaries that define player objectives without bleeding into the interior board.
* **Victory Path Highlighting:** Upon a win, the specific chain of hexagons connecting the sides is highlighted with a Gold outline.
* **Pointy-Top Geometry:** Uses a staggered hexagonal coordinate system for accurate Hex topology.

## 🛠️ Requirements
* Python 3.x
* Pygame library

## 🚀 How to Run
1.  **Install Pygame:**
    ```bash
    pip install pygame
    ```
2.  **Run the script:**
    ```bash
    python hex_game.py
    ```

## 🧠 Game Rules
Hex is a connection game played on a rhombus-shaped grid of hexagons.
* **Red Player:** Must form an unbroken chain of red hexagons connecting the **top** and **bottom** red boundaries.
* **Blue Player:** Must form an unbroken chain of blue hexagons connecting the **left** and **right** blue boundaries.
* The game can never end in a draw; the topology of the grid ensures one player must always be able to complete a path.

## 📐 Technical Details: Boundary Rendering
The game uses a **Pointy-Top** hexagon orientation. To create a continuous perimeter, the rendering logic targets specific vertices ($V_0$ through $V_5$) to create "V-shaped" zigzag borders:

* **Red (Top/Bottom):** Highlights the slanted top edges of the first row and slanted bottom edges of the last row.
* **Blue (Left/Right):** Highlights the slanted side edges of the first and last columns.
* **Vertex Math:** Centers are calculated using $x = col \cdot \text{width} + (row \cdot \text{width} / 2)$, creating the classic $60^\circ$ offset required for a Hex board.

---
*Developed as a project exploring hexagonal tiling, topological connectivity, and pathfinding algorithms.*