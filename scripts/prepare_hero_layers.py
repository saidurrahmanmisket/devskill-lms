import os
import sys
from PIL import Image

BRAIN_DIR = r"C:\Users\saidur\.gemini\antigravity-ide\brain\f2fbad96-2dda-4e29-8c27-69b52e35189e"
STUDENT_JPG = os.path.join(BRAIN_DIR, "student_hero_isolated_1790324917773.jpg")
CHECK_JPG = os.path.join(BRAIN_DIR, "check_icon_3d_1790324935445.jpg")
GOOGLE_JPG = os.path.join(BRAIN_DIR, "google_icon_3d_1790324952786.jpg")
OUTPUT_DIR = r"c:\Users\saidur\Desktop\practice\django\static\images"

def remove_bg(input_path, output_path, bottom_fade=False):
    from rembg import remove
    print(f"Removing background from {input_path}...")
    with open(input_path, 'rb') as i:
        input_data = i.read()
        output_data = remove(input_data)
        
    with open(output_path, 'wb') as o:
        o.write(output_data)
        
    if bottom_fade:
        # Apply smooth bottom gradient alpha fade to student so he blends naturally
        im = Image.open(output_path).convert("RGBA")
        w, h = im.size
        r, g, b, a = im.split()
        fade_start = int(h * 0.82)
        fade_len = h - fade_start
        alpha_bytes = bytearray(a.tobytes())
        for y in range(fade_start, h):
            factor = (h - y) / float(fade_len)
            for x in range(w):
                idx = y * w + x
                alpha_bytes[idx] = int(alpha_bytes[idx] * factor)
        a_faded = Image.frombytes("L", (w, h), bytes(alpha_bytes))
        im_faded = Image.merge("RGBA", (r, g, b, a_faded))
        im_faded.save(output_path, "PNG")
        print(f"Saved with bottom fade: {output_path}")
    else:
        print(f"Saved: {output_path}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Student layer
    student_out = os.path.join(OUTPUT_DIR, "hero_layer_student.png")
    remove_bg(STUDENT_JPG, student_out, bottom_fade=True)
    
    # 2. Check icon layer
    check_out = os.path.join(OUTPUT_DIR, "hero_layer_check.png")
    remove_bg(CHECK_JPG, check_out, bottom_fade=False)
    
    # 3. Google icon layer
    google_out = os.path.join(OUTPUT_DIR, "hero_layer_google.png")
    remove_bg(GOOGLE_JPG, google_out, bottom_fade=False)

    print("All layers prepared successfully!")

if __name__ == "__main__":
    main()
