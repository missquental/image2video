🎨 Fitur Aplikasi
🔧 Fitur Utama:
Upload Gambar: Support PNG, JPG, JPEG
Custom Prompt: Input deskripsi video yang diinginkan
Pengaturan Parameter:
Jumlah frame (8-25)
FPS (4-12)
Guidance scale
Decode chunk size
Preview Frames: Tampilkan frame pertama dan terakhir
Download Options:
Video MP4 (jika imageio tersedia)
ZIP semua frames
Responsive Design: Layout dua kolom
📱 UI/UX Features:
Loading spinner selama proses
Error handling yang baik
Preview real-time
Contoh prompt yang bisa diklik
Sidebar dengan pengaturan
Informasi dan tips penggunaan
▶️ Cara Menjalankan
Install dependencies:
pip install -r requirements.txt
Install tambahan (opsional tapi direkomendasikan):
pip install imageio[ffmpeg]
Jalankan aplikasi:
streamlit run app.py
Akses di browser:
http://localhost:8501
⚠️ Catatan Penting
Waktu Proses: Bisa memakan waktu 5-15 menit tergantung hardware
RAM Usage: Butuh minimal 8GB RAM
GPU: Direkomendasikan GPU untuk kecepatan optimal
Storage: Pastikan cukup space untuk menyimpan frames sementara
🛠️ Troubleshooting
Jika error memory:

# Tambahkan di bagian load_model():
pipe.enable_attention_slicing()  # Tambahkan line ini
Untuk versi minimalis tanpa imageio:

Hapus fungsi save_frames_as_mp4
Hanya download frames dalam bentuk ZIP
