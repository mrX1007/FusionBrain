# 🧠 FusionBrain

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Quantum](https://img.shields.io/badge/Quantum-Qiskit-purple)

**FusionBrain** is an experimental neuro-symbolic cognitive architecture (System 2 Thinking) that combines Large Language Models (LLMs), quantum probability simulation, and meta-learning.

Unlike standard chatbots, FusionBrain **thinks before it answers** by modeling the consequences of its actions in a quantum environment.

## 🔥 Key Features

* **⚛️ Quantum World Model:** Uses IBM Qiskit (Aer Simulator) for risk assessment and scenario modeling via quantum entanglement.
* **🛡️ Safety First:** The agent refuses to execute dangerous commands (e.g., deleting system files or making high-risk investments) based on consequence simulation.
* **🎓 Meta-Learning:** A "reflection" system. The agent analyzes its own errors, formulates lessons (`[LESSON]`), and saves them to long-term memory (RAG).
* **🧩 Modular Pipeline:** Clear separation of roles: `Web` -> `Reasoning` -> `Simulation` -> `Code` -> `Critic`.

## 🛠️ Architecture

1.  **WebExpert:** Gathers up-to-date facts from the web.
2.  **ReasoningExpert:** Builds hypotheses and strategic plans.
3.  **WorldModelExpert (The Core):** Validates strategies using quantum simulation.
4.  **CodeExpert:** Generates code while adhering to security constraints.
5.  **CriticExpert:** Performs final validation and review.
6.  **MetaLearning:** Handles self-learning and memory optimization.

## 🚀 Quick Start

We use [uv](https://github.com/astral-sh/uv) for lightning-fast dependency management.

### 1. Installation

```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/FusionBrain.git](https://github.com/YOUR_USERNAME/FusionBrain.git)
cd FusionBrain

# Install uv (if not already installed)
pip install uv

# Create environment and install dependencies (1 command!)
uv sync


2. Setup Pre-commit (For Developers)

source .venv/bin/activate
uv run pre-commit install


3. Usage

uv run run.py
