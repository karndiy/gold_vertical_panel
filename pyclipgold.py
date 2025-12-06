import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Tuple, Optional

import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.Resize import Resize
from moviepy.video.fx.Loop import Loop
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.video.fx.CrossFadeOut import CrossFadeOut
from moviepy.video.fx.Crop import Crop


URL = "https://karndiy.pythonanywhere.com/goldjsonv2"
BG_PATH = os.path.join("assets", "bg.mp4")
OUT_PATH = "out/output.mp4"

# Target vertical mobile resolution
W, H = 1080, 1920
DURATION = 10  # seconds
FPS = 15


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


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        if not words:
            lines.append("")
            continue
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
    # Load fonts (try common system fonts, then fallback)
    title_font = try_load_font([
        ("C:/Windows/Fonts/arialbd.ttf", 64),
        ("C:/Windows/Fonts/segoeuib.ttf", 64),
        ("arialbd.ttf", 64),
        ("Arial.ttf", 64),
    ])
    body_font = try_load_font([
        ("C:/Windows/Fonts/arial.ttf", 48),
        ("C:/Windows/Fonts/segoeui.ttf", 48),
        ("arial.ttf", 48),
        ("Arial.ttf", 48),
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
    card_w = int(W * 0.92)
    card_h = int(H * 0.52)
    radius = 28

    # Colors
    header_c1 = (255, 167, 38)   # #FFA726
    header_c2 = (251, 140, 0)    # #FB8C00
    table_bg = (255, 255, 255)
    table_head_bg = (255, 248, 225)  # light yellow
    grid = (224, 224, 224)
    text_primary = (34, 34, 34)
    text_muted = (120, 120, 120)
    green = (46, 125, 50)

    # Fonts
    title_font = load_thai_font([
        ("C:/Windows/Fonts/LeelawUI.ttf", 60),
        ("C:/Windows/Fonts/THSarabunNew.ttf", 72),
        ("C:/Windows/Fonts/Tahoma.ttf", 56),
        ("C:/Windows/Fonts/segoeui.ttf", 56),
    ])
    head_font = load_thai_font([
        ("C:/Windows/Fonts/LeelawUI.ttf", 48),
        ("C:/Windows/Fonts/THSarabunNew.ttf", 60),
        ("C:/Windows/Fonts/Tahoma.ttf", 44),
        ("C:/Windows/Fonts/segoeui.ttf", 44),
    ])
    label_font = load_thai_font([
        ("C:/Windows/Fonts/LeelawUI.ttf", 46),
        ("C:/Windows/Fonts/THSarabunNew.ttf", 56),
        ("C:/Windows/Fonts/Tahoma.ttf", 42),
        ("C:/Windows/Fonts/segoeui.ttf", 42),
    ])
    num_font = load_thai_font([
        ("C:/Windows/Fonts/arialbd.ttf", 48),
        ("C:/Windows/Fonts/Tahoma.ttf", 48),
        ("C:/Windows/Fonts/segoeuib.ttf", 48),
    ])
    chip_l_font = load_thai_font([
        ("C:/Windows/Fonts/LeelawUI.ttf", 40),
        ("C:/Windows/Fonts/Tahoma.ttf", 36),
        ("C:/Windows/Fonts/segoeui.ttf", 36),
    ])
    chip_r_font = load_thai_font([
        ("C:/Windows/Fonts/arialbd.ttf", 40),
        ("C:/Windows/Fonts/Tahoma.ttf", 40),
    ])
    small_font = load_thai_font([
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

    # Header text
    title = "ราคาทองตามประกาศสมาคมค้าทองคำ"
    draw = ImageDraw.Draw(img)
    tw = draw.textlength(title, font=title_font)
    draw.text(((card_w - tw) // 2, int(header_h * 0.28)), title, font=title_font, fill=(255, 255, 255))

    # Metrics chips row (Gold Spot, USD/THB)
    chip_pad_x = int(card_w * 0.04)
    chip_y = header_h + int(card_h * 0.02)
    goldspot = entry.get("goldspot", "-")
    bahtusd = entry.get("bahtusd", "-")
    # left chip: Gold Spot
    x_cursor = chip_pad_x
    chip_w1 = _draw_chip(
        img,
        (x_cursor, chip_y),
        "Gold Spot",
        f"${goldspot}",
        chip_l_font,
        chip_r_font,
        bg=(255, 153, 0),
    )
    x_cursor += chip_w1 + 16
    # right chip: USD/THB
    _draw_chip(
        img,
        (x_cursor, chip_y),
        "USD/THB",
        f"{bahtusd}",
        chip_l_font,
        chip_r_font,
        bg=(0, 150, 136),
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
    buy_text, buy_color = arrow_and_color(delta_buy)
    sell_text, sell_color = arrow_and_color(delta_sell)
    # draw small triangle icon + value
    tri_size = 24
    up_buy = (delta_buy or 0) >= 0
    up_sell = (delta_sell or 0) >= 0
    # buy cell
    bx, by = _text_center_y(draw, mbox, buy_text, label_font)
    _draw_triangle(draw, (mbox[0] + 28, by + 16), tri_size, buy_color, up=up_buy)
    draw.text((mbox[0] + 28 + tri_size + 10, by), buy_text, font=label_font, fill=buy_color)
    # sell cell
    sx, sy = _text_center_y(draw, rbox, sell_text, label_font)
    _draw_triangle(draw, (rbox[0] + 28, sy + 16), tri_size, sell_color, up=up_sell)
    draw.text((rbox[0] + 28 + tri_size + 10, sy), sell_text, font=label_font, fill=sell_color)

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
    # Fill and center-crop to vertical 1080x1920
    if bg.h < H:
        bg_resized = bg.with_effects([Resize(height=H)])
    else:
        bg_resized = bg.with_effects([Resize(width=W)])
    # Now scale to cover both dims
    scale_w = W / bg_resized.w
    scale_h = H / bg_resized.h
    scale = max(scale_w, scale_h)
    new_w = int(bg_resized.w * scale)
    new_h = int(bg_resized.h * scale)
    bg_cover = bg_resized.with_effects([Resize(new_size=(new_w, new_h))])
    x_center = bg_cover.w // 2
    y_center = bg_cover.h // 2
    x1 = int(x_center - W / 2)
    y1 = int(y_center - H / 2)
    bg_cropped = bg_cover.with_effects([Crop(x1=x1, y1=y1, x2=x1 + W, y2=y1 + H)])

    # Loop or trim to DURATION
    if bg_cropped.duration < DURATION:
        loops = int(np.ceil(DURATION / bg_cropped.duration))
        looped = bg_cropped.with_effects([Loop(n=loops)]).with_duration(DURATION)
        return looped.without_audio()
    else:
        return bg_cropped.subclipped(0, DURATION).without_audio()


def build_video(entries: List[Dict[str, str]], out_path: str) -> None:
    bg = ensure_background(BG_PATH)

    # Show the latest panel immediately for the full duration (no waiting/segments)
    latest = entries[-1] if entries else {}
    prev = entries[-2] if len(entries) >= 2 else None
    panel = make_panel_clip(latest, prev).with_start(0).with_duration(DURATION).with_position(("center", int(H * 0.14)))

    # Footer watermark/info (persistent for entire duration)
    footer_text = "Data: karndiy.pythonanywhere.com/goldjsonv2"
    footer_clip = make_text_clip(footer_text, width=int(W * 0.92), max_height=140,
                                 font_color=(230, 230, 230), bg_color=(0, 0, 0, 120), pad=16)
    footer_clip = footer_clip.with_position(("center", H - footer_clip.h - 40)).with_duration(DURATION)

    comp = CompositeVideoClip([bg, footer_clip, panel], size=(W, H))
    comp.write_videofile(out_path, fps=FPS, codec="libx264", audio=False, preset="medium", threads=4)


def main():
    try:
        entries = fetch_entries(URL)
    except Exception as e:
        print(f"Failed to fetch remote data: {e}")
        # Fallback to local cache if exists
        cache = os.path.join("data", "gold_prices.json")
        if os.path.exists(cache):
            with open(cache, "r", encoding="utf-8") as f:
                entries = json.load(f)
        else:
            sys.exit(1)

    # Persist a local cache snapshot for repeatability
    os.makedirs("data", exist_ok=True)
    try:
        with open(os.path.join("data", "gold_prices.json"), "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    build_video(entries, OUT_PATH)
    print(f"Saved: {OUT_PATH}")


if __name__ == "__main__":
    main()
