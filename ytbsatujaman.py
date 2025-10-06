import sys
import subprocess
import threading
import os
import streamlit.components.v1 as components

# 🔹 Pastikan Streamlit terinstall
try:
    import streamlit as st
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    import streamlit as st


# =========================================================
# 🧠 Fungsi utama untuk menjalankan FFmpeg streaming
# =========================================================
def run_ffmpeg(video_path, stream_key, is_shorts, log_callback):
    output_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    scale = "-vf scale=720:1280" if is_shorts else ""

    cmd = [
        "ffmpeg", "-re", "-i", video_path,
        "-c:v", "libx264", "-preset", "veryfast", "-b:v", "2500k",
        "-maxrate", "2500k", "-bufsize", "5000k",
        "-g", "60", "-keyint_min", "60",
        "-c:a", "aac", "-b:a", "128k",
        "-f", "flv"
    ]

    if scale:
        cmd += scale.split()
    cmd.append(output_url)

    log_callback(f"🎬 Menjalankan: {' '.join(cmd)}")

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            log_callback(line.strip())
        process.wait()
    except Exception as e:
        log_callback(f"❌ Error: {e}")
    finally:
        log_callback("✅ Streaming selesai atau dihentikan.")


# =========================================================
# 🎥 Aplikasi Streamlit utama
# =========================================================
def main():
    # ✅ Konfigurasi halaman Streamlit
    st.set_page_config(
        page_title="YouTube Live Streamer",
        page_icon="🎥",
        layout="wide"
    )

    # ✅ Naikkan limit upload file besar (hingga 4GB)
    os.environ["STREAMLIT_SERVER_MAX_UPLOAD_SIZE"] = "4096"
    os.environ["STREAMLIT_SERVER_MAX_MESSAGE_SIZE"] = "4096"

    st.title("🎬 Live Streaming ke YouTube")

    # =========================================================
    # 🧾 Iklan (opsional)
    # =========================================================
    show_ads = st.checkbox("Tampilkan Iklan", value=True)
    if show_ads:
        st.subheader("Iklan Sponsor")
        components.html(
            """
            <div style="background:#f0f2f6;padding:20px;border-radius:10px;text-align:center">
                <script type='text/javascript' 
                        src='//pl26562103.profitableratecpm.com/28/f9/95/28f9954a1d5bbf4924abe123c76a68d2.js'>
                </script>
                <p style="color:#888">Iklan akan muncul di sini</p>
            </div>
            """,
            height=300
        )

    # =========================================================
    # 🎞️ Pilih atau upload video
    # =========================================================
    video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.flv'))]
    st.write("📂 Video yang tersedia di folder ini:")
    selected_video = st.selectbox("Pilih video yang sudah ada:", video_files) if video_files else None

    uploaded_file = st.file_uploader(
        "📤 Atau upload video baru (MP4/FLV - codec H264/AAC)",
        type=['mp4', 'flv']
    )

    if uploaded_file:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"✅ Video '{uploaded_file.name}' berhasil diupload!")
        video_path = uploaded_file.name
    elif selected_video:
        video_path = selected_video
    else:
        video_path = None

    # =========================================================
    # 🔑 Input Stream Key dan mode video
    # =========================================================
    stream_key = st.text_input("Masukkan YouTube Stream Key", type="password")
    is_shorts = st.checkbox("Mode Shorts (720x1280)", value=False)

    # =========================================================
    # 🧾 Logging dan status
    # =========================================================
    log_placeholder = st.empty()
    logs = []

    def log_callback(msg):
        logs.append(msg)
        log_placeholder.text("\n".join(logs[-20:]))

    # =========================================================
    # ▶️ Tombol kontrol streaming
    # =========================================================
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Mulai Streaming"):
            if not video_path or not stream_key:
                st.error("❌ Harus pilih video dan isi stream key dulu!")
            else:
                thread = threading.Thread(
                    target=run_ffmpeg, args=(video_path, stream_key, is_shorts, log_callback), daemon=True)
                thread.start()
                st.success("🎥 Streaming dimulai ke YouTube!")

    with col2:
        if st.button("🛑 Stop Streaming"):
            os.system("pkill ffmpeg" if os.name != 'nt' else "taskkill /im ffmpeg.exe /f")
            st.warning("🛑 Streaming dihentikan!")

    # Menampilkan log terbaru
    log_placeholder.text("\n".join(logs[-20:]))


# =========================================================
# 🚀 Jalankan program
# =========================================================
if __name__ == "__main__":
    main()
