import streamlit as st
from utils import send_contact_email

def render_contact_page():
    """
    Renders the postcard contact inquiry page.
    """
    st.markdown("<h1 class='collections-header-title'>Postcard Inbox</h1>", unsafe_allow_html=True)
    st.markdown("<p class='collections-header-subtitle'>Let’s discuss shoots, bookings, or exhibition collaborations</p>", unsafe_allow_html=True)
    
    col_info, col_form = st.columns([1, 1.2])
    
    with col_info:
        st.markdown(
            """
            <div class="neo-card neo-card-full-height animate-slide-up">
                <h3>Contact Details</h3>
                <p class="contact-detail-item contact-detail-item-top">
                    📞 <b>Phone Number</b>:<br>
                    <span class="contact-detail-accent">+91 XXXXX XXXXX</span>
                </p>
                <p class="contact-detail-item">
                    📧 <b>Email Address</b>:<br>
                    <a href="mailto:vishalp30102004@gmail.com" class="contact-detail-link">
                        vishalp30102004@gmail.com
                    </a>
                </p>
                <p class="contact-detail-item">
                    📸 <b>Instagram</b>:<br>
                    <a href="https://www.instagram.com/the_travelling_lens_v/" target="_blank" class="contact-detail-link">
                        @the_travelling_lens_v
                    </a>
                </p>
                <p class="contact-detail-item contact-detail-item-last">
                    ✨ <b>Collaboration Availability</b>:<br>
                    Available for event assignments, portrait sessions, street walks, and private gallery proofings.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_form:
        st.markdown('<div class="postcard-container animate-slide-up">', unsafe_allow_html=True)
        st.markdown('<div class="postcard-stamp"></div>', unsafe_allow_html=True)
        st.markdown("<h3>Send a Booking Inquiry ✉️</h3>", unsafe_allow_html=True)
        
        with st.form("postcard_form", clear_on_submit=True):
            name = st.text_input("Name/Agency")
            email = st.text_input("Email Address")
            message = st.text_area("Write your message here...", height=120)
            
            submit = st.form_submit_button("📮 Send Message")
            if submit:
                if name and email and message:
                    success, status_msg = send_contact_email(name, email, message)
                    if success:
                        st.success(f"✉️ {status_msg}")
                    else:
                        st.warning(f"⚠️ {status_msg}")
                else:
                    st.warning("⚠️ Please fill in all the fields before sending!")
        st.markdown('</div>', unsafe_allow_html=True)
