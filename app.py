import os
import streamlit as st
from datetime import datetime
from ollama import Client

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="AI Content & Coding Suite",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Content & Coding Suite (Ollama Cloud)")

# =========================
# API KEY
# =========================
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")

if not OLLAMA_API_KEY:
    st.error("⚠️ `OLLAMA_API_KEY` belum diset di Streamlit Secrets")
    st.stop()

# =========================
# CLIENT CLOUD
# =========================
client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"}
)

# =========================
# SIDEBAR
# =========================
st.sidebar.header("⚙️ Pengaturan")

# ——— Model untuk Artikel ———
article_model = st.sidebar.selectbox(
    "Model Artikel",
    [
        "qwen3.5:cloud",
        "glm-4:cloud",
        "deepseek-v3.2:cloud",
        "mistral-large-24.11:cloud",  # updated version
        "gpt-oss"
    ],
    key="article_model"
)

article_length = st.sidebar.selectbox(
    "Panjang Artikel",
    ["500 kata", "1000 kata", "2000 kata"],
    key="article_length"
)

tone = st.sidebar.selectbox(
    "Gaya",
    ["Formal", "Santai", "SEO Friendly", "Storytelling"],
    key="tone"
)

# ——— Model untuk Coding ———
coding_model = st.sidebar.selectbox(
    "Model Coding",
    [
        "qwen3-coder-next:cloud",   # ✅ Cloud-ready & terbaru
        "deepseek-v3.1:cloud",
        "gpt-oss"
    ],
    key="coding_model"
)

# =========================
# TABS
# =========================
tab1, tab2 = st.tabs(["📝 Artikel", "💻 Coding Agent"])

# =========================
# TAB ARTIKEL
# =========================
with tab1:
    st.subheader("📝 Generator Artikel")

    title = st.text_input("Judul Artikel")
    keywords = st.text_input("Keyword (opsional)")

    if st.button("🚀 Generate Artikel") and title:
        prompt = f"""
        Buat artikel {article_length}, gaya {tone}.
        Judul: {title}
        Keyword: {keywords or "-"}

        Struktur:
        - Pendahuluan
        - Subjudul dengan heading H2 & H3
        - Isi informatif dan mendalam
        - Kesimpulan
        """

        messages = [{"role": "user", "content": prompt}]

        container = st.empty()
        full_text = ""

        with st.spinner("⏳ Memproses..."):
            try:
                for part in client.chat(model=article_model, messages=messages, stream=True):
                    if part and part.message and part.message.content:
                        full_text += part.message.content
                        container.markdown(full_text)
            except Exception as e:
                st.error(f"❌ Error saat generate artikel: `{str(e)}`")
                st.stop()

        if full_text.strip():
            st.download_button(
                "📥 Download Artikel",
                full_text,
                file_name=f"artikel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        else:
            st.error("❌ Tidak ada output dari model. Pastikan model tersedia dan API key valid.")

# =========================
# TAB CODING AGENT (Dengan Memory)
# =========================
with tab2:
    st.subheader("💻 Coding Chat Agent (Revisi Mode)")

    coding_model = st.selectbox(
        "Model Coding",
        [
            "qwen3-coder-next",
            "qwen3-coder",
            "devstral-2",
            "deepseek-v3.1",
            "glm-5:cloud",
            "gpt-oss"
        ],
        key="coding_model"
    )

    # =========================
    # SESSION MEMORY
    # =========================

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": """
                Kamu adalah Senior Software Engineer dan AI Coding Assistant.
                Jawab profesional.
                Jika membuat code:
                - Berikan code lengkap
                - Gunakan best practice
                - Tambahkan komentar
                """
            }
        ]

    # =========================
    # TAMPILKAN CHAT HISTORY
    # =========================

    for msg in st.session_state.chat_history[1:]:
        if msg["role"] == "user":
            st.chat_message("user").markdown(msg["content"])
        else:
            st.chat_message("assistant").markdown(msg["content"])

    # =========================
    # INPUT CHAT
    # =========================

    user_input = st.chat_input("Tulis instruksi / revisi code...")

    if user_input:

        # Tambahkan pesan user ke memory
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        st.chat_message("user").markdown(user_input)

        # Streaming response
        response_container = st.chat_message("assistant")
        full_response = ""

        with response_container:
            placeholder = st.empty()

            for part in client.chat(
                model=coding_model,
                messages=st.session_state.chat_history,
                stream=True
            ):
                if part.message.content:
                    full_response += part.message.content
                    placeholder.markdown(full_response)

        # Simpan jawaban ke memory
        st.session_state.chat_history.append(
            {"role": "assistant", "content": full_response}
        )

    # =========================
    # RESET BUTTON
    # =========================

    if st.button("🔄 Reset Chat"):
        st.session_state.chat_history = [
            {
                "role": "system",
                "content": """
                Kamu adalah Senior Software Engineer dan AI Coding Assistant.
                Jawab profesional.
                Jika membuat code:
                - Berikan code lengkap
                - Gunakan best practice
                - Tambahkan komentar
                """
            }
        ]
        st.success("Chat berhasil direset")
