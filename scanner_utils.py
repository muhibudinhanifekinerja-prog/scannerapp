"""
Fungsi-fungsi inti pemrosesan citra untuk Smart Doc Scanner:
- Deteksi otomatis kontur dokumen (tepi kertas)
- Perspective transform ("meratakan" hasil foto dokumen)
- Filter tampilan hasil scan
- Konversi PIL <-> OpenCV, rotasi
"""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


# ----------------------------------------------------------------------------
# Konversi format gambar
# ----------------------------------------------------------------------------
def pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    arr = np.array(pil_img.convert("RGB"))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def cv2_to_pil(cv_img: np.ndarray) -> Image.Image:
    if len(cv_img.shape) == 2:  # grayscale / binary
        return Image.fromarray(cv_img)
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def rotate_image(cv_img: np.ndarray, angle: int) -> np.ndarray:
    angle = angle % 360
    if angle == 0:
        return cv_img
    if angle == 90:
        return cv2.rotate(cv_img, cv2.ROTATE_90_CLOCKWISE)
    if angle == 180:
        return cv2.rotate(cv_img, cv2.ROTATE_180)
    if angle == 270:
        return cv2.rotate(cv_img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return cv_img


# ----------------------------------------------------------------------------
# Deteksi tepi dokumen + perspective transform
# ----------------------------------------------------------------------------
def _order_points(pts: np.ndarray) -> np.ndarray:
    """Urutkan 4 titik: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left  (x+y terkecil)
    rect[2] = pts[np.argmax(s)]   # bottom-right (x+y terbesar)

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right (x-y terkecil)
    rect[3] = pts[np.argmax(diff)]  # bottom-left (x-y terbesar)
    return rect


def _four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
    rect = _order_points(pts)
    (tl, tr, br, bl) = rect

    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_width = max(int(width_a), int(width_b))

    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_height = max(int(height_a), int(height_b))

    max_width = max(max_width, 1)
    max_height = max(max_height, 1)

    dst = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype="float32",
    )

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))
    return warped


def _find_document_contour(image: np.ndarray, resize_height: int = 700):
    """Cari kontur 4-titik terbesar yang menyerupai selembar dokumen."""
    orig_h, orig_w = image.shape[:2]
    ratio = orig_h / float(resize_height)
    resized = cv2.resize(image, (int(orig_w / ratio), resize_height))

    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    edged = cv2.dilate(edged, np.ones((3, 3), np.uint8), iterations=1)
    edged = cv2.erode(edged, np.ones((3, 3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    img_area = resized.shape[0] * resized.shape[1]

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4 and cv2.contourArea(approx) > 0.2 * img_area:
            return approx.reshape(4, 2).astype("float32") * ratio

    return None


def auto_detect_and_warp(image: np.ndarray):
    """
    Mendeteksi dokumen secara otomatis lalu meratakan perspektifnya.
    Mengembalikan tuple: (gambar_hasil, berhasil_terdeteksi: bool)
    """
    contour = _find_document_contour(image)
    if contour is None:
        return image, False

    warped = _four_point_transform(image, contour)
    return warped, True


# ----------------------------------------------------------------------------
# Filter hasil scan
# ----------------------------------------------------------------------------
def apply_filter(image: np.ndarray, mode: str) -> np.ndarray:
    if mode == "Warna Asli":
        return image

    if mode == "Abu-abu":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray

    if mode == "Hitam-Putih (Dokumen)":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            25,
            15,
        )
        return thresh

    if mode == "Ditingkatkan (Auto)":
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge((l, a, b))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        enhanced = cv2.convertScaleAbs(enhanced, alpha=1.08, beta=8)
        return enhanced

    return image
