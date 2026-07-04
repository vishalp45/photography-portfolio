# 📸 Vishal's Photography Portfolio

A sophisticated, minimalist, and responsive photography portfolio website built with Python and Streamlit. Designed to attract clients, exhibition opportunities, and creative collaborations.

## ✨ Features

* **Minimalist & Distraction-Free Layout**: A premium aesthetic utilizing a curated color palette (Deep Navy backdrop, Gold accents) to let the photographs dominate.
* **Responsive Masonry Gallery Grid**: Dynamically displays and clusters shots ratio-wise to maintain clean grid rows across screen sizes.
* **Stable Randomized Ordering**: Groups photos by shape but shuffles group order stably per category tab so vertical vs. horizontal shots get equal prominence without causing layout jumps.
* **Automated EXIF Metadata Extraction**: Automatically parses aperture, shutter speed, ISO, lens, and camera details from image uploads.
* **Cache Image Optimization**: Dynamically compresses and caches optimized image variations to speed up page loads and performance.
* **Hybrid Deployment Paths**: Seamless transition between reading local Desktop folders during development and relative project directories in production.
* **SMTP Inquiry Inbox**: Interactive contact page that logs messages locally to `messages.txt` and dispatches email notifications to your inbox.
* **Modular Codebase**: Clean, separated architecture (`app.py`, `utils.py`, `collections_page.py`, `contacts_page.py`, and `style.css`).

---

## 🛠️ Local Installation & Running

1. **Clone the repository**:
   ```bash
   git clone <your-repository-url>
   cd pf_site
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit server**:
   ```bash
   streamlit run app.py
   ```

---

## 🚀 Cloud Deployment

### 1. Azure App Service (Recommended)
1. **Push your code to GitHub** (including `requirements.txt` and the `gallery/` subdirectory with your select photographs).
2. **Create a Linux Python Web App** on the Azure Portal (using runtime stack **Python 3.10** or **3.11**).
3. Under **Settings > Configuration > General settings**, configure the **Startup Command** as:
   ```bash
   python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0
   ```
4. Under **Application settings**, add a new setting `WEBSITES_PORT` with value `8000`.
5. Connect deployment from your GitHub repository under the **Deployment Center** tab.

### 2. Streamlit Community Cloud
1. Link your GitHub account at [share.streamlit.io](https://share.streamlit.io/).
2. Select your repository, set the entrypoint file to `app.py`, and click **Deploy**.

---

## 📬 Contact Form SMTP Environment Configuration
To enable direct email notifications on form submissions, configure these environment variables in your Azure App Service Application settings:
* `SMTP_SERVER`: (Default: `smtp.gmail.com`)
* `SMTP_PORT`: (Default: `587`)
* `SMTP_USER`: Your email address
* `SMTP_PASSWORD`: Your email app password (use a Gmail App Password)
* `RECIPIENT_EMAIL`: The inbox where you want to receive booking inquiries
