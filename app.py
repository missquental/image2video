import streamlit as st
import torch
from diffusers import StableVideoDiffusionPipeline
from PIL import Image
import numpy as np
import os
import tempfile
import uuid
from io import BytesIO
import base64

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎥",
    layout="wide"
)

# Judul aplikasi
st.title("🎥 AI Video Generator")
st.subheader("Generate video dari gambar menggunakan Stable Video Diffusion")

# Sidebar untuk pengaturan
with st.sidebar:
    st.header("⚙️ Pengaturan")
    num_frames = st.slider("Jumlah Frame", min_value=8, max_value=25, value=16, step=1)
    fps = st.slider("FPS", min_value=4, max_value=12, value=8, step=1)
    guidance_scale = st.slider("Guidance Scale", min_value=0.0, max_value=2.0, value=1.0, step=0.1)
    decode_chunk_size = st.selectbox("Decode Chunk Size", [4, 8, 16], index=1)
    
    st.divider()
    st.info("💡 Tips: Gunakan gambar yang jelas dan resolusi tinggi untuk hasil terbaik")

@st.cache_resource
def load_model():
    """Load model dengan caching untuk performance"""
    try:
        pipe = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid-xt",
            torch_dtype=torch.float16,
            variant="fp16"
        )
        pipe.enable_model_cpu_offload()
        return pipe
    except Exception as e:
        st.error(f"Gagal memuat model: {str(e)}")
        return None

def generate_video(pipe, image, prompt, num_frames, guidance_scale, decode_chunk_size):
    """Generate video dari gambar dan prompt"""
    try:
        with st.spinner("🔄 Sedang menggenerate video... Mohon tunggu beberapa menit"):
            frames = pipe(
                prompt,
                image=image,
                num_frames=num_frames,
                guidance_scale=guidance_scale,
                decode_chunk_size=decode_chunk_size
            ).frames[0]
        return frames
    except Exception as e:
        st.error(f"Error saat generate video: {str(e)}")
        return None

def save_frames_as_mp4(frames, fps, output_path):
    """Simpan frames sebagai video MP4 menggunakan imageio"""
    try:
        import imageio
        writer = imageio.get_writer(output_path, fps=fps)
        
        for frame in frames:
            # Convert PIL image to numpy array
            if isinstance(frame, Image.Image):
                frame_array = np.array(frame)
            else:
                frame_array = frame
            
            writer.append_data(frame_array)
        
        writer.close()
        return True
    except ImportError:
        st.warning("imageio tidak ditemukan. Silakan install dengan: pip install imageio[ffmpeg]")
        return False
    except Exception as e:
        st.error(f"Error saat menyimpan video: {str(e)}")
        return False

def image_to_base64(image):
    """Convert PIL image to base64 string"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Input")
    
    # Upload gambar
    uploaded_file = st.file_uploader(
        "Upload Gambar", 
        type=["png", "jpg", "jpeg"],
        help="Upload gambar sebagai dasar untuk generate video"
    )
    
    if uploaded_file is not None:
        # Tampilkan gambar yang diupload
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Gambar Input", use_column_width=True)
        
        # Prompt input
        prompt = st.text_input(
            "Prompt Deskripsi Video",
            placeholder="Contoh: A panda walking in the forest...",
            help="Deskripsikan apa yang ingin terjadi dalam video"
        )
        
        # Tombol generate
        if st.button("🎬 Generate Video", type="primary", use_container_width=True):
            if not prompt:
                st.warning("⚠️ Silakan masukkan prompt terlebih dahulu")
            else:
                # Load model
                with st.spinner("📥 Memuat model..."):
                    pipe = load_model()
                
                if pipe is not None:
                    # Generate video
                    frames = generate_video(pipe, image, prompt, num_frames, guidance_scale, decode_chunk_size)
                    
                    if frames is not None:
                        st.success("✅ Video berhasil digenerate!")
                        
                        # Buat temporary directory untuk menyimpan frames
                        temp_dir = tempfile.mkdtemp()
                        
                        # Simpan frames individu
                        frame_paths = []
                        for i, frame in enumerate(frames):
                            frame_path = os.path.join(temp_dir, f"frame_{i:04d}.png")
                            frame.save(frame_path)
                            frame_paths.append(frame_path)
                        
                        # Tampilkan preview frames pertama dan terakhir
                        st.subheader("🖼️ Preview Frames")
                        preview_col1, preview_col2 = st.columns(2)
                        with preview_col1:
                            st.image(frames[0], caption="Frame Pertama", width=200)
                        with preview_col2:
                            st.image(frames[-1], caption="Frame Terakhir", width=200)
                        
                        # Simpan sebagai MP4 jika imageio tersedia
                        video_path = os.path.join(temp_dir, "generated_video.mp4")
                        if save_frames_as_mp4(frames, fps, video_path):
                            # Download button untuk video
                            with open(video_path, "rb") as file:
                                st.download_button(
                                    label="💾 Download Video (MP4)",
                                    data=file,
                                    file_name="generated_video.mp4",
                                    mime="video/mp4",
                                    use_container_width=True
                                )
                        
                        # Download button untuk frames ZIP
                        try:
                            import zipfile
                            zip_path = os.path.join(temp_dir, "frames.zip")
                            with zipfile.ZipFile(zip_path, 'w') as zipf:
                                for frame_path in frame_paths:
                                    zipf.write(frame_path, os.path.basename(frame_path))
                            
                            with open(zip_path, "rb") as file:
                                st.download_button(
                                    label="📁 Download All Frames (ZIP)",
                                    data=file,
                                    file_name="video_frames.zip",
                                    mime="application/zip",
                                    use_container_width=True
                                )
                        except Exception as e:
                            st.warning(f"Tidak dapat membuat ZIP: {str(e)}")
                        
                        # Cleanup temporary files setelah beberapa waktu
                        # (opsional: implement cleanup otomatis)
                        
                    else:
                        st.error("❌ Gagal mengenerate video")
                else:
                    st.error("❌ Model tidak dapat dimuat")

with col2:
    st.header("ℹ️ Informasi")
    
    st.info("""
    **Cara Menggunakan:**
    1. Upload gambar sebagai dasar video
    2. Masukkan prompt deskriptif
    3. Atur parameter di sidebar
    4. Klik tombol "Generate Video"
    5. Download hasil video
    
    **Tips:**
    - Gunakan gambar berkualitas tinggi
    - Prompt yang deskriptif menghasilkan video lebih baik
    - Proses membutuhkan waktu beberapa menit
    """)
    
    st.divider()
    
    st.markdown("""
    **Model:** Stable Video Diffusion  
    **Developer:** Stability AI  
    **Platform:** Hugging Face Diffusers
    """)
    
    # Contoh prompt
    st.subheader("📝 Contoh Prompt:")
    example_prompts = [
        "A cat playing with a ball in the garden",
        "A car driving through a rainy street at night",
        "A bird flying over mountains during sunset",
        "A robot dancing in a futuristic city"
    ]
    
    for prompt in example_prompts:
        if st.button(f"📋 {prompt}", key=f"prompt_{uuid.uuid4()}"):
            st.session_state.prompt_example = prompt

# Footer
st.divider()
st.caption("🎥 AI Video Generator | Powered by Stable Video Diffusion & Streamlit")

# Auto-fill prompt dari contoh jika ada
if 'prompt_example' in st.session_state:
    st.experimental_rerun()
