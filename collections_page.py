import streamlit as st
import os
import base64
from utils import (
    get_optimized_image_path,
    get_original_image_bytes,
    get_image_exif,
    get_image_aspect_ratio
)

def render_collections_page(gallery_data):
    """
    Renders the paginated photography collections page in a responsive grid.
    """
    st.markdown("<h1 class='collections-header-title'>Photography Collections</h1>", unsafe_allow_html=True)
    st.markdown("<p class='collections-header-subtitle'>Exhibition portfolios and personal photography projects</p>", unsafe_allow_html=True)
    
    if not gallery_data:
        st.markdown(
            """
            <div class="neo-card empty-catalog-card">
                <h3>Exhibition Catalog is Empty! 📂</h3>
                <p class="empty-catalog-text">
                    Upload photos under <code>gallery/[category]/</code> subdirectories.
                    The app will automatically scan EXIF metadata and build your tabs!
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # Settings Toolbar
    st.markdown("<div class='neo-card neo-card-compact'>", unsafe_allow_html=True)
    col_g_c1, col_g_c2, col_g_c3 = st.columns([1.5, 1, 1])
    with col_g_c1:
        search_query = st.text_input("🔍 Live EXIF & Frame Search Engine", value="", placeholder="Type 'Sony', 'Canon', 'Concert', 'Street', 'f/1.8' to filter...")
    with col_g_c2:
        grid_cols_num = st.slider("Grid Columns Density", 2, 4, 3)
    with col_g_c3:
        show_exif = st.checkbox("Show Camera EXIF overlay", value=True)
        exp_per_page = st.selectbox("Exposures Per Page", [9, 12, 18, 24, 36], index=1)
    st.markdown("</div>", unsafe_allow_html=True)

    genres_mapping = {
        "All Works": "all",
        "Institute Events & Festivals": "festivals",
        "Portraits": "portraits",
        "Candids & Street Photography": "street",
        "Event Coverage": "events",
        "Landscapes / Personal Projects": "personal"
    }
    
    genres_tabs = list(genres_mapping.keys())
    tabs = st.tabs(genres_tabs)
    
    if "gallery_pages" not in st.session_state:
        st.session_state.gallery_pages = {}
    if "prev_search" not in st.session_state or st.session_state.prev_search != search_query:
        st.session_state.prev_search = search_query
        st.session_state.gallery_pages = {}
        
    def render_category_gallery(tab_idx, source_imgs, tab_key_name):
        filtered_imgs = []
        for img_path, img_genre in source_imgs:
            exif = get_image_exif(img_path)
            base_name = os.path.basename(img_path)
            caption = base_name.split(".")[0].replace("_", " ").title()
            
            exif_str = f"{exif['camera']} {exif['lens']} {exif['focal_length']} {exif['aperture']} {exif['shutter_speed']} {exif['iso']}"
            search_text = f"{base_name} {caption} {img_genre} {exif_str}".lower()
            
            if not search_query or search_query.lower() in search_text:
                filtered_imgs.append((img_path, img_genre, caption, exif))
        
        # Group by aspect ratio to keep similar shapes together, but shuffle group order stably per tab
        import random
        
        ratio_groups = {}
        for item in filtered_imgs:
            ratio = round(get_image_aspect_ratio(item[0]), 1)
            if ratio not in ratio_groups:
                ratio_groups[ratio] = []
            ratio_groups[ratio].append(item)
            
        stable_rng = random.Random(tab_key_name)
        ratios = list(ratio_groups.keys())
        stable_rng.shuffle(ratios)
        
        shuffled_imgs = []
        for r in ratios:
            shuffled_imgs.extend(ratio_groups[r])
        filtered_imgs = shuffled_imgs
                
        total_filtered = len(filtered_imgs)
        
        if total_filtered > 0:
            current_page = st.session_state.gallery_pages.get(tab_key_name, 0)
            
            total_pages = (total_filtered + exp_per_page - 1) // exp_per_page
            if current_page >= total_pages:
                current_page = 0
                st.session_state.gallery_pages[tab_key_name] = 0
                
            start_idx = current_page * exp_per_page
            end_idx = min(start_idx + exp_per_page, total_filtered)
            page_items = filtered_imgs[start_idx:end_idx]
            
            st.markdown(f"<p class='collections-counter-text'>Showing <b>{start_idx + 1} - {end_idx}</b> of <b>{total_filtered}</b> matching exposures:</p>", unsafe_allow_html=True)
            
            cols = st.columns(grid_cols_num)
            for idx, (img_path, img_genre, caption, exif) in enumerate(page_items):
                col_target = cols[idx % grid_cols_num]
                with col_target:
                    max_w_opt = 600 if grid_cols_num == 2 else 400
                    opt_path = get_optimized_image_path(img_path, max_width=max_w_opt)
                    if os.path.exists(opt_path):
                        with open(opt_path, "rb") as f:
                            img_b64 = base64.b64encode(f.read()).decode("utf-8")
                            
                        exif_line = f"{exif['camera']} | {exif['focal_length']} | {exif['aperture']} | {exif['shutter_speed']} | {exif['iso']}"
                        if not exif["has_exif"]:
                            exif_line = f"Manual Focus | 50mm | f/2.8 | {img_genre}"
                            
                        exif_overlay_html = f'<div class="exif-badge-overlay">{exif_line}</div>' if show_exif else ''
                        
                        st.markdown(f"""
                        <div class="exif-keepsake-frame exif-keepsake-frame-compact animate-slide-up">
                            <div class="relative-keepsake-wrapper">
                                <img src="data:image/jpeg;base64,{img_b64}" class="keepsake-img">
                                {exif_overlay_html}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        img_bytes = get_original_image_bytes(img_path)
                        if img_bytes:
                            st.download_button(
                                label="💾 Download Original negative",
                                data=img_bytes,
                                file_name=os.path.basename(img_path),
                                mime="image/jpeg",
                                key=f"dl_{tab_key_name}_{idx}_{os.path.basename(img_path)}"
                            )
                        st.markdown("<br>", unsafe_allow_html=True)
            
            if total_pages > 1:
                st.write("---")
                p_cols = st.columns(total_pages)
                for p_idx in range(total_pages):
                    with p_cols[p_idx]:
                        is_active = (p_idx == current_page)
                        btn_label = f"🎯 Page {p_idx + 1}" if is_active else f"Page {p_idx + 1}"
                        if st.button(btn_label, key=f"btn_{tab_key_name}_{p_idx}", use_container_width=True):
                            st.session_state.gallery_pages[tab_key_name] = p_idx
                            st.rerun()
        else:
            st.info("ℹ️ No exposures found matching your search filter.")

    # Render Tabs
    for t_idx, tab_name in enumerate(genres_tabs):
        with tabs[t_idx]:
            mapped_genre = genres_mapping[tab_name]
            if mapped_genre == "all":
                all_imgs = []
                for g_name, g_paths in gallery_data.items():
                    for p in g_paths:
                        all_imgs.append((p, g_name))
                render_category_gallery(t_idx, all_imgs, "tab_all")
            else:
                genre_imgs = [(p, tab_name) for p in gallery_data.get(tab_name, [])]
                render_category_gallery(t_idx, genre_imgs, f"tab_{mapped_genre}")
