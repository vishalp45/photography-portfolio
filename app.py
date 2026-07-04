import streamlit as st
import base64
import os
import json
from utils import (
    inject_custom_css, 
    get_optimized_image_path,
    scan_genre_gallery,
    THEMES
)
from collections_page import render_collections_page
from contacts_page import render_contact_page

# Page configuration
st.set_page_config(
    page_title="Vishal | Professional Photography Portfolio",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Color Preset helper
def load_preset_colors(theme_name):
    if theme_name in THEMES:
        preset = THEMES[theme_name]
        st.session_state.bg_color = preset["bg"]
        st.session_state.text_color = preset["text"]
        st.session_state.card_color = preset["card"]
        st.session_state.primary_color = preset["primary"]
        st.session_state.secondary_color = preset["secondary"]
        st.session_state.accent_color = preset["accent"]
        st.session_state.shadow_color = preset["shadow"]

# Initialize Session State
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "shutter_index" not in st.session_state:
    st.session_state.shutter_index = 0
if "flash_active" not in st.session_state:
    st.session_state.flash_active = False
if "audio_nav_active" not in st.session_state:
    st.session_state.audio_nav_active = False
if "theme" not in st.session_state:
    st.session_state.theme = "Leica Navy & Gold"
if "client_auth" not in st.session_state:
    st.session_state.client_auth = False
if "client_page" not in st.session_state:
    st.session_state.client_page = 0

# Pre-populate custom color states if not present
if "bg_color" not in st.session_state:
    load_preset_colors(st.session_state.theme)

# Initialize Viewfinder Filter states
if "vf_brightness" not in st.session_state:
    st.session_state.vf_brightness = 1.0
if "vf_contrast" not in st.session_state:
    st.session_state.vf_contrast = 1.0
if "vf_saturation" not in st.session_state:
    st.session_state.vf_saturation = 1.0
if "vf_blur" not in st.session_state:
    st.session_state.vf_blur = 0
if "vf_filter" not in st.session_state:
    st.session_state.vf_filter = "Normal"
if "vf_vignette" not in st.session_state:
    st.session_state.vf_vignette = False

# Sidebar Controls (The Camera Control Center)
with st.sidebar:
    st.markdown("<h2 style='font-family: Playfair Display, serif; margin-bottom: 5px; font-weight:700;'>⚙️ Custom Tuning</h2>", unsafe_allow_html=True)
    
    theme_options = list(THEMES.keys())
    theme_icons = {
        "Leica Navy & Gold": "🖤 Leica Navy & Gold",
        "Fujifilm Titanium": "🩶 Fujifilm Titanium",
        "Zeiss Obsidian": "💙 Zeiss Obsidian",
        "Sony Alpha": "🧡 Sony Alpha"
    }
    
    display_options = theme_options.copy()
    if st.session_state.theme == "Custom":
        display_options.append("Custom")
        theme_icons["Custom"] = "🎨 Custom Calibration"

    selected_preset = st.selectbox(
        "Chassis Trim Finish", 
        display_options, 
        index=display_options.index(st.session_state.theme),
        format_func=lambda x: theme_icons.get(x, x)
    )
    
    if selected_preset != st.session_state.theme and selected_preset != "Custom":
        st.session_state.theme = selected_preset
        load_preset_colors(selected_preset)
        st.rerun()

    # Individual Color Pickers Expander
    with st.expander("🎨 Custom Palette Tuning", expanded=False):
        st.write("Tune individual hex values:")
        bg_val = st.color_picker("Background Page", value=st.session_state.bg_color)
        text_val = st.color_picker("Text Elements", value=st.session_state.text_color)
        card_val = st.color_picker("Cards (Glass bg)", value=st.session_state.card_color)
        prim_val = st.color_picker("Primary Accent", value=st.session_state.primary_color)
        sec_val = st.color_picker("Secondary Details", value=st.session_state.secondary_color)
        acc_val = st.color_picker("Action Highlight", value=st.session_state.accent_color)
        shd_val = st.color_picker("Borders & Shadows", value=st.session_state.shadow_color)
        
        if (bg_val != st.session_state.bg_color or text_val != st.session_state.text_color or 
            card_val != st.session_state.card_color or prim_val != st.session_state.primary_color or 
            sec_val != st.session_state.secondary_color or acc_val != st.session_state.accent_color or 
            shd_val != st.session_state.shadow_color):
            
            st.session_state.bg_color = bg_val
            st.session_state.text_color = text_val
            st.session_state.card_color = card_val
            st.session_state.primary_color = prim_val
            st.session_state.secondary_color = sec_val
            st.session_state.accent_color = acc_val
            st.session_state.shadow_color = shd_val
            st.session_state.theme = "Custom"
            st.rerun()

    # Viewfinder Filters Panel (Available only on Home page)
    if st.session_state.page == "Home":
        st.markdown("---")
        st.markdown("<h3 style='font-family: Playfair Display, serif;'>🎛️ Digital Lens Filters</h3>", unsafe_allow_html=True)
        st.write("Adjust mirrorless camera parameters in the main viewfinder:")
        
        vf_filter = st.selectbox(
            "Film Simulation", 
            ["Normal", "B&W", "Sepia", "Negative", "Chrome"],
            index=["Normal", "B&W", "Sepia", "Negative", "Chrome"].index(st.session_state.vf_filter)
        )
        vf_brightness = st.slider("Aperture Exposure", 0.5, 2.0, st.session_state.vf_brightness, 0.1)
        vf_contrast = st.slider("Dynamic Contrast", 0.5, 2.0, st.session_state.vf_contrast, 0.1)
        vf_saturation = st.slider("Chroma Saturation", 0.0, 2.0, st.session_state.vf_saturation, 0.1)
        vf_blur = st.slider("Bokeh Blur (Defocus)", 0, 10, st.session_state.vf_blur, 1)
        vf_vignette = st.checkbox("Edge Vignette Falloff", value=st.session_state.vf_vignette)
        
        if (vf_filter != st.session_state.vf_filter or vf_brightness != st.session_state.vf_brightness or
            vf_contrast != st.session_state.vf_contrast or vf_saturation != st.session_state.vf_saturation or
            vf_blur != st.session_state.vf_blur or vf_vignette != st.session_state.vf_vignette):
            
            st.session_state.vf_filter = vf_filter
            st.session_state.vf_brightness = vf_brightness
            st.session_state.vf_contrast = vf_contrast
            st.session_state.vf_saturation = vf_saturation
            st.session_state.vf_blur = vf_blur
            st.session_state.vf_vignette = vf_vignette
            st.rerun()
            
    st.markdown("---")
    st.markdown("<h3 style='font-family: Playfair Display, serif; margin-bottom:5px;'>🔐 Private Proofing</h3>", unsafe_allow_html=True)
    st.write("Clients can enter passcodes under the **Client Room** tab to proof private shoots.")

# Build Active Colors Map
active_colors = {
    "bg": st.session_state.bg_color,
    "text": st.session_state.text_color,
    "card": st.session_state.card_color,
    "primary": st.session_state.primary_color,
    "secondary": st.session_state.secondary_color,
    "accent": st.session_state.accent_color,
    "shadow": st.session_state.shadow_color
}

# Inject Custom CSS styles
inject_custom_css(active_colors)

# Scan gallery subfolders
gallery_data = scan_genre_gallery()

# Populate viewfinder images
FEATURED_IMAGES = []
if gallery_data:
    for genre, paths in gallery_data.items():
        FEATURED_IMAGES.extend(paths[:3])
else:
    # Fallback default photos if gallery is empty
    FEATURED_IMAGES = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", img)
        for img in ["hero.JPG", "g1.jpg", "g2.jpg", "g3.jpg", "g4.JPG"]
        if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", img))
    ]

# Frame stories & descriptions for homepage slides
FRAME_STORIES = [
    {"title": "The Stage Presence", "desc": "Captured during the Inter-IIT Cultural Meet, freezing stage presence and stage lighting flares.", "specs": "Sony α7RIV | 70-200mm | f/2.8 | ISO 800 | 1/250s"},
    {"title": "The Delegate", "desc": "Candid capture at the Institute MUN conference, documenting collegiate delegation discussions.", "specs": "Sony α7IV | 85mm | f/1.8 | ISO 320 | 1/160s"},
    {"title": "Old Alleys Study", "desc": "Monochrome study highlighting shadows, brick geometry, and local street frames.", "specs": "Leica M11 | 35mm | f/2.0 | ISO 100 | 1/500s"},
    {"title": "The Portrait", "desc": "Detailed candid shot highlighting natural light separations at campus lawns.", "specs": "Sony α7RIV | 90mm Macro | f/4.0 | ISO 200 | 1/320s"}
]

# Flash & Navigation audio click triggers
if st.session_state.flash_active:
    st.markdown('<div class="flash-active"></div>', unsafe_allow_html=True)
    st.markdown('<audio src="https://www.soundjay.com/mechanical/camera-shutter-click-01.mp3" autoplay></audio>', unsafe_allow_html=True)
    st.session_state.flash_active = False

if st.session_state.audio_nav_active:
    st.markdown('<audio src="https://www.soundjay.com/button/button-16.mp3" autoplay></audio>', unsafe_allow_html=True)
    st.session_state.audio_nav_active = False

# Navigation Header (Clean, minimalist menu)
col_logo, col_nav = st.columns([1.1, 2])
with col_logo:
    st.markdown('<div class="nav-logo">VISHAL | <span>PHOTOGRAPHER</span></div>', unsafe_allow_html=True)
with col_nav:
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 Exhibition", use_container_width=True):
            st.session_state.page = "Home"
            st.session_state.audio_nav_active = True
            st.rerun()
    with c2:
        if st.button("🖼&nbsp; Collections", use_container_width=True):
            st.session_state.page = "Gallery"
            st.session_state.audio_nav_active = True
            st.rerun()
    with c3:
        if st.button("📮 Contact", use_container_width=True):
            st.session_state.page = "Contact"
            st.session_state.audio_nav_active = True
            st.rerun()

st.markdown("---")

# Render Page
if st.session_state.page == "Home":
    # ---------------------------------------------
    # HERO VIEWPORT & ABOUT BIOGRAPHY
    # ---------------------------------------------
    st.markdown(
        """
        <div class="brand-intro-container animate-fade-in">
            <h1 class="brand-intro-title">VISHAL</h1>
            <p class="brand-intro-subtitle">
                PHOTOGRAPHER
            </p>
            <p class="brand-intro-tagline">
                "Waking up at 4 AM, chasing the turquoise-blue wings of a kingfisher, and learning that the frame matters more than a broken ankle."
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_about_img, col_about_txt = st.columns([1, 1.8])
    with col_about_img:
        about_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "about.jpg")
        about_opt_path = get_optimized_image_path(about_img_path, max_width=600)
        if os.path.exists(about_opt_path):
            from PIL import Image
            st.image(Image.open(about_opt_path), use_container_width=True, caption="Vishal | Photographer")
    with col_about_txt:
        st.markdown(
            """
            <div class="neo-card neo-card-full-height animate-slide-up">
                <h3>👤 About Me</h3>
                <p>
                    My journey into photography began as a college curiosity and quickly became an obsession—the kind that makes you wake up at 4:00 AM to capture a kingfisher's blue wings, and teaches you that protecting your camera gear is more important than a broken ankle.
                </p>
                <p>
                    Serving as the <b>Official Institute Photographer</b> at IIT Bhubaneswar, I specialize in freezing high-energy festival stages, candid MUN debates, and street composition. My style prioritizes visual story narrative and organic details, focusing on real frames rather than staged setups.
                </p>
                <h4>Expertise Fields:</h4>
                <ul>
                    <li class="list-item-spacing"><b>Event & Concert Coverage</b>: stage lighting, movement capture, crowd dynamics.</li>
                    <li class="list-item-spacing"><b>Collegiate MUN Coverage</b>: documenting delegates, candid debates, and interactions.</li>
                    <li class="list-item-spacing"><b>Street & Portrait Photography</b>: capturing local brick framing, shadows, and expressions.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Narrative Quote Card
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="neo-card narrative-quote-card animate-slide-up">
            <h4 class="narrative-quote-title">📖 BEHIND THE SHUTTER: THE 4 AM MUSE</h4>
            <p class="narrative-quote-text">
                "One morning, while focusing on a kingfisher's eye, I fell and broke my ankle. Sitting on the asphalt in silence, my only regret was missing the opportunity to capture those beautiful, vibrant wings. That was the moment I realized photography was no longer just a hobby—it was something else."
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )



elif st.session_state.page == "Gallery":
    render_collections_page(gallery_data)





elif st.session_state.page == "Contact":
    render_contact_page()

# Footer
st.markdown(
    """
    <div class="footer-banner animate-fade-in">
        <p class="footer-banner-copyright">© 2026 Vishal. Built with ❤️ and Streamlit.</p>
        <p>
            <a href="https://www.instagram.com/the_travelling_lens_v/" target="_blank">Instagram</a> | 
            <a href="mailto:vishalp30102004@gmail.com">Email</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
