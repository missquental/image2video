import os
import streamlit as st
from ollama import Client
from datetime import datetime

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="AI Artikel Generator - Ollama Cloud",
    page_icon="📝",
    layout="wide"
)

st.title("📝 AI Artikel Generator (Ollama Cloud API)")
st.write("Generate artikel otomatis menggunakan Ollama Cloud (ollama.com)")

# =========================
# API KEY
# =========================

OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")

if not OLLAMA_API_KEY:
    st.error("⚠️ OLLAMA_API_KEY belum diset di Streamlit Cloud Secrets")
    st.stop()

# =========================
# CLIENT
# =========================

client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + OLLAMA_API_KEY}
)

# =========================
# SIDEBAR
# =========================

st.sidebar.header("⚙️ Pengaturan")

model_name = st.sidebar.selectbox(
    "Pilih Model",
    [
        "gpt-oss:120b",
        "gpt-oss:20b"
    ]
)

article_length = st.sidebar.selectbox(
    "Panjang Artikel",
    ["Pendek (500 kata)", "Sedang (1000 kata)", "Panjang (2000 kata)"]
)

tone = st.sidebar.selectbox(
    "Gaya Penulisan",
    ["Formal", "Santai", "SEO Friendly", "Storytelling"]
)

# =========================
# INPUT
# =========================

title = st.text_input("Judul Artikel")

keywords = st.text_input("Keyword (pisahkan dengan koma)")

generate_button = st.button("🚀 Generate Artikel")

# =========================
# GENERATE
# =========================

if generate_button and title:

    length_instruction = {
        "Pendek (500 kata)": "sekitar 500 kata",
        "Sedang (1000 kata)": "sekitar 1000 kata",
        "Panjang (2000 kata)": "sekitar 2000 kata"
    }

    prompt = f"""
    Buatkan artikel {length_instruction[article_length]} dengan gaya {tone}.
    Judul: {title}
    Keyword utama: {keywords}

    Struktur artikel:
    - Pendahuluan
    - Subjudul H2 & H3
    - Paragraf informatif
    - Kesimpulan
    - Optimasi SEO natural
    """

    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]

    st.info("⏳ Sedang generate artikel...")

    article_container = st.empty()
    full_response = ""

    try:
        for part in client.chat(model_name, messages=messages, stream=True):
            if part.message.content:
                full_response += part.message.content
                article_container.markdown(full_response)

        st.success("✅ Artikel selesai dibuat!")

        # Download button
        st.download_button(
            label="📥 Download Artikel (.txt)",
            data=full_response,
            file_name=f"artikel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"Terjadi error: {e}")
