import zlib
import struct
import math
import os

def create_png(width, height, get_pixel_fn):
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # Filter byte 0
        for x in range(width):
            r, g, b, a = get_pixel_fn(x, y, width, height)
            raw_data.extend((r, g, b, a))

    compressed = zlib.compress(bytes(raw_data), 9)

    def make_chunk(chunk_type, data):
        length = struct.pack(">I", len(data))
        crc = struct.pack(">I", zlib.crc32(chunk_type + data) & 0xffffffff)
        return length + chunk_type + data + crc

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png.extend(make_chunk(b"IHDR", ihdr))
    png.extend(make_chunk(b"IDAT", compressed))
    png.extend(make_chunk(b"IEND", b""))
    return bytes(png)

def inside_rounded_rect(x, y, w, h, rx, ry):
    # Returns distance to rounded rect boundary (negative = inside)
    # Map (x, y) relative to center
    cx, cy = w / 2.0, h / 2.0
    px, py = abs(x - cx), abs(y - cy)
    dx = px - (cx - rx)
    dy = py - (cy - ry)
    if dx > 0 and dy > 0:
        dist = math.hypot(dx, dy) - rx
        return dist
    return max(dx - rx, dy - ry)

def inside_flame(x, y, cx, cy, scale_w, scale_h):
    # Flame contour approximation
    nx = (x - cx) / scale_w
    ny = (y - cy) / scale_h
    # Flame tip at (0, -1), base around (0, 0.8)
    if ny < -1.0 or ny > 0.9:
        return 999.0
    
    # Width profile along height
    # ny goes from -1.0 (top tip) to +0.8 (bottom)
    t = (ny + 1.0) / 1.8  # 0 at tip, 1 at base
    if t <= 0:
        return 999.0
    
    # Flame teardrop profile: w ~ sin(pi * t^0.7) * (1 - 0.2*sin(2*pi*t))
    w_profile = math.sin(math.pi * (t ** 0.65)) * 0.95
    # Bottom rounding
    if ny > 0.4:
        bottom_t = (ny - 0.4) / 0.5
        w_profile *= math.sqrt(max(0.0, 1.0 - bottom_t * bottom_t))
    
    dist_x = abs(nx) - w_profile
    return dist_x

def generate_fhir_icon():
    W, H = 256, 256
    
    def pixel_shader(x, y, w, h):
        # 1. Background Squircle
        bg_dist = inside_rounded_rect(x, y, w, h, 54, 54)
        if bg_dist > 1.5:
            return 0, 0, 0, 0  # Fully transparent
        
        bg_alpha = 1.0 - max(0.0, min(1.0, bg_dist + 0.5))
        
        # Background gradient: Dark slate
        t_bg = y / float(h)
        bg_r = int(32 * (1 - t_bg) + 18 * t_bg)
        bg_g = int(40 * (1 - t_bg) + 24 * t_bg)
        bg_b = int(52 * (1 - t_bg) + 32 * t_bg)
        
        # Border stroke
        if -2.5 < bg_dist <= 0.5:
            bg_r += 30
            bg_g += 35
            bg_b += 45

        # 2. Outer Flame
        cx, cy = 128.0, 142.0
        f_dist_outer = inside_flame(x, y, cx, cy, 76.0, 108.0)
        
        # Left flicker tongue
        f_left = inside_flame(x, y, 108.0, 150.0, 48.0, 75.0)
        # Right flicker tongue
        f_right = inside_flame(x, y, 148.0, 150.0, 48.0, 75.0)
        
        flame_outer_dist = min(f_dist_outer, f_left + 0.05, f_right + 0.05)
        
        # 3. Inner Flame
        flame_inner_dist = inside_flame(x, y, cx, cy + 12.0, 52.0, 78.0)
        
        # 4. Core Flame
        flame_core_dist = inside_flame(x, y, cx, cy + 22.0, 32.0, 50.0)

        # 5. Medical Cross in core
        in_cross = False
        if 132 <= y <= 188 and 120 <= x <= 136:  # Vertical bar
            in_cross = True
        if 152 <= y <= 168 and 100 <= x <= 156:  # Horizontal bar
            in_cross = True

        # Render layers
        if flame_outer_dist < 0.05:
            # Outer flame colors (Red -> Orange -> Gold)
            flame_t = (y - 35.0) / 180.0
            r = int(240 + 15 * flame_t)
            g = int(50 + 130 * flame_t)
            b = int(20 + 20 * flame_t)
            
            # Anti-aliasing outer edge
            if flame_outer_dist > -0.05:
                edge_a = (0.05 - flame_outer_dist) / 0.1
            else:
                edge_a = 1.0

            # Inner flame blend
            if flame_inner_dist < 0.0:
                inner_t = (y - 70.0) / 140.0
                r = int(255)
                g = int(160 + 80 * inner_t)
                b = int(30 + 80 * inner_t)
            
            # Core flame blend
            if flame_core_dist < 0.0:
                r, g, b = 255, 245, 210

            # Medical Cross
            if in_cross and flame_outer_dist < -0.15:
                r, g, b = 220, 38, 38  # Deep red cross in flame center

            # Blend flame over background
            final_r = int(r * edge_a + bg_r * (1 - edge_a))
            final_g = int(g * edge_a + bg_g * (1 - edge_a))
            final_b = int(b * edge_a + bg_b * (1 - edge_a))
            return final_r, final_g, final_b, int(bg_alpha * 255)

        return bg_r, bg_g, bg_b, int(bg_alpha * 255)

    png_bytes = create_png(W, H, pixel_shader)
    os.makedirs("assets", exist_ok=True)
    with open("assets/icon.png", "wb") as f:
        f.write(png_bytes)
    print("✅ assets/icon.png erfolgreich erstellt!")

    # Erstelle auch einfaches icon.ico für Windows
    create_ico_from_png("assets/icon.png", "assets/icon.ico", W, H, len(png_bytes))

def create_ico_from_png(png_path, ico_path, width, height, png_len):
    with open(png_path, "rb") as f:
        png_data = f.read()
    
    # ICO Header: Reserved (0), Type (1=Icon), Count (1)
    ico_header = struct.pack("<HHH", 0, 1, 1)
    # Icon Entry: Width (0 for 256), Height (0 for 256), Colors (0), Reserved (0), Planes (1), BPP (32), Size (bytes), Offset (22)
    w_byte = width if width < 256 else 0
    h_byte = height if height < 256 else 0
    ico_entry = struct.pack("<BBBBHHII", w_byte, h_byte, 0, 0, 1, 32, len(png_data), 22)
    
    with open(ico_path, "wb") as f:
        f.write(ico_header + ico_entry + png_data)
    print("✅ assets/icon.ico erfolgreich erstellt!")

if __name__ == "__main__":
    generate_fhir_icon()

