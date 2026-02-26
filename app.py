import json
import os
import sys
import random
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import argparse # Added for command-line arguments

import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, vfx

# Get the directory of the current script (app.py)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

URL = "https://karndiy.pythonanywhere.com/goldjsonv2"

# Default background selection logic (can be overridden by args)
BG_PATH_DEFAULT = os.path.join(SCRIPT_DIR, "assets", f"bg_{random.randint(0, 9):02d}.mp4")
OUT_VIDEO_PATH_DEFAULT = os.path.join(SCRIPT_DIR, "out", "output.mp4")
OUT_IMAGE_PATH_DEFAULT = os.path.join(SCRIPT_DIR, "out", "output_panel.jpg")

# Target vertical mobile resolution
W, H = 1080, 1920
DURATION = 10  # seconds
FPS = 15

# --- Customizable elements mapping (add more as assets are available) ---
BACKGROUND_THEMES = {
    "random": None, # Will use default random logic
    "elegant": os.path.join(SCRIPT_DIR, "assets", "bg_elegant.mp4"), # Example specific file
    "modern": os.path.join(SCRIPT_DIR, "assets", "bg_modern.mp4"),   # Example specific file
    # Add more themes and their corresponding file paths here
}

def fetch_entries(url: str) -> List[Dict[str, str]]:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        raise ValueError("Unexpected JSON format: expected a list")
    return data


def try_load_font(candidates: List[Tuple[str, int]]):
    """Try load fonts from a list of (path_or_name, size) and fall back to default."""
    for name, size in candidates:
        try:
            # If name is a filename path it will load; on Windows common fonts are available.
            return ImageFont.truetype(name, size=size)
        except Exception:
            continue
    # Fallback
    return ImageFont.load_default()


def contains_thai(text: str) -> bool:
    """Return True if any character is in the Thai Unicode block."""
    for ch in text:
        cp = ord(ch)
        if 0x0E00 <= cp <= 0x0E7F:
            return True
    return False


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    """Wrap text to fit max_width.

    - For languages with spaces, wrap by words.
    - For Thai (no spaces commonly), fall back to character-based wrapping.
    """
    lines: List[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue

        if contains_thai(paragraph) or " " not in paragraph:
            # Character-based greedy wrap (handles Thai and long unspaced strings)
            current = ""
            for ch in paragraph:
                trial = current + ch
                if draw.textlength(trial, font=font) <= max_width or not current:
                    current = trial
                else:
                    lines.append(current)
                    current = ch
            if current:
                lines.append(current)
        else:
            # Word-based wrap
            words = paragraph.split(" ")
            current = words[0]
            for w in words[1:]:
                trial = current + " " + w
                if draw.textlength(trial, font=font) <= max_width:
                    current = trial
                else:
                    lines.append(current)
                    current = w
            lines.append(current)
    return "\n".join(lines)


def make_text_clip(text: str, width: int, max_height: int,
                   font_color: Tuple[int, int, int] = (255, 255, 255),
                   bg_color: Tuple[int, int, int, int] = (0, 0, 0, 160),
                   pad: int = 24,
                   align: str = "ls") -> ImageClip:
    # Load fonts (prefer Thai-capable fonts)
    title_font = try_load_font([
        os.path.join(SCRIPT_DIR, "fonts", "THSarabunNew.ttf"), # Assuming a fonts folder
        ("C:/Windows/Fonts/THSarabunNew.ttf", 72),
        ("C:/Windows/Fonts/LeelawUI.ttf", 64),
        ("C:/Windows/Fonts/Tahoma.ttf", 60),
        ("THSarabunNew.ttf", 72),
        ("LeelawUI.ttf", 64),
        ("Tahoma.ttf", 60),
        ("Arial Unicode.ttf", 60),
        ("arialuni.ttf", 60),
    ])
    body_font = try_load_font([
        os.path.join(SCRIPT_DIR, "fonts", "THSarabunNew.ttf"),
        ("C:/Windows/Fonts/THSarabunNew.ttf", 56),
        ("C:/Windows/Fonts/LeelawUI.ttf", 50),
        ("C:/Windows/Fonts/Tahoma.ttf", 48),
        ("THSarabunNew.ttf", 56),
        ("LeelawUI.ttf", 50),
        ("Tahoma.ttf", 48),
        ("Arial Unicode.ttf", 48),
        ("arialuni.ttf", 48),
    ])

    # Prepare drawing surface for measuring
    dummy_img = Image.new("RGBA", (width, max_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(dummy_img)

    # Split text: first line as title if we detect a line break early
    parts = text.split("\n", 1)
    if len(parts) == 2:
        title, body = parts[0], parts[1]
    else:
        title, body = text, ""

    # Wrap to fit width minus padding
    content_width = width - 2 * pad
    title_wrapped = wrap_text(draw, title, title_font, content_width)
    body_wrapped = wrap_text(draw, body, body_font, content_width) if body else ""

    # Measure sizes
    title_bbox = draw.multiline_textbbox((0, 0), title_wrapped, font=title_font, spacing=6)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]

    body_h = 0
    if body_wrapped:
        body_bbox = draw.multiline_textbbox((0, 0), body_wrapped, font=body_font, spacing=6)
        body_h = body_bbox[3] - body_bbox[1]

    box_w = min(width, max(title_w, content_width) + 2 * pad)
    box_h = min(max_height, title_h + (12 if body_wrapped else 0) + body_h + 2 * pad)

    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Background rounded rectangle
    try:
        d.rounded_rectangle([(0, 0), (box_w - 1, box_h - 1)], radius=20, fill=bg_color)
    except Exception:
        d.rectangle([(0, 0), (box_w - 1, box_h - 1)], fill=bg_color)

    # Draw text
    cursor_y = pad
    d.multiline_text((pad, cursor_y), title_wrapped, font=title_font, fill=font_color, spacing=6, align="left")
    cursor_y += title_h + 12
    if body_wrapped:
        d.multiline_text((pad, cursor_y), body_wrapped, font=body_font, fill=font_color, spacing=6, align="left")

    # Convert to ImageClip
    np_img = np.array(img)
    clip = ImageClip(np_img)
    return clip


def format_entry(entry: Dict[str, str]) -> str:
    # Build a multi-line string with key fields
    asdate = entry.get("asdate", "-")
    ombuy = entry.get("ombuy", "-")
    omsell = entry.get("omsell", "-")
    blbuy = entry.get("blbuy", "-")
    blsell = entry.get("blsell", "-")
    diff = entry.get("diff", "-")
    goldspot = entry.get("goldspot", "-")
    bahtusd = entry.get("bahtusd", "-")

    header = f"Gold Prices • {asdate}"
    lines = [
        f"OM Buy:  {ombuy}  |  OM Sell: {omsell}",
        f"BL Buy:  {blbuy}  |  BL Sell: {blsell}",
        f"Diff: {diff}   Spot: {goldspot}   USD/THB: {bahtusd}",
    ]
    return header + "\n" + "\n".join(lines)


# --- Modern Thai panel rendering ---
TH_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
]


def parse_money(value: str) -> Optional[float]:
    try:
        return float(value.replace(",", ""))
    except Exception:
        return None


def thai_date_time(asdate: str) -> Tuple[str, str]:
    # Input example: '15/10/2568 17:23'
    try:
        date_part, time_part = asdate.split()
        d, m, y = date_part.split("/")
        day = int(d)
        month = int(m)
        year = int(y)
        month_name = TH_MONTHS[month - 1]
        date_str = f"{day} {month_name} {year}"
        time_str = f"เวลา {time_part} น."
        return date_str, time_str
    except Exception:
        return asdate, ""


def load_thai_font(candidates: List[Tuple[str, int]]):
    return try_load_font(candidates)


def arrow_and_color(delta: Optional[float]) -> Tuple[str, Tuple[int, int, int]]:
    if delta is None:
        return "—", (200, 200, 200)
    if delta > 0:
        return f"▲ {abs(delta):,.0f}", (46, 125, 50)  # green
    if delta < 0:
        return f"▼ {abs(delta):,.0f}", (211, 47, 47)  # red
    return "0", (180, 180, 180)


def draw_gradient(size: Tuple[int, int], color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> Image.Image:
    w, h = size
    grad = Image.new("RGB", (w, h), color1)
    # horizontal gradient
    for x in range(w):
        t = x / max(1, w - 1)
        r = int(color1[0] * (1 - t) + color2[0] * t)
        g = int(color1[1] * (1 - t) + color2[1] * t)
        b = int(color1[2] * (1 - t) + color2[2] * t)
        ImageDraw.Draw(grad).line([(x, 0), (x, h)], fill=(r, g, b))
    return grad


def _text_center_y(draw: ImageDraw.ImageDraw, box: Tuple[int, int, int, int], text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    x1, y1, x2, y2 = box
    bbox = draw.textbbox((0, 0), text, font=font)
    th = bbox[3] - bbox[1]
    return x1, int(y1 + (y2 - y1 - th) / 2)


def _text_right(draw: ImageDraw.ImageDraw, box: Tuple[int, int, int, int], text: str, font: ImageFont.FreeTypeFont, margin: int = 24) -> Tuple[int, int]:
    x1, y1, x2, y2 = box
    tw = draw.textlength(text, font=font)
    bbox = draw.textbbox((0, 0), text, font=font)
    th = bbox[3] - bbox[1]
    return x2 - margin - int(tw), int(y1 + (y2 - y1 - th) / 2)


def _measure_chip_width(draw: ImageDraw.ImageDraw, text_left: str, text_right: str,
                        font_left: ImageFont.FreeTypeFont, font_right: ImageFont.FreeTypeFont,
                        pad_x: int = 18, pad_y: int = 10) -> Tuple[int, int]:
    tlw = draw.textlength(text_left, font=font_left)
    trw = draw.textlength(text_right, font=font_right)
    h = max(
        draw.textbbox((0, 0), text_left, font=font_left)[3] - draw.textbbox((0, 0), text_left, font=font_left)[1],
        draw.textbbox((0, 0), text_right, font=font_right)[3] - draw.textbbox((0, 0), text_right, font=font_right)[1],
    ) + pad_y * 2
    w = int(tlw + trw + pad_x * 3)
    return w, h


def _draw_chip(base: Image.Image, xy: Tuple[int, int], text_left: str, text_right: str,
               font_left: ImageFont.FreeTypeFont, font_right: ImageFont.FreeTypeFont,
               bg: Tuple[int, int, int], fg_left=(255, 255, 255), fg_right=(255, 255, 255)) -> int:
    draw = ImageDraw.Draw(base)
    pad_y = 10
    pad_x = 18
    tlw = draw.textlength(text_left, font=font_left)
    trw = draw.textlength(text_right, font=font_right)
    h = max(
        draw.textbbox((0, 0), text_left, font=font_left)[3] - draw.textbbox((0, 0), text_left, font=font_left)[1],
        draw.textbbox((0, 0), text_right, font=font_right)[3] - draw.textbbox((0, 0), text_right, font=font_right)[1],
    ) + pad_y * 2
    w = int(tlw + trw + pad_x * 3)
    x, y = xy
    try:
        ImageDraw.Draw(base).rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    except Exception:
        ImageDraw.Draw(base).rectangle([x, y, x + w, y + h], fill=bg)
    # write texts
    ty = y + pad_y
    draw.text((x + pad_x, ty), text_left, font=font_left, fill=fg_left)
    draw.text((x + pad_x + tlw + pad_x // 2, ty), text_right, font=font_right, fill=fg_right)
    return w


def _draw_triangle(draw: ImageDraw.ImageDraw, center: Tuple[int, int], size: int, color: Tuple[int, int, int], up: bool = True):
    cx, cy = center
    if up:
        pts = [(cx, cy - size // 2), (cx - size // 2, cy + size // 2), (cx + size // 2, cy + size // 2)]
    else:
        pts = [(cx, cy + size // 2), (cx - size // 2, cy - size // 2), (cx + size // 2, cy - size // 2)]
    draw.polygon(pts, fill=color)


def make_panel_clip(entry: Dict[str, str], prev_entry: Optional[Dict[str, str]]) -> ImageClip:
    # Card size relative to screen
    card_w = int(W * 0.94)
    card_h = int(H * 0.55)
    radius = 32

    # Professional Color Scheme (Navy Blue + Gold)
    header_c1 = (25, 55, 109)      # Dark Navy Blue
    header_c2 = (41, 84, 144)      # Medium Navy Blue
    accent_gold = (212, 175, 55)   # Professional Gold
    table_bg = (255, 255, 255)
    table_head_bg = (240, 245, 250)  # Light blue-gray
    grid = (200, 210, 220)
    text_primary = (30, 30, 30)
    text_muted = (100, 110, 120)
    green = (34, 139, 34)
    red = (220, 53, 69)

    # Fonts
    title_font = load_thai_font([
        (os.path.join(SCRIPT_DIR, "fonts", "LeelawUI.ttf"), 60), # Assuming fonts folder
        ("C:/Windows/Fonts/LeelawUI.ttf", 60),
        ("C:/Windows/Fonts/THSarabunNew.ttf", 72),
        ("C:/Windows/Fonts/Tahoma.ttf", 56),
        ("C:/Windows/Fonts/segoeui.ttf", 56),
    ])
    head_font = load_thai_font([
        (os.path.join(SCRIPT_DIR, "fonts", "LeelawUI.ttf"), 48),
        ("C:/Windows/Fonts/LeelawUI.ttf", 48),
        ("C:/Windows/Fonts/THSarabunNew.ttf", 60),
        ("C:/Windows/Fonts/Tahoma.ttf", 44),
        ("C:/Windows/Fonts/segoeui.ttf", 44),
    ])
    label_font = load_thai_font([
        (os.path.join(SCRIPT_DIR, "fonts", "LeelawUI.ttf"), 46),
        ("C:/Windows/Fonts/LeelawUI.ttf", 46),
        ("C:/Windows/Fonts/THSarabunNew.ttf", 56),
        ("C:/Windows/Fonts/Tahoma.ttf", 42),
        ("C:/Windows/Fonts/segoeui.ttf", 42),
    ])
    num_font = load_thai_font([
        (os.path.join(SCRIPT_DIR, "fonts", "arialbd.ttf"), 48),
        ("C:/Windows/Fonts/arialbd.ttf", 48),
        ("C:/Windows/Fonts/Tahoma.ttf", 48),
        ("C:/Windows/Fonts/segoeuib.ttf", 48),
    ])
    chip_l_font = load_thai_font([
        (os.path.join(SCRIPT_DIR, "fonts", "LeelawUI.ttf"), 40),
        ("C:/Windows/Fonts/LeelawUI.ttf", 40),
        ("C:/Windows/Fonts/Tahoma.ttf", 36),
        ("C:/Windows/Fonts/segoeui.ttf", 36),
    ])
    chip_r_font = load_thai_font([
        (os.path.join(SCRIPT_DIR, "fonts", "arialbd.ttf"), 40),
        ("C:/Windows/Fonts/arialbd.ttf", 40),
        ("C:/Windows/Fonts/Tahoma.ttf", 40),
    ])
    small_font = load_thai_font([
        (os.path.join(SCRIPT_DIR, "fonts", "LeelawUI.ttf"), 40),
        ("C:/Windows/Fonts/LeelawUI.ttf", 40),
        ("C:/Windows/Fonts/Tahoma.ttf", 36),
        ("C:/Windows/Fonts/segoeui.ttf", 36),
    ])

    # Base image with rounded card
    img = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        draw.rounded_rectangle([(0, 0), (card_w - 1, card_h - 1)], radius=radius, fill=(255, 255, 255, 235))
    except Exception:
        draw.rectangle([(0, 0), (card_w - 1, card_h - 1)], fill=(255, 255, 255, 235))

    # Header gradient
    header_h = int(card_h * 0.20)
    grad = draw_gradient((card_w - 2, header_h), header_c1, header_c2)
    header_img = Image.new("RGBA", (card_w - 2, header_h))
    header_img.paste(grad, (0, 0))
    img.paste(header_img, (1, 1))

    # Header text with subtitle
    draw = ImageDraw.Draw(img)
    title = "ราคาทองคำวันนี้"
    subtitle = "ข้อมูลจากสมาคมค้าทองคำ"
    
    tw = draw.textlength(title, font=title_font)
    draw.text(((card_w - tw) // 2, int(header_h * 0.20)), title, font=title_font, fill=(255, 255, 255))
    
    # Subtitle in gold
    stw = draw.textlength(subtitle, font=small_font)
    draw.text(((card_w - stw) // 2, int(header_h * 0.60)), subtitle, font=small_font, fill=accent_gold)

    # Metrics chip row (Diff) — centered
    chip_y = header_h + int(card_h * 0.02)
    print(f"c_1 -> {chip_y}")
    goldspot = entry.get("goldspot", "-")
    bahtusd = entry.get("bahtusd", "-")
    diff_x = entry.get("diff", "-")
    mw, _ = _measure_chip_width(draw, "Diff", f"{diff_x}", chip_l_font, chip_r_font,18,16)
    diff_val = parse_money(str(diff_x))

    dv = (diff_val or 0)
    is_up = dv > 0                       # or >= 0 if zero should be "UP"
    m_head = "ขาขึ้น" if is_up else "ขาลง"
    xbg = green if is_up else red

   
    start_x = (card_w - mw) // 2
    _draw_chip(
        img,
        (start_x, chip_y),
        m_head,
        f"{diff_x}",
        chip_l_font,
        chip_r_font,
        bg=xbg,
    )
  

    # Table area
    table_x = int(card_w * 0.04)
    table_y = chip_y + int(card_h * 0.10)
    table_w = card_w - 2 * table_x
    row_h = int((card_h - table_y - int(card_h * 0.16)) / 4)

    col_left_w = int(table_w * 0.42)
    col_mid_w = int((table_w - col_left_w) / 2)
    col_right_w = table_w - col_left_w - col_mid_w

    def cell_rect(row: int, col: int) -> Tuple[int, int, int, int]:
        x = table_x + [0, col_left_w, col_left_w + col_mid_w][col]
        w = [col_left_w, col_mid_w, col_right_w][col]
        y = table_y + row * row_h
        return x, y, x + w, y + row_h

    # Header row backgrounds
    draw.rectangle(cell_rect(0, 0), fill=(246, 246, 246))
    draw.rectangle(cell_rect(0, 1), fill=table_head_bg)
    draw.rectangle(cell_rect(0, 2), fill=table_head_bg)

    # Grid lines
    for r in range(5):
        y = table_y + r * row_h
        draw.line([(table_x, y), (table_x + table_w, y)], fill=grid, width=2)
    # verticals
    draw.line([(table_x, table_y), (table_x, table_y + 4 * row_h)], fill=grid, width=2)
    draw.line([(table_x + col_left_w, table_y), (table_x + col_left_w, table_y + 4 * row_h)], fill=grid, width=2)
    draw.line([(table_x + col_left_w + col_mid_w, table_y), (table_x + col_left_w + col_mid_w, table_y + 4 * row_h)], fill=grid, width=2)
    draw.line([(table_x + table_w, table_y), (table_x + table_w, table_y + 4 * row_h)], fill=grid, width=2)

    # Header labels
    left_header_box = cell_rect(0, 0)
    lx, ly = _text_center_y(draw, left_header_box, "96.5%", head_font)
    draw.text((lx + 16, ly), "96.5%", font=head_font, fill=text_primary)
    hmid_box = cell_rect(0, 1)
    hright_box = cell_rect(0, 2)
    mx, my = _text_center_y(draw, hmid_box, "รับซื้อ", head_font)
    rx, ry = _text_center_y(draw, hright_box, "ขายออก", head_font)
    draw.text((mx + 16, my), "รับซื้อ", font=head_font, fill=text_primary)
    draw.text((rx + 16, ry), "ขายออก", font=head_font, fill=text_primary)

    # Values
    def draw_row(row_idx: int, label: str, left_val: str, right_val: str):
        lbox = cell_rect(row_idx, 0)
        mbox = cell_rect(row_idx, 1)
        rbox = cell_rect(row_idx, 2)
        lx, ly = _text_center_y(draw, lbox, label, label_font)
        draw.text((lx + 16, ly), label, font=label_font, fill=text_primary)
        # Numbers right-aligned within cells
        lv = f"{parse_money(left_val):,.2f}" if parse_money(left_val) is not None else left_val
        rv = f"{parse_money(right_val):,.2f}" if parse_money(right_val) is not None else right_val
        mx, my = _text_right(draw, mbox, lv, num_font, margin=24)
        rx, ry = _text_right(draw, rbox, rv, num_font, margin=24)
        draw.text((mx, my), lv, font=num_font, fill=green)
        draw.text((rx, ry), rv, font=num_font, fill=green)

    draw_row(1, "ทองคำแท่ง", entry.get("blbuy", "-"), entry.get("blsell", "-"))
    draw_row(2, "ทองรูปพรรณ", entry.get("ombuy", "-"), entry.get("omsell", "-"))

    # Diff row (วันนี้ ...)
    # Compute deltas using previous entry if available
    delta_buy = None
    delta_sell = None
    diff_text = None
    diff_text = entry.get("diff", "")
    if prev_entry:
        cb = parse_money(entry.get("blbuy", ""))
        pb = parse_money(prev_entry.get("blbuy", ""))
        cs = parse_money(entry.get("blsell", ""))
        ps = parse_money(prev_entry.get("blsell", ""))
        if cb is not None and pb is not None:
            delta_buy = cb - pb
        if cs is not None and ps is not None:
            delta_sell = cs - ps

    lbox = cell_rect(3, 0)
    mbox = cell_rect(3, 1)
    rbox = cell_rect(3, 2)
    lx, ly = _text_center_y(draw, lbox, "วันนี้", label_font)
    draw.text((lx + 16, ly), "วันนี้", font=label_font, fill=text_primary)
    # Safely parse diff (handles commas/empty) and derive colors/arrows
    delta_val = parse_money(diff_text)
    delta_color = green if (delta_val or 0) > 0 else red if (delta_val or 0) < 0 else text_muted
    is_up = (delta_val or 0) >= 0
    
    # Merge both cells - draw in the center spanning both columns
    tri_size = 24
    # Calculate merged cell area (columns 1 and 2)
    merged_x1 = mbox[0]
    merged_x2 = rbox[2]
    merged_y1 = mbox[1]
    merged_y2 = mbox[3]
    merged_w = merged_x2 - merged_x1
    
    # Center the text in merged area
    text_w = draw.textlength(diff_text + " ", font=label_font)
    total_w = tri_size + 10 + text_w
    start_x = merged_x1 + (merged_w - total_w) // 2
    center_y = (merged_y1 + merged_y2) // 2
    
    # Draw triangle and text centered
    _draw_triangle(draw, (start_x + tri_size // 2, center_y), tri_size, delta_color, up=is_up)
    draw.text((start_x + tri_size + 10, center_y - 16), diff_text + " ", font=label_font, fill=delta_color)



    # Metrics chips row (Gold Spot, USD/THB)
    chip_pad_x = int(card_w * 0.04)
    chip_y = 850 + int(card_h * 0.02)
    print(f"c_2 -> {chip_y}")
    goldspot = entry.get("goldspot", "-")
    bahtusd = entry.get("bahtusd", "-")
    diff_x = entry.get("diff", "-")
    # left chip: Gold Spot
    x_cursor = chip_pad_x
    chip_w1 = _draw_chip(
        img,
        (x_cursor, chip_y),
        "Gold Spot",
        f"${goldspot}",
        chip_l_font,
        chip_r_font,
        bg=accent_gold,
    )
    x_cursor += chip_w1 + 16
    # right chip: USD/THB
    chip_w2 =   _draw_chip(
        img,
        (x_cursor, chip_y),
        "USD/THB",
        f"{bahtusd}",
        chip_l_font,
        chip_r_font,
        bg=header_c2,
    )

   



    # Footer date/time line
    date_str, time_str = thai_date_time(entry.get("asdate", ""))
    left_info = date_str
    mid_info = time_str
    right_info = f"(ครั้งที่ {entry.get('nqy', '-')})"
    baseline_y = card_h - int(card_h * 0.06)
    # left
    draw.text((int(card_w * 0.05), baseline_y), left_info, font=small_font, fill=text_muted)
    # center
    mid_w = draw.textlength(mid_info, font=small_font)
    draw.text(((card_w - mid_w) // 2, baseline_y), mid_info, font=small_font, fill=text_muted)
    # right
    right_w = draw.textlength(right_info, font=small_font)
    draw.text((card_w - right_w - int(card_w * 0.05), baseline_y), right_info, font=small_font, fill=text_muted)

    np_img = np.array(img)
    return ImageClip(np_img)


def ensure_background(bg_path: str) -> VideoFileClip:
    if not os.path.exists(bg_path):
        raise FileNotFoundError(f"Background video not found: {bg_path}")
    bg = VideoFileClip(bg_path)
    if bg.h < H:
        bg_resized = bg.fx(vfx.resize, height=H)
    else:
        bg_resized = bg.fx(vfx.resize, width=W)

    scale_w = W / bg_resized.w
    scale_h = H / bg_resized.h
    scale = max(scale_w, scale_h)

    bg_cover = bg_resized.fx(
        vfx.resize,
        newsize=(int(bg_resized.w * scale), int(bg_resized.h * scale))
    )

    x_center = bg_cover.w // 2
    y_center = bg_cover.h // 2
    x1 = int(x_center - W / 2)
    y1 = int(y_center - H / 2)

    bg_cropped = bg_cover.fx(
        vfx.crop,
        x1=x1, y1=y1, x2=x1 + W, y2=y1 + H
    )

    if bg_cropped.duration < DURATION:
        bg_cropped = bg_cropped.fx(vfx.loop, duration=DURATION)

    return bg_cropped.subclip(0, DURATION).without_audio()


def build_video(entries: List[Dict[str, str]], out_video_path: str, 
                background_theme: str = "random", 
                custom_message: str = "", 
                logo_url: str = "",
                out_image_path: Optional[str] = None) -> None:
    
    # Determine background video path based on theme
    bg_video_path = BG_PATH_DEFAULT
    if background_theme in BACKGROUND_THEMES and BACKGROUND_THEMES[background_theme] is not None:
        bg_video_path = BACKGROUND_THEMES[background_theme]
    
    # Create background video clip
    bg = ensure_background(bg_video_path)
    
    all_clips = [bg]

    # Show the latest panel immediately for the full duration (no waiting/segments)
    latest = entries[-1] if entries else {}
    prev = entries[-2] if len(entries) >= 2 else None
    panel = (
    make_panel_clip(latest, prev)
    .set_start(0)
    .set_duration(DURATION)
    .set_position(("center", int(H * 0.14))))
    all_clips.append(panel)

    # Save static image if path is provided
    if out_image_path:
        try:
            # Get the raw PIL Image from the panel clip
            # This requires rendering the first frame of the ImageClip
            # A simpler way is to extract the PIL Image used to create the clip directly
            if isinstance(panel, ImageClip):
                panel_pil_image = Image.fromarray(panel.img)
            else:
                # If panel is a CompositeVideoClip or similar, render a frame
                panel_pil_image = Image.fromarray(panel.get_frame(0))

            # Ensure output directory exists for the image
            os.makedirs(os.path.dirname(out_image_path), exist_ok=True)
            panel_pil_image.save(out_image_path)
            print(f"[APP] Saved static panel image: {out_image_path}")
        except Exception as e:
            print(f"Error saving static panel image to {out_image_path}: {e}")
   
    # Footer watermark/info (persistent for entire duration)
    footer_text = "ที่มา: สมาคมค้าทองคำ"
    footer_clip = make_text_clip(footer_text, width=int(W * 0.94), max_height=140,
                                 font_color=(255, 255, 255), bg_color=(25, 55, 109, 200), pad=28)
    footer_clip = (
    footer_clip
    .set_position(("center", H - footer_clip.h - 180))
    .set_duration(DURATION))
    all_clips.append(footer_clip)

    # Add Custom Message if provided
    if custom_message:
        custom_msg_clip = make_text_clip(custom_message, width=int(W * 0.8), max_height=100,
                                         font_color=(255, 255, 0), bg_color=(0, 0, 0, 180), pad=15)
        # Position above the footer, adjust as needed
        custom_msg_clip = (
        custom_msg_clip
        .set_position(("center", H - custom_msg_clip.h - footer_clip.h - 200))
        .set_duration(DURATION))
        all_clips.append(custom_msg_clip)

    # Add Logo if URL provided
    if logo_url:
        try:
            logo_response = requests.get(logo_url, stream=True, timeout=10)
            logo_response.raise_for_status()
            logo_img = Image.open(logo_response.raw)
            
            # Resize logo to fit (e.g., max width 200, maintain aspect ratio)
            max_logo_w = 200
            if logo_img.width > max_logo_w:
                logo_img = logo_img.resize((max_logo_w, int(logo_img.height * (max_logo_w / logo_img.width))))

            logo_clip = ImageClip(np.array(logo_img)).set_duration(DURATION)
            # Position logo (e.g., top-right corner)
            logo_clip = logo_clip.set_position((W - logo_img.width - 30, 30))
            all_clips.append(logo_clip)
        except Exception as e:
            print(f"Error adding logo from {logo_url}: {e}")

    comp = CompositeVideoClip(all_clips, size=(W, H))
    comp.write_videofile(out_video_path, fps=FPS, codec="libx264", audio=False, preset="medium", threads=4)


def main():
    parser = argparse.ArgumentParser(description="Generate a gold price video with customization.")
    parser.add_argument("--background_theme", type=str, default="random",
                        help="Theme for background video (e.g., 'random', 'elegant', 'modern').")
    parser.add_argument("--custom_message", type=str, default="",
                        help="Custom message to display in the video.")
    parser.add_argument("--logo_url", type=str, default="",
                        help="URL of a logo image to overlay on the video.")
    parser.add_argument("--output_video_path", type=str, default=OUT_VIDEO_PATH_DEFAULT,
                        help="Path to save the output video.")
    parser.add_argument("--output_image_path", type=str, default=OUT_IMAGE_PATH_DEFAULT,
                        help="Path to save the output static image.")
    args = parser.parse_args()

    try:
        entries = fetch_entries(URL)
    except Exception as e:
        print(f"Failed to fetch remote data: {e}")
        # Fallback to local cache if exists
        cache = os.path.join(SCRIPT_DIR, "data", "gold_prices.json")
        if os.path.exists(cache):
            with open(cache, "r", encoding="utf-8") as f:
                entries = json.load(f)
        else:
            sys.exit(1)

    # Persist a local cache snapshot for repeatability
    os.makedirs(os.path.join(SCRIPT_DIR, "data"), exist_ok=True)
    try:
        with open(os.path.join(SCRIPT_DIR, "data", "gold_prices.json"), "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    build_video(entries, args.output_video_path, 
                background_theme=args.background_theme, 
                custom_message=args.custom_message, 
                logo_url=args.logo_url,
                out_image_path=args.output_image_path)
    print(f"Saved video: {args.output_video_path}")
    print(f"Saved image: {args.output_image_path}")


if __name__ == "__main__":
    main()