# Hex & Brouwer: Topology Lab (MAT 436)

An interactive simulation exploring the discrete topological foundations of the Brouwer Fixed-Point Theorem. This tool uses the game of Hex and Sperner's Lemma to demonstrate why a continuous mapping of a disk to itself must contain at least one fixed point.

## 🔬 Core Features
* **Hex Game Engine:** Play Human vs. Human, Human vs. AI, or AI vs. AI on a 5x5 Rhombus.
* **Dual Graph Visualization:** Toggles a triangular mesh representing the dual graph of the hexagonal tiling.
* **Sperner Lemma Overlay:** Highlights "Sperner Triangles" (cells where Red, Blue, and White meet) to show the "seeds" of connectivity.
* **Vector Field Mode:** Visualizes the board state as a discrete vector field, approximating the flow toward a fixed point.
* **Step-by-Step Analysis:** Full history navigation to observe how topological features shift and merge during gameplay.

## 🎓 Mathematical Context
This lab is designed for **Berea College MAT 436 (Topology)**. It serves as a visual aid for the following concepts:

1.  **Sperner’s Lemma:** Proving that any valid coloring of a triangulated simplex contains an odd number of "complete" triangles.
2.  **Hex Theorem:** Demonstrating that the game of Hex cannot end in a draw, which is logically equivalent to the Brouwer Fixed-Point Theorem.
3.  **Harkness Discussion:** Students should use the "Step" feature to identify why Sperner triangles never disappear, even as the board reaches a high state of entropy.

## 🛠️ Requirements & Setup
* **Python 3.x**
* **Pygame** (`pip install pygame`)

To run the lab:
```bash
python hex_brouwer_lab.py