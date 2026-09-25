import os
import numpy as np
from PIL import Image, ImageFilter
from collections import deque

BRAIN_DIR = r"C:\Users\saidur\.gemini\antigravity-ide\brain\f2fbad96-2dda-4e29-8c27-69b52e35189e"
STUDENT_JPG = os.path.join(BRAIN_DIR, "student_hero_isolated_1790324917773.jpg")
CHECK_JPG = os.path.join(BRAIN_DIR, "check_icon_3d_1790324935445.jpg")
GOOGLE_JPG = os.path.join(BRAIN_DIR, "google_icon_3d_1790324952786.jpg")
STATIC_IMG = r"c:\Users\saidur\Desktop\practice\django\static\images"

def extract_connected_background(img_path, out_path, color_thresh=25, blur_radius=1.5, bottom_fade=False):
    im = Image.open(img_path).convert('RGB')
    w, h = im.size
    arr = np.array(im, dtype=np.float32)
    
    # Calculate Euclidean distance from pure white (255, 255, 255)
    dist = np.sqrt(np.sum((255.0 - arr) ** 2, axis=2))
    
    # Background candidates: near white
    is_near_white = dist < color_thresh
    
    # Breadth-first search from all four borders
    visited = np.zeros((h, w), dtype=bool)
    q = deque()
    
    # Seed outer borders
    for x in range(w):
        if is_near_white[0, x]:
            visited[0, x] = True
            q.append((0, x))
        if is_near_white[h - 1, x]:
            visited[h - 1, x] = True
            q.append((h - 1, x))
            
    for y in range(h):
        if is_near_white[y, 0] and not visited[y, 0]:
            visited[y, 0] = True
            q.append((y, 0))
        if is_near_white[y, w - 1] and not visited[y, w - 1]:
            visited[y, w - 1] = True
            q.append((y, w - 1))
            
    while q:
        cy, cx = q.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                if is_near_white[ny, nx]:
                    visited[ny, nx] = True
                    q.append((ny, nx))
                    
    # Foreground mask: 255 for non-background, 0 for background
    fg_mask_arr = np.where(visited, 0, 255).astype(np.uint8)
    fg_mask = Image.fromarray(fg_mask_arr, mode='L')
    
    # Smooth edges with Gaussian blur for natural anti-aliasing
    if blur_radius > 0:
        fg_mask = fg_mask.filter(ImageFilter.GaussianBlur(blur_radius))
        
    # Convert mask to numpy to apply bottom fade if requested
    if bottom_fade:
        mask_np = np.array(fg_mask, dtype=np.float32)
        fade_start = int(h * 0.82)
        fade_len = h - fade_start
        for y in range(fade_start, h):
            factor = (h - y) / float(fade_len)
            mask_np[y, :] *= factor
        fg_mask = Image.fromarray(np.clip(mask_np, 0, 255).astype(np.uint8), mode='L')
        
    # Merge RGBA
    r, g, b = im.split()
    rgba = Image.merge('RGBA', (r, g, b, fg_mask))
    
    # Crop to non-empty bounding box with slight padding
    bbox = fg_mask.getbbox()
    if bbox:
        # keep bottom aligned for student
        if bottom_fade:
            crop_box = (max(0, bbox[0] - 10), max(0, bbox[1] - 10), min(w, bbox[2] + 10), h)
        else:
            crop_box = (max(0, bbox[0] - 10), max(0, bbox[1] - 10), min(w, bbox[2] + 10), min(h, bbox[3] + 10))
        rgba = rgba.crop(crop_box)
        
    rgba.save(out_path, 'PNG')
    print(f"Generated {out_path} ({rgba.size})")

def main():
    os.makedirs(STATIC_IMG, exist_ok=True)
    
    # 1. Student Layer
    extract_connected_background(
        STUDENT_JPG, 
        os.path.join(STATIC_IMG, "hero_layer_student.png"), 
        color_thresh=28, 
        blur_radius=1.2, 
        bottom_fade=True
    )
    
    # 2. Check Icon Layer (keep soft 3D shadow: thresh=15)
    extract_connected_background(
        CHECK_JPG, 
        os.path.join(STATIC_IMG, "hero_layer_check.png"), 
        color_thresh=18, 
        blur_radius=1.0, 
        bottom_fade=False
    )
    
    # 3. Google Icon Layer (keep soft 3D shadow: thresh=18)
    extract_connected_background(
        GOOGLE_JPG, 
        os.path.join(STATIC_IMG, "hero_layer_google.png"), 
        color_thresh=20, 
        blur_radius=1.0, 
        bottom_fade=False
    )

if __name__ == "__main__":
    main()
