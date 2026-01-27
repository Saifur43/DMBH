from PIL import Image
from collections import Counter

def get_dominant_color(image_path):
    try:
        img = Image.open(image_path)
        img = img.resize((50, 50))  # Resize for speed
        img = img.convert("RGB")
        pixels = list(img.getdata())
        # Filter out white/near-white/black pixels to find the "brand" color
        filtered_pixels = [
            p for p in pixels 
            if not (p[0] > 240 and p[1] > 240 and p[2] > 240) and # Not white
               not (p[0] < 20 and p[1] < 20 and p[2] < 20)        # Not black
        ]
        
        if not filtered_pixels:
            return "No distinct color found"
            
        counts = Counter(filtered_pixels)
        return counts.most_common(5)
    except Exception as e:
        return str(e)

print(get_dominant_color("dm logo.jpeg"))
