"""
📄 Smart Doc Scanner
Aplikasi scan dokumen berbasis Streamlit — mirip CamScanner / vFlat Scanner.
Fitur:
- Deteksi otomatis tepi dokumen & perspective correction
- Preview sebelum disimpan, bisa scan ulang jika belum pas
- Filter hasil scan (Warna, Abu-abu, Hitam-Putih)
- Rotasi manual
- Multi halaman + export ke PDF / ZIP gambar
"""

import io
import zipfile
from datetime import datetime

import cv2
import img2pdf
import numpy as np
import streamlit as st
from PIL import Image

from scanner_utils import (
    apply_filter,
    auto_detect_and_warp,
    cv2_to_pil,
    pil_to_cv2,
    rotate_image,
)

# ----------------------------------------------------------------------------
# Konfigurasi halaman
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Doc Scanner",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------------
# CSS kustom agar tampilan responsif & nyaman di layar HP
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 720px;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 0.6rem 0.5rem;
        font-weight: 600;
        font-size: 1rem;
    }
    div[data-testid="stCameraInput"] video, div[data-testid="stCameraInput"] img {
        border-radius: 14px;
    }
    .page-thumb {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 4px;
    }
    .scan-title {
        text-align:center;
        font-size:1.9rem;
        font-weight:800;
        margin-bottom:0;
    }
    .scan-sub {
        text-align:center;
        color:#6b6b6b;
        margin-top:2px;
        margin-bottom:1.2rem;
        font-size:0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# State
# ----------------------------------------------------------------------------
if "pages" not in st.session_state:
    st.session_state.pages = []          # daftar halaman final (bytes JPEG)
if "camera_key" not in st.session_state:
    st.session_state.camera_key = 0      # untuk trik "scan ulang"
if "rotation" not in st.session_state:
    st.session_state.rotation = 0
if "captured_raw" not in st.session_state:
    st.session_state.captured_raw = None # foto asli hasil kamera (cv2 array)

st.markdown('<p class="scan-title">📄 Smart Doc Scanner</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="scan-sub">Scan dokumen langsung dari kamera HP kamu — otomatis '
    'terdeteksi & terpotong rapi</p>',
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# 1. Ambil foto
# ----------------------------------------------------------------------------
st.subheader("1️⃣ Ambil Foto Dokumen")
img_file = st.camera_input(
    "Arahkan kamera ke dokumen, pastikan seluruh sisi kertas terlihat",
    key=f"camera_{st.session_state.camera_key}",
)

if img_file is not None:
    pil_img = Image.open(img_file).convert("RGB")
    st.session_state.captured_raw = pil_to_cv2(pil_img)
    st.session_state.rotation = 0  # reset rotasi tiap foto baru

# ----------------------------------------------------------------------------
# 2. Preview & proses
# ----------------------------------------------------------------------------
if st.session_state.captured_raw is not None:
    st.subheader("2️⃣ Tinjau Hasil Scan")

    raw = st.session_state.captured_raw
    raw = rotate_image(raw, st.session_state.rotation)

    col_r1, col_r2, _ = st.columns([1, 1, 2])
    with col_r1:
        if st.button("↺ Putar Kiri"):
            st.session_state.rotation = (st.session_state.rotation - 90) % 360
            st.rerun()
    with col_r2:
        if st.button("↻ Putar Kanan"):
            st.session_state.rotation = (st.session_state.rotation + 90) % 360
            st.rerun()

    mode = st.radio(
        "Mode deteksi",
        ["🤖 Otomatis (deteksi tepi)", "✋ Gunakan foto penuh (tanpa crop)"],
        horizontal=True,
    )

    warped, found = (None, False)
    if mode.startswith("🤖"):
        warped, found = auto_detect_and_warp(raw)
        if not found:
            st.warning(
                "⚠️ Tepi dokumen tidak terdeteksi dengan jelas. "
                "Menampilkan foto penuh — kamu bisa pindah ke mode manual "
                "atau foto ulang dengan pencahayaan lebih baik / latar polos."
            )
            warped = raw
    else:
        warped = raw

    filter_choice = st.select_slider(
        "🎨 Filter hasil scan",
        options=["Warna Asli", "Ditingkatkan (Auto)", "Abu-abu", "Hitam-Putih (Dokumen)"],
        value="Ditingkatkan (Auto)",
    )
    final_img = apply_filter(warped, filter_choice)

    st.markdown("**Preview sebelum disimpan:**")
    c1, c2 = st.columns(2)
    with c1:
        st.image(cv2_to_pil(raw), caption="Foto Asli", use_container_width=True)
    with c2:
        st.image(cv2_to_pil(final_img), caption="Hasil Scan", use_container_width=True)

    st.markdown("---")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🔄 Scan Ulang", type="secondary"):
            st.session_state.captured_raw = None
            st.session_state.camera_key += 1
            st.rerun()
    with b2:
        if st.button("✅ Simpan Halaman Ini", type="primary"):
            pil_final = cv2_to_pil(final_img)
            buf = io.BytesIO()
            pil_final.save(buf, format="JPEG", quality=92)
            st.session_state.pages.append(buf.getvalue())
            st.session_state.captured_raw = None
            st.session_state.camera_key += 1
            st.success(f"Halaman {len(st.session_state.pages)} tersimpan!")
            st.rerun()

# ----------------------------------------------------------------------------
# 3. Galeri halaman tersimpan
# ----------------------------------------------------------------------------
if st.session_state.pages:
    st.subheader(f"3️⃣ Halaman Tersimpan ({len(st.session_state.pages)})")

    n_cols = 3
    rows = (len(st.session_state.pages) + n_cols - 1) // n_cols
    idx = 0
    for _ in range(rows):
        cols = st.columns(n_cols)
        for c in cols:
            if idx >= len(st.session_state.pages):
                break
            with c:
                st.image(
                    st.session_state.pages[idx],
                    caption=f"Hal. {idx + 1}",
                    use_container_width=True,
                )
                if st.button("🗑️ Hapus", key=f"del_{idx}"):
                    st.session_state.pages.pop(idx)
                    st.rerun()
            idx += 1

    st.markdown("---")
    st.subheader("4️⃣ Simpan / Unduh")

    file_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    dcol1, dcol2, dcol3 = st.columns(3)

    with dcol1:
        pdf_bytes = img2pdf.convert(st.session_state.pages)
        st.download_button(
            "⬇️ Unduh PDF",
            data=pdf_bytes,
            file_name=f"scan_{file_stamp}.pdf",
            mime="application/pdf",
        )

    with dcol2:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            for i, page in enumerate(st.session_state.pages, start=1):
                zf.writestr(f"halaman_{i}.jpg", page)
        st.download_button(
            "⬇️ Unduh ZIP",
            data=zip_buf.getvalue(),
            file_name=f"scan_{file_stamp}.zip",
            mime="application/zip",
        )

    with dcol3:
        if st.button("🗑️ Hapus Semua"):
            st.session_state.pages = []
            st.rerun()
else:
    st.info("Belum ada halaman tersimpan. Ambil foto lalu simpan hasil scan-mu di atas.")

st.markdown("---")
st.caption("Dibuat dengan Streamlit + OpenCV • Buka dari browser HP untuk akses kamera langsung 📱")
