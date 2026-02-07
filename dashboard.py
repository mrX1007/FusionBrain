import os
import sys
import time

import streamlit as st

# --- 🛠 ФИКС ПУТЕЙ (Чтобы работало рядом с run.py) ---
# Получаем текущую директорию (папка fusionbrain)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Получаем родителя
parent_dir = os.path.dirname(current_dir)
# Добавляем родителя в sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
# ----------------------------------------------------

try:
    from fusionbrain import FusionBrain
except ImportError as e:
    st.error(f"Critical Import Error: {e}")
    st.stop()

# --- Настройка страницы ---
st.set_page_config(
    page_title="FusionBrain AGI", page_icon="🧠", layout="wide", initial_sidebar_state="expanded"
)

# --- CSS (Matrix Style) ---
st.markdown(
    """
<style>
    .stApp { background-color: #0e1117; }
    .stTextInput > div > div > input { background-color: #1c1c1c; color: #00ff00; border: 1px solid #333; }
    .stChatMessage { background-color: #262730; border: 1px solid #444; border-radius: 10px; }
    h1, h2, h3 { color: #e0e0e0 !important; }
    .stProgress > div > div > div > div { background-color: #00ff00; }
</style>
""",
    unsafe_allow_html=True,
)

# --- Инициализация (Singleton) ---
if "brain" not in st.session_state:
    with st.spinner("🧠 Booting Neural Core..."):
        try:
            st.session_state.brain = FusionBrain()
            st.session_state.messages = []
            st.session_state.last_thought_process = ""
            st.toast("System Online", icon="✅")
        except Exception as e:
            st.error(f"Critical Boot Error: {e}")
            st.stop()

# --- Сайдбар: Монитор ---
with st.sidebar:
    st.header("🧠 Monitor")

    col1, col2 = st.columns(2)
    with col1:
        sid = getattr(st.session_state.brain, "session_id", "Unknown")
        st.metric("Session", sid[:6])
    with col2:
        # --- ФИКС ДЛЯ ТВОЕЙ ПАМЯТИ ---
        # Твоя память использует self.buffer (deque), а не self.history
        if hasattr(st.session_state.brain, "memory"):
            # Берем длину буфера
            count = len(st.session_state.brain.memory.buffer)
        else:
            count = 0
        st.metric("Memories", count)
        # -----------------------------

    st.divider()

    # Выбор режима
    mode = st.radio("Mode", ["💬 Chat", "🕵️‍♂️ Research"])

    st.divider()

    # Визуализация состояния (Квантовая энтропия из логов)
    last_proc = str(st.session_state.get("last_thought_process", ""))

    if "QUANTUM STATE" in last_proc or "CHAOS_MODE" in last_proc:
        st.progress(0.9)
        st.caption("Status: SUPERPOSITION (High Entropy)")
        st.warning("🔥 Mode: CHAOS / CREATIVITY")
    elif "LOGIC_MODE" in last_proc:
        st.progress(0.2)
        st.caption("Status: COLLAPSED (Low Entropy)")
        st.success("🛡️ Mode: LOGIC / SAFETY")
    else:
        st.progress(0.0)
        st.caption("Status: Idle")

# --- Чат ---
st.title("FusionBrain Dashboard")

# Отображаем историю чата (локальную для Streamlit)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Enter command...")

if prompt:
    # 1. Показываем сообщение юзера
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Обработка
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        with st.status("Running Cognitive Pipeline...", expanded=True) as status:
            try:
                # ЛОГИКА ВЫБОРА АГЕНТА
                if mode == "🕵️‍♂️ Research" or prompt.strip().startswith("/research"):
                    st.write("🕵️‍♂️ Engaging Autonomous Research Agent...")
                    clean_prompt = prompt.replace("/research", "").strip() or prompt

                    # Запуск ресерча
                    response = st.session_state.brain.research_expert.run(clean_prompt)
                    status.update(label="Research Complete", state="complete")

                else:
                    st.write("check...")
                    time.sleep(0.2)
                    st.write("🧠 Reasoning & Simulation...")

                    # Запуск обычного мышления
                    response = st.session_state.brain.think(prompt)
                    status.update(label="Reasoning Complete", state="complete")

                # Сохраняем "сырой" ответ для анализа в сайдбаре
                st.session_state.last_thought_process = response

                # Вывод ответа
                message_placeholder.markdown(response)

                # Сохраняем в историю чата
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"Pipeline Error: {e}")
                status.update(label="Error Occurred", state="error")
