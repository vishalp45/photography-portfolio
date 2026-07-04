import os
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont, ExifTags
import io
import base64

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "gallery", "cache")
DESKTOP_PATH = r"C:\Users\visha\Desktop\sorted_pics"
if os.path.exists(DESKTOP_PATH):
    GALLERY_DIR = DESKTOP_PATH
else:
    GALLERY_DIR = os.path.join(BASE_DIR, "gallery")

os.makedirs(CACHE_DIR, exist_ok=True)

# Premium Professional Theme Presets (Navy & Gold guidelines)
THEMES = {
    "Leica Navy & Gold": {
        "bg": "#0B0F19",          # Matte Deep Navy/Charcoal
        "text": "#F8F9FA",        # Clean Off-White
        "card": "#161B2E",        # Translucent Dark Navy Glass
        "primary": "#D4A574",     # Warm Gold/Amber Accent
        "secondary": "#222943",   # Muted Slate Navy
        "accent": "#C9A961",      # Light Gold Highlight
        "shadow": "#0A0D15"
    },
    "Fujifilm Titanium": {
        "bg": "#1A1A1C",          # Matte Titanium gray
        "text": "#E5E5E5",
        "card": "#232325",
        "primary": "#C5A059",     # Metallic brass/gold accent
        "secondary": "#3E3E42",   # Silver-gray
        "accent": "#C5A059",
        "shadow": "#0F0F10"
    },
    "Zeiss Obsidian": {
        "bg": "#07090C",          # Dark obsidian blue-black
        "text": "#E2E8F0",
        "card": "#12161C",
        "primary": "#007AFF",     # Zeiss cobalt blue
        "secondary": "#242F3D",   # Dark steel slate
        "accent": "#007AFF",
        "shadow": "#030406"
    },
    "Sony Alpha": {
        "bg": "#0E0E0F",          # Matte black
        "text": "#F5F5F7",
        "card": "#1C1C1E",
        "primary": "#FF5A00",     # Sony Alpha copper-orange
        "secondary": "#36363A",   # Matte body gray
        "accent": "#FF5A00",
        "shadow": "#050505"
    }
}

def hex_to_rgba(hex_str, alpha=0.6):
    """
    Converts hex color string to rgba for translucent CSS styling (e.g. selections/blur overlays).
    """
    hex_str = hex_str.lstrip('#')
    try:
        if len(hex_str) == 3:
            hex_str = "".join([c*2 for c in hex_str])
        r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r}, {g}, {b}, {alpha})"
    except Exception:
        return f"rgba(100, 100, 100, {alpha})"

@st.cache_data(show_spinner=False)
def get_optimized_image_path(image_path_or_name, max_width=1000):
    """
    Optimizes a high-resolution image by resizing it and saving it to the cache directory.
    """
    if os.path.isabs(image_path_or_name):
        full_path = image_path_or_name
        image_name = os.path.basename(image_path_or_name)
    else:
        full_path = os.path.join(BASE_DIR, "gallery", image_path_or_name)
        image_name = image_path_or_name

    if not os.path.exists(full_path):
        return full_path

    # Clean filename for cache
    cache_name = f"opt_{max_width}_{image_name.replace(os.sep, '_')}"
    cached_path = os.path.join(CACHE_DIR, cache_name)

    if os.path.exists(cached_path):
        return cached_path

    try:
        with Image.open(full_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            width, height = img.size
            if width > max_width:
                ratio = max_width / width
                new_size = (max_width, int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            img.save(cached_path, "JPEG", quality=80, optimize=True)
            return cached_path
    except Exception as e:
        print(f"Error optimizing image {image_name}: {e}")
        return full_path

def get_original_image_bytes(image_path):
    """
    Reads original image bytes from an absolute path.
    """
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return f.read()
    return b""

# Cached EXIF Metadata Extraction function
@st.cache_data(show_spinner=False)
def get_image_exif(image_path):
    """
    Extracts camera model, lens, aperture, shutter speed, and ISO directly from file EXIF tags.
    """
    exif_data = {
        "camera": "Unknown Camera",
        "lens": "Unknown Lens",
        "focal_length": "N/A",
        "aperture": "N/A",
        "shutter_speed": "N/A",
        "iso": "N/A",
        "has_exif": False
    }
    
    if not os.path.exists(image_path):
        return exif_data
        
    try:
        with Image.open(image_path) as img:
            info = img._getexif()
            if not info:
                return exif_data
                
            raw_exif = {}
            for tag, value in info.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                raw_exif[decoded] = value
            
            exif_data["has_exif"] = True
            
            # Extract Camera Model
            if "Model" in raw_exif:
                exif_data["camera"] = str(raw_exif["Model"]).strip()
            elif "Make" in raw_exif:
                exif_data["camera"] = str(raw_exif["Make"]).strip()
                
            # Lens Info
            if "LensModel" in raw_exif:
                exif_data["lens"] = str(raw_exif["LensModel"]).strip()
            
            # Aperture (FNumber)
            if "FNumber" in raw_exif:
                val = raw_exif["FNumber"]
                try:
                    f_val = float(val[0]) / float(val[1]) if isinstance(val, tuple) else float(val)
                    exif_data["aperture"] = f"f/{f_val:.1f}" if f_val.is_integer() else f"f/{f_val:.2f}"
                except:
                    exif_data["aperture"] = f"f/{val}"

            # Shutter Speed (ExposureTime)
            if "ExposureTime" in raw_exif:
                val = raw_exif["ExposureTime"]
                try:
                    if isinstance(val, tuple):
                        num, den = val[0], val[1]
                        if num == 1:
                            exif_data["shutter_speed"] = f"1/{den}s"
                        elif num > 1:
                            exif_data["shutter_speed"] = f"{num/den:.1f}s"
                        else:
                            exif_data["shutter_speed"] = f"1/{int(den/num)}s"
                    else:
                        exp = float(val)
                        if exp < 1.0:
                            exif_data["shutter_speed"] = f"1/{int(1.0/exp)}s"
                        else:
                            exif_data["shutter_speed"] = f"{exp:.1f}s"
                except:
                    exif_data["shutter_speed"] = f"{val}s"

            # ISO Rating
            if "ISOSpeedRatings" in raw_exif:
                exif_data["iso"] = f"ISO {raw_exif['ISOSpeedRatings']}"
            elif "PhotographicSensitivity" in raw_exif:
                exif_data["iso"] = f"ISO {raw_exif['PhotographicSensitivity']}"

            # Focal Length
            if "FocalLength" in raw_exif:
                val = raw_exif["FocalLength"]
                try:
                    f_len = float(val[0]) / float(val[1]) if isinstance(val, tuple) else float(val)
                    exif_data["focal_length"] = f"{int(f_len)}mm"
                except:
                    exif_data["focal_length"] = f"{val}mm"
                    
    except Exception as e:
        print(f"Error reading EXIF for {image_path}: {e}")
        
    return exif_data

@st.cache_data(show_spinner=False)
def get_image_aspect_ratio(image_path):
    """
    Returns the width/height aspect ratio. Caches output for speed.
    """
    if not os.path.exists(image_path):
        return 1.0
    try:
        with Image.open(image_path) as img:
            w, h = img.size
            return float(w) / float(h)
    except:
        return 1.0

# Dynamic Classifier for DSLR and Phone Photos
def classify_image_genre(image_path):
    """
    Dynamically classifies a file into one of the 5 portfolio categories
    based on filename keywords and cached EXIF metadata.
    """
    filename = os.path.basename(image_path).lower()
    exif = get_image_exif(image_path)
    
    # Check filename keywords first
    if "street" in filename or "urban" in filename or "chaos" in filename or "alley" in filename:
        return "Candids & Street Photography"
    if "bts" in filename or "behind" in filename or "coverage" in filename:
        return "Event Coverage"
    if "portrait" in filename or "face" in filename:
        return "Portraits"
    if "landscape" in filename or "nature" in filename or "sky" in filename or "moon" in filename or "complementary" in filename or "lizard" in filename or "bird" in filename:
        return "Landscapes / Personal Projects"
    if "fest" in filename or "event" in filename or "meet" in filename:
        return "Institute Events & Festivals"
        
    # Check EXIF attributes
    if exif["has_exif"]:
        fl = exif["focal_length"].replace("mm", "")
        ap = exif["aperture"].replace("f/", "")
        try:
            fl_val = float(fl)
            ap_val = float(ap)
            
            # Portrait lenses: 85mm, 50mm, 105mm at wide apertures
            if fl_val in [50, 85, 105, 135] or (50 <= fl_val <= 135 and ap_val <= 2.2):
                return "Portraits"
            
            # Street/Candid lenses: 28mm, 35mm, 50mm
            if fl_val in [28, 35] or (28 <= fl_val <= 50 and ap_val >= 2.8 and ap_val <= 5.6):
                return "Candids & Street Photography"
                
            # Landscape: wide angles <= 24mm or narrow apertures >= f/5.6
            if fl_val <= 24 or ap_val >= 8.0:
                return "Landscapes / Personal Projects"
                
            # Events/Concert: zoom lens 70-200mm
            if 70 <= fl_val <= 200:
                return "Event Coverage"
        except:
            pass
            
    # Fallbacks based on typical camera filename series
    if filename.startswith("0b4a") or filename.startswith("0q3a"):
        return "Event Coverage"
    if filename.startswith("dsc_"):
        # Split Nikon/Sony files between street, landscape, and portraits
        hash_val = sum(ord(c) for c in filename)
        if hash_val % 3 == 0:
            return "Candids & Street Photography"
        elif hash_val % 3 == 1:
            return "Landscapes / Personal Projects"
        else:
            return "Portraits"
            
    # General Default fallback
    return "Institute Events & Festivals"

# Direct scan Desktop folder
def scan_genre_gallery():
    """
    Scans the C:/Users/visha/Desktop/sorted_pics directory directly (or the local gallery/ directory).
    Dynamically classifies each photo file into one of the 5 portfolio categories
    and returns a dictionary of {category_name: [list_of_image_paths]}.
    """
    gallery_data = {
        "Institute Events & Festivals": [],
        "Portraits": [],
        "Candids & Street Photography": [],
        "Event Coverage": [],
        "Landscapes / Personal Projects": []
    }
    
    if not os.path.exists(GALLERY_DIR):
        return {}
        
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.jpg', '.JPG', '.PNG', '.JPEG')
    
    files_paths = []
    for root, dirs, files in os.walk(GALLERY_DIR):
        if "cache" in dirs:
            dirs.remove("cache")
        for file in files:
            if file.lower() == "about.jpg":
                continue
            if file.lower().endswith(valid_extensions):
                files_paths.append(os.path.join(root, file))
                
    files_paths.sort()
    
    for full_path in files_paths:
        # Classify dynamically
        genre = classify_image_genre(full_path)
        if genre in gallery_data:
            gallery_data[genre].append(full_path)
                
    # Filter out empty categories
    return {k: v for k, v in gallery_data.items() if v}

# Darkroom Image Filter Processing Function
def apply_darkroom_filters(image_source, brightness, contrast, saturation, blur_radius, filter_type):
    """
    Applies image enhancements and filters dynamically using PIL.
    """
    try:
        if isinstance(image_source, bytes):
            img = Image.open(io.BytesIO(image_source))
        else:
            if not os.path.exists(image_source):
                return b""
            img = Image.open(image_source)

        width, height = img.size
        if width > 800:
            ratio = 800 / width
            img = img.resize((800, int(height * ratio)), Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        if filter_type == "B&W":
            img = img.convert("L").convert("RGB")
        elif filter_type == "Sepia":
            gray = img.convert("L")
            img = ImageOps.colorize(gray, "#3B2314", "#F8ECC2")
        elif filter_type == "Negative":
            img = ImageOps.invert(img)
        elif filter_type == "Chrome":
            r, g, b = img.split()
            r = r.point(lambda i: i * 0.85)
            b = b.point(lambda i: min(int(i * 1.15), 255))
            img = Image.merge("RGB", (r, g, b))

        if brightness != 1.0:
            enh = ImageEnhance.Brightness(img)
            img = enh.enhance(brightness)
            
        if contrast != 1.0:
            enh = ImageEnhance.Contrast(img)
            img = enh.enhance(contrast)
            
        if saturation != 1.0 and filter_type != "B&W" and filter_type != "Sepia":
            enh = ImageEnhance.Color(img)
            img = enh.enhance(saturation)

        if blur_radius > 0:
            img = img.filter(ImageFilter.GaussianBlur(blur_radius))

        out_buffer = io.BytesIO()
        img.save(out_buffer, format="JPEG", quality=80)
        return out_buffer.getvalue()
    except Exception as e:
        print(f"Error applying filters: {e}")
        return b""

# Branded DSLR EXIF Keepsake Card Compiler
def create_polaroid_card(img_bytes, caption_text, brightness, contrast, saturation, blur_radius, filter_type):
    """
    Compiles webcam capture into a professional DSLR EXIF print card with signature text.
    """
    proc_bytes = apply_darkroom_filters(img_bytes, brightness, contrast, saturation, blur_radius, filter_type)
    if not proc_bytes:
        return b""
        
    try:
        photo = Image.open(io.BytesIO(proc_bytes))
        photo = photo.resize((540, 400), Image.Resampling.LANCZOS)
        
        # Create dark premium canvas mount (600, 600)
        canvas = Image.new("RGB", (600, 600), "#0B0F19")
        canvas.paste(photo, (30, 30))
        
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([28, 28, 572, 432], outline="#2D3748", width=2)
        draw.rectangle([2, 2, 597, 597], outline="#D4A574", width=2) # Gold frame border
        
        text_y_brand = 460
        text_y_exif = 510
        
        font_main = None
        font_sub = None
        # Try loading Windows system fonts
        for font_path in [r"C:\Windows\Fonts\Arial.ttf", r"C:\Windows\Fonts\consola.ttf"]:
            if os.path.exists(font_path):
                try:
                    font_main = ImageFont.truetype(font_path, 22)
                    font_sub = ImageFont.truetype(font_path, 16)
                    break
                except:
                    pass
        
        if not font_main:
            font_main = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            
        # Draw Signature line
        sign_text = "VISHAL PRAJAPATI PHOTOGRAPHY"
        try:
            w_sign = draw.textlength(sign_text, font=font_main)
        except:
            w_sign = len(sign_text) * 10
        draw.text(((600 - w_sign)//2, text_y_brand), sign_text, fill="#D4A574", font=font_main)
        
        # Draw Exif mock variables
        exif_text = f"ISO 200 | f/2.8 | 50mm | 1/250s | {caption_text}"
        try:
            w_exif = draw.textlength(exif_text, font=font_sub)
        except:
            w_exif = len(exif_text) * 8
        draw.text(((600 - w_exif)//2, text_y_exif), exif_text, fill="#A1A1AA", font=font_sub)
        
        out_buf = io.BytesIO()
        canvas.save(out_buf, format="JPEG", quality=90)
        return out_buf.getvalue()
    except Exception as e:
        print(f"Error creating branded EXIF keepsake: {e}")
        return b""

def inject_custom_css(colors):
    """
    Injects custom CSS based on the cinematic DSLR color theme and layout.
    """
    selection_color = hex_to_rgba(colors['primary'], 0.25)
    card_rgba = hex_to_rgba(colors['card'], 0.75)
    
    # CSS variables
    css_vars = f"""
    :root {{
        --bg-color: {colors['bg']};
        --text-color: {colors['text']};
        --card-bg: {card_rgba};
        --primary-color: {colors['primary']};
        --secondary-color: {colors['secondary']};
        --accent-color: {colors['accent']};
        --shadow-color: {colors['shadow']};
        --selection-color: {selection_color};
    }}
    """

    st.markdown(f"<style>{css_vars}</style>", unsafe_allow_html=True)

    # Read external style.css
    css_file_path = os.path.join(BASE_DIR, "style.css")
    if os.path.exists(css_file_path):
        try:
            with open(css_file_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading external style.css: {e}")

def send_contact_email(name, visitor_email, message_body):
    """
    Sends an email notification via SMTP if environment variables are configured.
    Otherwise, logs to a local file.
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")       # e.g. vishalp30102004@gmail.com
    smtp_password = os.environ.get("SMTP_PASSWORD") # App Password
    recipient_email = os.environ.get("RECIPIENT_EMAIL", "vishalp30102004@gmail.com")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(base_dir, "messages.txt")
    
    # 1. Log locally
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"Sender Name: {name}\nSender Email: {visitor_email}\nMessage:\n{message_body}\n{'='*40}\n")
        logged = True
    except Exception as e:
        print(f"Failed to log message locally: {e}")
        logged = False
        
    # 2. Try SMTP
    if smtp_user and smtp_password:
        try:
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = recipient_email
            msg["Subject"] = f"📸 New Portfolio Inquiry from {name}"
            
            email_content = f"""
            Hello Vishal,
            
            You have received a new inquiry from your photography portfolio website:
            
            ------------------------------------------------
            Name: {name}
            Email: {visitor_email}
            
            Message:
            {message_body}
            ------------------------------------------------
            
            This is an automated notification from your Azure Web App.
            """
            msg.attach(MIMEText(email_content, "plain"))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient_email, msg.as_string())
            server.quit()
            return True, "Email notification sent & message logged locally."
        except Exception as e:
            return False, f"Logged locally, but failed to send email: {e}"
    else:
        return True, "Logged locally to messages.txt (Configure SMTP in Azure App Settings for email alerts)."
