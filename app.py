import os
import streamlit as st
import base64
from io import BytesIO
from datetime import datetime
from PIL import Image
from ollama import Client, generate

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="AI Artikel & Image Generator",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Artikel & Image Generator (Ollama Cloud)")

# =========================
# API KEY
# =========================

OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")

if not OLLAMA_API_KEY:
    st.error("⚠️ OLLAMA_API_KEY belum diset di Streamlit Secrets")
    st.stop()

# =========================
# CLIENT
# =========================

client = Client(
    host="https://ollama.com",
    headers={"Authorization": "Bearer " + OLLAMA_API_KEY}
)

# =========================
# SIDEBAR SETTINGS
# =========================

st.sidebar.header("⚙️ Pengaturan Model")

model_name = st.sidebar.selectbox(
    "Pilih Model Artikel",
    [
        "qwen3.5:cloud",
        "qwen3-coder-next",
        "glm-5:cloud",
        "minimax-m2.5:cloud",
        "kimi-k2.5:cloud",
        "qwen3-vl",
        "rnj-1",
        "qwen3-next",
        "nemotron-3-nano",
        "gemini-3-flash-preview",
        "devstral-small-2",
        "devstral-2",
        "glm-4.7:cloud",
        "cogito-2.1",
        "minimax-m2:cloud",
        "glm-4.6:cloud",
        "deepseek-v3.2:cloud",
        "minimax-m2.1:cloud",
        "kimi-k2-thinking:cloud",
        "kimi-k2:1t-cloud",
        "mistral-large-3:675b-cloud",
        "gemma3",
        "gpt-oss",
        "qwen3-coder",
        "deepseek-v3.1"
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
# TABS
# =========================

tab1, tab2 = st.tabs(["📝 Generate Artikel", "🎨 Generate Image"])

# =========================
# TAB ARTIKEL
# =========================

with tab1:

    st.subheader("📝 Generator Artikel")

    title = st.text_input("Judul Artikel")
    keywords = st.text_input("Keyword (pisahkan dengan koma)")

    generate_button = st.button("🚀 Generate Artikel")

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

        Struktur:
        - Pendahuluan
        - Subjudul H2 dan H3
        - Paragraf informatif
        - Kesimpulan
        - SEO friendly natural
        """

        messages = [{"role": "user", "content": prompt}]

        st.info("⏳ Sedang generate artikel...")
        article_container = st.empty()
        full_response = ""

        try:
            for part in client.chat(model_name, messages=messages, stream=True):
                if part.message.content:
                    full_response += part.message.content
                    article_container.markdown(full_response)

            st.success("✅ Artikel selesai!")

            st.download_button(
                label="📥 Download Artikel (.txt)",
                data=full_response,
                file_name=f"artikel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Error: {e}")

# =========================
# TAB IMAGE
# =========================

with tab2:

    st.subheader("🎨 AI Image Generator")

    image_prompt = st.text_area("Prompt Gambar", "a sunset over mountains")

    image_model = st.selectbox(
        "Pilih Model Image",
        ["x/z-image-turbo"]
    )

    generate_image_button = st.button("🖼 Generate Image")

    if generate_image_button and image_prompt:

        st.info("⏳ Sedang generate gambar...")
        progress_text = st.empty()
        image_placeholder = st.empty()

        try:
            for response in generate(
                model=image_model,
                prompt=image_prompt,
                stream=True,
                host="https://ollama.com",
                headers={"Authorization": "Bearer " + OLLAMA_API_KEY}
            ):

                if response.image:
                    image_bytes = base64.b64decode(response.image)
                    image = Image.open(BytesIO(image_bytes))

                    image_placeholder.image(image, caption="Hasil Generate", use_column_width=True)

                    st.download_button(
                        label="📥 Download Image",
                        data=image_bytes,
                        file_name="generated_image.png",
                        mime="image/png"
                    )

                elif response.total:
                    progress_text.text(
                        f"Progress: {response.completed or 0}/{response.total}"
                    )

            st.success("✅ Gambar selesai dibuat!")

        except Exception as e:
            st.error(f"Error: {e}")
