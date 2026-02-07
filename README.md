# 🧠 FusionBrain AGI

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Quantum](https://img.shields.io/badge/Quantum-Qiskit-purple)
![AI](https://img.shields.io/badge/AI-Autonomous-orange)
![Interface](https://img.shields.io/badge/UI-Streamlit-red)

**FusionBrain** is an experimental **Neuro-Symbolic Cognitive Architecture** (System 2 Thinking) that combines Large Language Models (LLMs), Quantum Probability Simulation, and Autonomous Agents.

Unlike standard chatbots, FusionBrain **thinks before it answers**, possesses **Quantum Intuition** (balancing Logic vs. Chaos), and can **proactively research** topics on the web.

## 🔥 Key Features v4.0

* **⚛️ Quantum Intuition (Right Brain):** Uses **IBM Qiskit** to generate true entropy via quantum superposition. The agent dynamically switches between `LOGIC_MODE` (deterministic) and `CHAOS_MODE` (creative/high-risk) based on qubit measurement.
* **🕵️‍♂️ Autonomous Research Agent:** A proactive agent that scans the web (DuckDuckGo + Wikipedia), filters content using LLM-based scoring, memorizes facts (RAG), and creates **GitHub Issues** for high-value findings.
* **🖥️ Neural Dashboard:** A full-fledged Web UI (Streamlit) to monitor internal thought processes, memory state, and quantum entropy levels in real-time.
* **🧠 RAG Memory:** Long-term memory system based on **ChromaDB** and semantic search.
* **🛡️ Safety Simulation:** The World Model simulates the consequences of code execution before running it.

## 🛠️ Architecture

The system operates as a pipeline of specialized experts:

1.  **ResearchExpert:** Autonomous web researcher & GitHub integrator.
2.  **QuantumExpert:** Generates entropy and intuition (Logic vs Chaos).
3.  **ReasoningExpert:** Builds hypotheses and strategic plans.
4.  **WorldModelExpert:** Validates strategies using quantum simulation.
5.  **CodeExpert:** Generates code adhering to security constraints.
6.  **CriticExpert:** Performs final validation and review.

## 🚀 Quick Start

We use [uv](https://github.com/astral-sh/uv) for lightning-fast dependency management.

### 1. Installation

```bash
# Clone the repository
git clone [https://github.com/mrX1007/FusionBrain.git](https://github.com/mrX1007/FusionBrain.git)
cd FusionBrain

# Install uv (if not already installed)
pip install uv

# Create environment and install dependencies
uv sync

2. Configuration (.env)
Create a .env file in the root directory to enable all features:

# GitHub Integration (for ResearchExpert)
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=mrX1007/FusionBrain

# Local LLM Model (Ollama)
MODEL_NAME=qwen2.5-coder:7b



3. Usage
Option A: The Neural Dashboard (Recommended) 🖥️
Launch the web interface to see the brain in action.

uv run streamlit run dashboard.py

Option B: CLI Terminal Mode 💻
Run the classic terminal interface.

uv run run.py

🤖 Commands
Chat: Just type anything to talk to the Quantum Brain.

Research: Type /research <topic> (e.g., /research Future of AGI) to launch the autonomous agent.

📦 Tech Stack
Core: Python 3.11+, Ollama (Local LLM)

Quantum: Qiskit (Aer Simulator)

Memory: ChromaDB, Sentence-Transformers

Web: DuckDuckGo Search, Wikipedia API

UI: Streamlit

Tools: PyGithub, Dotenv
