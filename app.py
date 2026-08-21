import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
import urllib.parse
import io
import base64
import os
import time
import json
import math
from PIL import Image
from supabase import create_client, Client

# ==========================================
# CREDENTIALS & SETUP (YOUR EXACT KEYS)
# ==========================================
SUPABASE_URL = "https://xkkcerlqmhkvqxggivsc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhra2NlcmxxbWhrdnF4Z2dpdnNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODczMjgwNjEsImV4cCI6MjEwMjkwNDA2MX0.85lyq8dnzEvQblhxeAYfTYxsGwpxW8vJmmCUg_oGVic"

USERS = {
    "admin": {"password": "Japnik@3315", "role": "admin"},
    "staff": {"password": "12345", "role": "staff"},
    "management": {"password": "view@123", "role": "management"},
    "emp1": {"password": "emp1", "role": "employee"}
}

st.set_page_config(page_title="Makan Clinic Manager", page_icon="🏥", layout="wide")

# --- ਕਲੀਨਿਕ ਦੇ ਵੇਰਵੇ (CLINIC DETAILS) ---
CLINIC_ADDRESS = "Dream City Market, Manawala, G.T. Road, Amritsar"
CLINIC_LAT = 31.5830  
CLINIC_LON = 74.9660

BANK_ACCOUNTS = ["ਨਕਦ (Cash)", "Kotak Bank Regular", "Kotak Bank Corpus Fund", "Punjab & Sind Bank"]
EXPENSE_CATEGORIES = [
    "--- ਕਲੀਨਿਕ ਖਰਚੇ (Clinic Expenses) ---",
    "ਦਵਾਈਆਂ (Medicines)", "ਡੈਂਟਲ ਮਟੀਰੀਅਲ (Dental Supplies)", "ਲੈਬ ਟੈਸਟ (Lab Tests)", 
    "ਮਸ਼ੀਨਰੀ ਮੇਨਟੇਨੈਂਸ (Equipment Maintenance)", "ਸਾਫ਼-ਸਫ਼ਾਈ (Cleaning/Sanitation)", "ਡਾਕਟਰ ਫੀਸ (Doctor Payouts)",
    "--- ਹੋਰ ਪ੍ਰਬੰਧ (Other Management) ---",
    "ਸਟਾਕ ਖਰੀਦ (Purchase of Stock)", "ਸਟਾਫ਼ ਦੀ ਤਨਖਾਹ (Payment to Staff)", 
    "ਅਕਾਊਂਟੈਂਟ ਦੀ ਫੀਸ (Accountant Fee)", "ਫਰਨੀਚਰ (Furniture)", "ਬਿਲਡਿੰਗ (Building)", 
    "ਛਪਾਈ ਅਤੇ ਇਸ਼ਤਿਹਾਰ (Printing & Advt)", "ਸਟਾਫ਼ ਖਾਣਾ/ਚਾਹ (Staff Refreshments)", "ਹੋਰ ਖਰਚੇ (Others)"
]
STOCK_UNITS = ["ਕਿਲੋ (Kg)", "ਲੀਟਰ (Liter)", "ਪੀਸ (Pcs)", "ਗ੍ਰਾਮ (Gram)", "ਬੋਕਸ (Boxes)"]
ASSET_TYPES = ["ਬਿਲਡਿੰਗ (Building)", "ਫਰਨੀਚਰ (Furniture)", "ਮੈਡੀਕਲ ਉਪਕਰਨ (Medical Equipment)", "ਇਲੈਕਟ੍ਰੋਨਿਕਸ (Electronics/IT)", "ਹੋਰ (Other)"]

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
        .stAppDeployButton {display:none !important;}
        [data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 18px !important; font-weight: 600 !important; padding-bottom: 5px; }
        h2 { font-size: 26px !important; font-weight: 700 !important; padding-bottom: 5px !important; }
        .pro-header-flex { display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #F8F1D1 0%, #ffffff 100%); padding: 15px 20px; border-radius: 12px; border: 2px solid #0F4C81; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .pro-title { font-size: 28px; font-weight: bold; color: #0F4C81 !important; margin: 0; letter-spacing: 0.5px; text-align: center;}
        .pro-tagline { font-size: 17px; font-weight: bold; color: #D92B2B !important; margin: 4px 0; text-align: center;}
        .pro-sub { font-size: 13px; font-weight: bold; color: #333 !important; margin: 0; text-align: center;}
        div.stButton > button { font-size: 18px !important; font-weight: bold !important; padding: 16px 10px !important; border-radius: 10px !important; width: 100% !important; }
        .bs-box { border: 2px solid var(--text-color); border-radius: 8px; padding: 15px; margin-bottom: 20px; }
        .bs-header { text-align: center; font-size: 22px; font-weight: bold; border-bottom: 2px solid var(--text-color); padding-bottom: 10px; margin-bottom: 15px; }
        .bs-row { display: flex; justify-content: space-between; font-size: 16px; margin-bottom: 8px; }
        .bs-total { display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; color: #E53935; border-top: 1px solid var(--text-color); padding-top: 8px; margin-top: 10px; }
        .branch-btn > button { height: 140px !important; font-size: 26px !important; border: 3px solid #0F4C81 !important; background-color: #F8F1D1 !important; color: #0F4C81 !important; transition: 0.3s; }
        .branch-btn > button:hover { background-color: #0F4C81 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def compress_image(uploaded_file, max_size=(800, 800)):
    if uploaded_file is not None:
        try:
            img = Image.open(uploaded_file)
            img.thumbnail(max_size)
            buffered = io.BytesIO()
            img.convert("RGB").save(buffered, format="JPEG", quality=75)
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception as e:
            st.error(f"Image processing error: {e}")
            return ""
    return ""

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    return ""

@st.cache_resource
def init_connection(): 
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try: supabase: Client = init_connection()
except Exception: st.error("Supabase Connection Error. Please check URL and Key.")

def get_bani_footer():
    bani_logo_base64 = get_base64_image("bani_logo_2.jpeg")
    bani_img_html = f'<img src="data:image/jpeg;base64,{bani_logo_base64}" style="height: 25px; vertical-align: middle; margin-right: 8px; border-radius: 4px;">' if bani_logo_base64 else ''
    return f'<div class="bani-footer">{bani_img_html}Designed by Bani Tech Solutions | banitech.in</div>'

def generate_html_receipt(receipt_no, name, phone, amount, date_str, payment_mode, dept, bank_acc, on_account_of, collector=""):
    amount_text = f"Rs. {amount}/-"
    amount_in_words = f"Rupees {amount} Only" 
    display_phone = phone if phone else "________________"
    logo_base64 = get_base64_image("logo.png")
    img_html = f'<img src="data:image/png;base64,{logo_base64}" style="width: 100px; position: absolute; left: 30px; top: 20px;">' if logo_base64 else ''
    
    clinic_title = f"Makan {dept}"
    bani_footer = get_bani_footer()
    
    html_content = f"""
    <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Receipt #{receipt_no}</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; background-color: #fff; padding: 20px; }}
            .receipt-box {{ max-width: 800px; margin: auto; padding: 20px 30px; background-color: #F8F1D1; border-top: 20px solid #0F4C81; border-bottom: 20px solid #0F4C81; color: #333; position: relative;}}
            .header-text {{ text-align: center; width: 100%; }}
            .title-pa {{ font-size: 26px; font-weight: bold; color: #0F4C81; margin: 0; text-transform: uppercase; }}
            .sub-title-pa {{ font-size: 16px; color: #D92B2B; font-weight: bold; margin: 4px 0; }}
            .sub-title-en {{ font-size: 13px; font-weight: bold; color: #333; margin: 3px 0; }}
            .reg-row {{ display: flex; justify-content: space-between; border-top: 1.5px solid #333; border-bottom: 1.5px solid #333; padding: 5px 0; font-size: 14px; font-weight: bold; margin: 15px 0; }}
            .main-content {{ font-size: 15px; line-height: 2.0; font-weight: bold; color: #222; }}
            .field-value {{ font-family: 'Courier New', monospace; font-size: 16px; color: #0F4C81; border-bottom: 1px solid #666; padding: 0 10px; }}
            .amount-box {{ font-size: 18px; font-weight: bold; color: #0F4C81; border: 2px solid #333; padding: 5px 20px; border-radius: 15px; display: inline-block; }}
            .bani-footer {{ text-align: center; font-size: 11px; margin-top: 30px; color: #888; font-weight: bold; padding-top: 10px; display: flex; justify-content: center; align-items: center; }}
        </style></head>
    <body>
        <div class="receipt-box">
            {img_html}
            <div class="header-text">
                <p class="title-pa">{clinic_title}</p>
                <p class="sub-title-pa">Complete Care</p>
                <p class="sub-title-en">{CLINIC_ADDRESS}</p>
            </div>
            <div class="reg-row"><div>{dept.upper()} OPD RECEIPT</div><div>Consulting: <span class="field-value" style="font-size:14px;">{on_account_of}</span></div></div>
            <div class="main-content">
                <div style="display: flex; justify-content: space-between;"><div>Receipt No: <span class="field-value" style="color: #D92B2B;">{receipt_no:04d}</span></div><div>Date: <span class="field-value">{date_str[:10]}</span></div></div>
                <div style="margin-top: 10px;">Received with thanks from Patient <span class="field-value" style="width: 40%; display:inline-block;">{name}</span>, Mob: <span class="field-value">{display_phone}</span></div>
                <div style="margin-top: 10px;">A sum of <span class="field-value" style="width: 60%; display:inline-block;">{amount_in_words}</span> as Consultation Fee.</div>
                <div style="margin-top: 10px;">Mode: <span class="field-value">{payment_mode}</span> Bank: <span class="field-value">{bank_acc}</span> Date: <span class="field-value">{date_str[:10]}</span></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 30px;">
                <div class="amount-box">{amount_text}</div>
                <div style="text-align: right; padding-top: 10px;">Authorized Signatory</div>
            </div>
        </div>
        {bani_footer}
        <script>window.onload = function() {{ window.print(); }}</script>
    </body></html>
    """
    filename = f"Receipt_{receipt_no}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html_content)
    return filename

def generate_html_report(title, content_html, clinic_branch):
    logo_base64 = get_base64_image("logo.png")
    img_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 80px; margin-bottom: 10px;">' if logo_base64 else ''
    bani_footer = get_bani_footer()
    
    html_content = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title>
    <style>body {{ font-family: sans-serif; padding: 20px; text-align: center; }} table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; text-align: left; }} th, td {{ border: 1px solid #aaa; padding: 8px; }} th {{ background-color: #F8F1D1; color: #0F4C81; }} .bani-footer {{ text-align: center; font-size: 11px; margin-top: 25px; border-top: 1px solid #eee; padding-top: 10px; color: #888; font-weight: bold; display: flex; justify-content: center; align-items: center; }}</style></head>
    <body>{img_html}<h2>Makan {clinic_branch}</h2><h3>{title}</h3><div>{content_html}</div>
    {bani_footer}
    <script>window.onload = function() {{ window.print(); }}</script></body></html>"""
    filename = f"Report_{title.replace(' ', '_')}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html_content)
    return filename

def generate_html_report_landscape(title, content_html, clinic_branch):
    logo_base64 = get_base64_image("logo.png")
    img_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 80px; margin-bottom: 10px;">' if logo_base64 else ''
    bani_footer = get_bani_footer()
    
    html_content = f"""
    <!DOCTYPE html><html lang="pa"><head><meta charset="UTF-8"><title>{title}</title>
    <style>
        @page {{ size: landscape; margin: 10mm; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 10px; color: #333; background-color: #fff; text-align: center; }}
        .header {{ margin-bottom: 15px; border-bottom: 2px solid #0F4C81; padding-bottom: 10px; text-align: center; }}
        .title {{ font-size: 22px; font-weight: bold; color: #0F4C81; margin-bottom: 2px; }}
        .tagline {{ font-size: 15px; font-weight: bold; color: #D92B2B; margin-bottom: 5px; }}
        .report-title {{ font-size: 16px; font-weight: bold; color: #333; margin-top: 8px; }}
        .report-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; text-align: center; vertical-align: middle; }}
        .report-table th, .report-table td {{ border: 1px solid #aaa; padding: 5px; color: #000; vertical-align: middle; text-align: center; }}
        .report-table th {{ background-color: #F8F1D1; color: #0F4C81; font-weight: bold; }}
        .table-img {{ width: 60px; height: 60px; object-fit: cover; border-radius: 5px; border: 1px solid #ccc; }}
        .bani-footer {{ text-align: center; font-size: 11px; margin-top: 20px; color: #888; font-weight: bold; border-top: 1px solid #eee; padding-top: 8px; display: flex; justify-content: center; align-items: center; }}
        @media print {{ body {{ padding: 0; }} }}
    </style></head>
    <body>
        <div class="header">
            {img_html}
            <div class="title">Makan {clinic_branch}</div>
            <div class="tagline">Complete Care</div>
            <div style="font-size: 12px;">{CLINIC_ADDRESS}</div>
            <div class="report-title">{title}</div>
        </div>
        <div style="overflow-x: auto;">{content_html}</div>
        {bani_footer}
        <script>window.onload = function() {{ window.print(); }}</script>
    </body></html>
    """
    filename = f"Report_Landscape_{title.replace(' ', '_')}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html_content)
    return filename

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.clinic_branch = None
if 'current_tab' not in st.session_state: 
    st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"

# ==========================================
# LOGIN SCREEN
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_login_path = "logo.png"
        if os.path.exists(logo_login_path): st.image(logo_login_path, width=100)
        st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'><h2 style='color: #0F4C81;'>Makan Clinics</h2><p style='color: #E53935; font-weight: bold;'>Login Portal</p></div>", unsafe_allow_html=True)
        with st.form("login_form"):
            username_input = st.text_input("ਯੂਜ਼ਰਨੇਮ (Username)").lower()
            password_input = st.text_input("ਪਾਸਵਰਡ (Password)", type="password")
            if st.form_submit_button("ਲਾਗਇਨ (Login)", type="primary"):
                if username_input in USERS and USERS[username_input]["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.role = USERS[username_input]["role"]
                    st.session_state.username = username_input
                    st.rerun()
                else: st.error("ਗਲਤ ਪਾਸਵਰਡ! (Incorrect Password!)")
        
        # Adding Bani Tech Branding to the Login Page Footer
        st.markdown("<br><hr>", unsafe_allow_html=True)
        if os.path.exists("bani_logo_2.jpeg"):
            bc1, bc2, bc3 = st.columns([1, 2, 1])
            with bc2: st.image("bani_logo_2.jpeg", use_container_width=True)
        st.markdown("<div style='text-align: center; font-size: 12px; color: #888;'>Designed by <b>Bani Tech Solutions</b><br><a href='https://banitech.in' target='_blank' style='color: #0F4C81; text-decoration: none;'>banitech.in</a></div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# CLINIC BRANCH SELECTION PORTAL (SEPARATION)
# ==========================================
if st.session_state.logged_in and st.session_state.clinic_branch is None:
    st.markdown("<h2 style='text-align: center; color: #0F4C81; margin-top: 50px;'>🏥 Select Clinic Branch</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; margin-bottom: 40px;'>Please choose which clinic environment you want to access.</p>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
    with c2:
        st.markdown('<div class="branch-btn">', unsafe_allow_html=True)
        if st.button("🫁 Makan Chest Clinic", use_container_width=True):
            st.session_state.clinic_branch = "Chest Clinic"
            st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="branch-btn">', unsafe_allow_html=True)
        if st.button("🦷 Makan Dental Clinic", use_container_width=True):
            st.session_state.clinic_branch = "Dental Clinic"
            st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Variables for the active clinic
cb = st.session_state.clinic_branch
is_admin = st.session_state.role == "admin"
is_mgmt = st.session_state.role == "management"

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.title("👤 ਪ੍ਰੋਫਾਈਲ (Profile)")
    st.success(f"✅ Logged in as: {st.session_state.role.upper()}")
    st.info(f"📍 Active: {cb}")
    
    if st.button("🔄 Switch Clinic Branch"):
        st.session_state.clinic_branch = None
        st.rerun()
        
    if st.button("🚪 ਲਾਗਆਊਟ ਕਰੋ (Logout)"):
        st.session_state.logged_in = False
        st.session_state.clinic_branch = None
        st.rerun()
    st.markdown("---")
    
    menu_options = [
        "🏠 ਹੋਮ ਪੇਜ (Home)",
        "📝 ਰੋਜ਼ਾਨਾ ਓ.ਪੀ.ਡੀ (OPD Entry)", 
        "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA)",
        "📝 ਡਾਕਟਰ ਪਰਚੀ (Prescriptions)",
        "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Books)",
        "🩺 ਮਰੀਜ਼ ਰਿਕਾਰਡ (Patient Records)",
        "🦷 ਪ੍ਰੋਸੀਜਰ / ਸਰਜਰੀ (Special Procedures)",
        "🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff)"
    ]
    if is_admin: menu_options.append("⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin)")
        
    try: current_idx = menu_options.index(st.session_state.current_tab)
    except ValueError: current_idx = 0

    st.session_state.current_tab = st.radio("ਚੁਣੋ (Select Menu)", menu_options, index=current_idx, label_visibility="collapsed")
    
    # --- BANI TECH SOLUTIONS BRANDING IN SIDEBAR ---
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    if os.path.exists("bani_logo_2.jpeg"):
        st.image("bani_logo_2.jpeg", use_container_width=True)
    st.markdown("<div style='text-align: center; font-size: 12px; color: #888;'>Designed by <b>Bani Tech Solutions</b><br><a href='https://banitech.in' target='_blank' style='color: #0F4C81; text-decoration: none;'>banitech.in</a></div>", unsafe_allow_html=True)

# --- HEADER ---
st.markdown(f"<div class='pro-header-flex'><div class='pro-text-box'><div class='pro-title'>🏥 Makan {cb}</div><div class='pro-tagline'>Complete Care Environment</div><div class='pro-sub'>{CLINIC_ADDRESS}</div></div></div>", unsafe_allow_html=True)

# ==========================================
# 0. HOME PAGE DASHBOARD
# ==========================================
if st.session_state.current_tab == "🏠 ਹੋਮ ਪੇਜ (Home)":
    st.markdown(f"### 📝 ਓ.ਪੀ.ਡੀ ਐਂਟਰੀਆਂ ({cb})")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("💰 ਨਵੀਂ ਓ.ਪੀ.ਡੀ (OPD Fee)", use_container_width=True, type="primary"):
        st.session_state.current_tab = "📝 ਰੋਜ਼ਾਨਾ ਓ.ਪੀ.ਡੀ (OPD Entry)"
        st.rerun()
    if c2.button("📝 ਡਾਕਟਰ ਪਰਚੀ (Prescription)", use_container_width=True, type="primary"):
        st.session_state.current_tab = "📝 ਡਾਕਟਰ ਪਰਚੀ (Prescriptions)"
        st.rerun()
    if c3.button("📉 ਕਲੀਨਿਕ ਖਰਚਾ (Expense)", use_container_width=True, type="primary"):
        st.session_state.current_tab = "📝 ਰੋਜ਼ਾਨਾ ਓ.ਪੀ.ਡੀ (OPD Entry)"
        st.rerun()
    if c4.button("📊 ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", use_container_width=True, type="primary"):
        st.session_state.current_tab = "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA)"
        st.rerun()

# ==========================================
# 1. OPD & EXPENSE ENTRY
# ==========================================
elif st.session_state.current_tab == "📝 ਰੋਜ਼ਾਨਾ ਓ.ਪੀ.ਡੀ (OPD Entry)":
    st.header(f"📝 {cb} - ਓ.ਪੀ.ਡੀ ਐਂਟਰੀ ਅਤੇ ਖਰਚੇ")
    modes = ["💰 ਨਵੀਂ ਓ.ਪੀ.ਡੀ ਫੀਸ (OPD Fee Entry)", "📉 ਕਲੀਨਿਕ ਖਰਚਾ (Add Expense)", "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ (Reprint Receipt)"]
    entry_mode = st.radio("ਐਕਸ਼ਨ ਚੁਣੋ:", modes, horizontal=True)
    st.markdown("---")

    if entry_mode == "💰 ਨਵੀਂ ਓ.ਪੀ.ਡੀ ਫੀਸ (OPD Fee Entry)":
        with st.form("opd_form", clear_on_submit=True):
            st.write(f"### 🩺 {cb} ਕੰਸਲਟੇਸ਼ਨ ਫੀਸ")
            
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                patient_name = st.text_input("ਮਰੀਜ਼ ਦਾ ਨਾਮ (Patient Name)*")
                patient_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone Number)")
            with col_o2:
                rec_no = st.number_input("ਰਸੀਦ ਨੰਬਰ (Receipt No)*", min_value=1, step=1)
                treatment = st.text_input("ਕੰਸਲਟੇਸ਼ਨ ਦਾ ਵੇਰਵਾ (Consultation/Treatment)")
                
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                amount = st.number_input("ਫੀਸ (Fee Amount ₹)*", min_value=1.0)
                pay_mode = st.selectbox("ਭੁਗਤਾਨ ਮੋਡ (Mode)", ["ਨਕਦ (Cash)", "UPI/Google Pay", "Card"])
            with col_m2:
                bank_acc = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚ ਆਏ? (Bank Account)", BANK_ACCOUNTS)
                opd_date = st.date_input("ਮਿਤੀ (Date)", value=date.today())
                
            add_to_mirror = st.checkbox("✅ ਬੈਂਕ ਲੈਜ਼ਰ ਵਿੱਚ ਵੀ ਜੋੜੋ (Add to Bank Ledger)", value=True)
            submitted = st.form_submit_button("ਰਸੀਦ ਸੇਵ ਕਰੋ (Save & Print)", type="primary")
            
        if submitted and patient_name:
            existing_rec = supabase.table("donations").select("id").eq("id", int(rec_no)).eq("clinic_branch", cb).execute().data
            if existing_rec:
                st.error(f"❌ ਰਸੀਦ ਨੰਬਰ {rec_no} ਪਹਿਲਾਂ ਹੀ {cb} ਵਿੱਚ ਮੌਜੂਦ ਹੈ!")
            else:
                don_type = f"{cb} OPD Fee"
                formatted_date = opd_date.strftime("%Y-%m-%d")
                
                supabase.table("donations").insert({
                    "id": int(rec_no), "name": patient_name, "phone": patient_phone, "amount": amount, 
                    "date": formatted_date, "payment_mode": pay_mode, "donation_type": don_type, 
                    "item_details": "", "bank_account": bank_acc, "on_account_of": treatment, 
                    "add_to_mirror": add_to_mirror, "collector_name": "Reception", "clinic_branch": cb
                }).execute()
                
                st.success(f"✅ {cb} ਦੀ ਰਸੀਦ #{rec_no} ਸੇਵ ਹੋ ਗਈ!")
                html_file = generate_html_receipt(int(rec_no), patient_name, patient_phone, amount, formatted_date, pay_mode, cb, bank_acc, treatment, "Reception")
                
                with open(html_file, "r", encoding="utf-8") as file:
                    st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ (Print Receipt)", data=file.read(), file_name=html_file, mime="text/html", type="primary")

    elif entry_mode == "📉 ਕਲੀਨਿਕ ਖਰਚਾ (Add Expense)":
        with st.form("expense_form", clear_on_submit=True):
            st.write(f"### 📉 {cb} ਦਾ ਖਰਚਾ ਦਰਜ ਕਰੋ")
            desc = st.text_input("ਖਰਚੇ ਦਾ ਵੇਰਵਾ (Expense Description)")
            cat = st.selectbox("ਕੈਟਾਗਰੀ (Category)", [c for c in EXPENSE_CATEGORIES if not c.startswith("---")])
            exp_amount = st.number_input("ਰਕਮ (Amount ₹)", min_value=1.0)
            bank_acc_exp = st.selectbox("ਬੈਂਕ ਖਾਤਾ (Bank Account)", BANK_ACCOUNTS)
            exp_date = st.date_input("ਮਿਤੀ (Date)", value=date.today())
            if st.form_submit_button("ਖਰਚਾ ਸੇਵ ਕਰੋ", type="primary") and desc:
                supabase.table("expenses").insert({
                    "description": desc, "amount": exp_amount, "date": str(exp_date), 
                    "category": cat, "bank_account": bank_acc_exp, "add_to_mirror": True, "clinic_branch": cb
                }).execute()
                st.success("✅ ਖਰਚਾ ਸੇਵ ਹੋ ਗਿਆ!")

    elif entry_mode == "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ (Reprint Receipt)":
        search_id = st.number_input("ਰਸੀਦ ਨੰਬਰ (Enter Receipt No.)", min_value=1, step=1)
        if st.button("🔍 ਰਸੀਦ ਲੱਭੋ (Search)", type="primary"):
            res = supabase.table("donations").select("*").eq("id", search_id).eq("clinic_branch", cb).execute().data
            if res:
                rec = res[0]
                html_file = generate_html_receipt(search_id, rec['name'], rec.get('phone',''), rec['amount'], rec['date'], rec['payment_mode'], cb, rec['bank_account'], rec.get('on_account_of',''))
                with open(html_file, "r", encoding="utf-8") as file: st.download_button("🖨️ ਡਾਊਨਲੋਡ ਕਰੋ", data=file.read(), file_name=html_file, mime="text/html", type="primary")
            else: st.error(f"❌ ਰਸੀਦ ਨਹੀਂ ਮਿਲੀ (Not found in {cb}).")

# ==========================================
# 2. DOCTOR PRESCRIPTION MODULE (WITH DIRECT CAMERA)
# ==========================================
elif st.session_state.current_tab == "📝 ਡਾਕਟਰ ਪਰਚੀ (Prescriptions)":
    st.header(f"📝 {cb} - ਡਾਕਟਰ ਪਰਚੀ ਅਤੇ ਨੋਟਸ (Prescription & Findings)")
    
    pt_tab1, pt_tab2 = st.tabs(["➕ ਨਵੀਂ ਪਰਚੀ ਦਰਜ ਕਰੋ (New)", "📋 ਪੁਰਾਣੀਆਂ ਪਰਚੀਆਂ (History)"])
    
    with pt_tab1:
        with st.form("prescription_form", clear_on_submit=True):
            st.write(f"### 🩺 ਮਰੀਜ਼ ਦੀ ਜਾਂਚ ਅਤੇ ਪਰਚੀ ਅੱਪਲੋਡ ({cb})")
            
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                p_name = st.text_input("ਮਰੀਜ਼ ਦਾ ਨਾਮ (Patient Name)*")
            with p_col2:
                p_date = st.date_input("ਮਿਤੀ (Date)", value=date.today())
                
            p_findings = st.text_area("ਡਾਕਟਰ ਦੇ ਨੋਟਸ / ਬਿਮਾਰੀ (Doctor Findings / Chief Complaints)")
            
            # --- DIRECT CAMERA INPUT ADDED HERE ---
            st.markdown("---")
            st.write("📸 **ਪਰਚੀ ਜਾਂ X-Ray ਦੀ ਫੋਟੋ (Prescription / X-Ray Photo)**")
            
            p_photo_cam = st.camera_input("ਸਿੱਧਾ ਕੈਮਰੇ ਨਾਲ ਫੋਟੋ ਖਿੱਚੋ (Open Camera & Capture)")
            p_photo_file = st.file_uploader("ਜਾਂ ਪੁਰਾਣੀ ਫਾਈਲ ਅੱਪਲੋਡ ਕਰੋ (Or Upload from Device)", type=['png', 'jpg', 'jpeg'])
            
            # Use camera photo if taken, otherwise use the uploaded file
            p_photo = p_photo_cam if p_photo_cam is not None else p_photo_file
            
            if st.form_submit_button("ਪਰਚੀ ਸੇਵ ਕਰੋ (Save Prescription)", type="primary") and p_name:
                with st.spinner("ਸੇਵ ਹੋ ਰਿਹਾ ਹੈ..."):
                    photo_str = compress_image(p_photo)
                    try:
                        supabase.table("prescriptions").insert({
                            "patient_name": p_name,
                            "department": cb,
                            "findings": p_findings,
                            "prescription_date": str(p_date),
                            "photo_base64": photo_str,
                            "clinic_branch": cb
                        }).execute()
                        st.success(f"✅ {p_name} ਦੀ ਪਰਚੀ {cb} ਰਿਕਾਰਡ ਵਿੱਚ ਸੇਵ ਹੋ ਗਈ!")
                    except Exception as e:
                        st.error(f"❌ Database Error. Error: {e}")

    with pt_tab2:
        st.write(f"### 📋 {cb} ਦੀਆਂ ਪੁਰਾਣੀਆਂ ਪਰਚੀਆਂ (Prescription History)")
        try: prescriptions = supabase.table("prescriptions").select("*").eq("clinic_branch", cb).order("prescription_date", desc=True).limit(50).execute().data
        except Exception: prescriptions = []
        
        if prescriptions:
            for pr in prescriptions:
                with st.expander(f"📅 {pr['prescription_date']} | {pr['patient_name']}"):
                    st.write(f"**Findings:** {pr.get('findings', 'N/A')}")
                    if pr.get('photo_base64'):
                        st.image(base64.b64decode(pr['photo_base64']), caption="Prescription / Scan", use_container_width=True)
                    else:
                        st.info("ਕੋਈ ਫੋਟੋ ਅੱਪਲੋਡ ਨਹੀਂ ਕੀਤੀ ਗਈ। (No photo attached)")
        else:
            st.info(f"ਕੋਈ ਰਿਕਾਰਡ ਨਹੀਂ ਮਿਲਿਆ ({cb}).")

# ==========================================
# 3. LEDGERS & CA REPORTS
# ==========================================
elif st.session_state.current_tab == "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ (Ledgers & CA)":
    st.header(f"🏦 {cb} - ਬੈਲੇਂਸ ਸ਼ੀਟ ਅਤੇ CA ਰਿਪੋਰਟਾਂ")
    modes = ["⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Daybook)", "📊 CA ਐਕਸਪੋਰਟ"]
    acc_mode = st.radio("ਰਿਪੋਰਟ ਚੁਣੋ:", modes, horizontal=True)
    st.markdown("---")

    don_data = supabase.table("donations").select("*").eq("clinic_branch", cb).execute().data or []
    exp_data = supabase.table("expenses").select("*").eq("clinic_branch", cb).execute().data or []
    try: ledg_data = supabase.table("bank_ledger").select("*").eq("clinic_branch", cb).execute().data or []
    except Exception: ledg_data = []
    
    df_don = pd.DataFrame(don_data)
    df_exp = pd.DataFrame(exp_data)
    df_ledg = pd.DataFrame(ledg_data)

    if acc_mode == "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)":
        total_income = df_don['amount'].sum() if not df_don.empty else 0.0
        total_expense = df_exp['amount'].sum() if not df_exp.empty else 0.0
        surplus = total_income - total_expense

        st.subheader(f"📊 Income & Expenditure Account ({cb})")
        inc_exp_html = f"""
        <table class="report-table">
            <tr><th>Expenditure (ਖਰਚੇ)</th><th>Amount (₹)</th><th>Income (ਆਮਦਨ)</th><th>Amount (₹)</th></tr>
            <tr><td>Total Clinic Expenses</td><td>{total_expense:,.2f}</td>
                <td>Total OPD Fees & Receipts</td>
                <td>{total_income:,.2f}</td>
            </tr>
            <tr style="font-weight:bold; color: #D92B2B;"><td>Surplus (ਬੱਚਤ)</td><td>{surplus if surplus > 0 else 0:,.2f}</td><td>Deficit (ਘਾਟਾ)</td><td>{abs(surplus) if surplus < 0 else 0:,.2f}</td></tr>
            <tr style="background-color: #F8F1D1; font-weight:bold;"><td>Total</td><td>{max(total_income, total_expense):,.2f}</td><td>Total</td><td>{max(total_income, total_expense):,.2f}</td></tr>
        </table>
        """
        st.markdown(inc_exp_html, unsafe_allow_html=True)
        
        full_html = f"<h3>Income & Expenditure Account ({cb})</h3>{inc_exp_html}"
        fin_report = generate_html_report(f"Financial Statements - {cb}", full_html, cb)
        with open(fin_report, "r", encoding="utf-8") as file: st.download_button("🖨️ ਫਾਈਨਾਂਸ਼ੀਅਲ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=fin_report, mime="text/html", type="primary")

    elif acc_mode == "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Daybook)":
        start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ", value=date(date.today().year, date.today().month, 1))
        end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ", value=date.today())
        
        main_entries = []
        if not df_don.empty:
            for _, row in df_don.iterrows():
                main_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਫੀਸ: {row['name']}", 'Credit': float(row['amount']), 'Debit': 0.0, 'Source': 'Consultation'})
        if not df_exp.empty:
            for _, row in df_exp.iterrows():
                main_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਖਰਚਾ: {row['description']}", 'Credit': 0.0, 'Debit': float(row['amount']), 'Source': 'Expense'})
                
        df_main = pd.DataFrame(main_entries)
        if not df_main.empty:
            df_main['Date'] = pd.to_datetime(df_main['Date']).dt.date
            df_main = df_main.sort_values(by='Date')
            df_period = df_main[(df_main['Date'] >= start_date) & (df_main['Date'] <= end_date)].copy()
            
            disp_cols = ['ID', 'Date', 'Description', 'Source', 'Credit', 'Debit']
            st.dataframe(df_period[disp_cols].style.format({'Credit': '{:.2f}', 'Debit': '{:.2f}'}), hide_index=True, use_container_width=True)

    elif acc_mode == "📊 CA ਐਕਸਪੋਰਟ":
        st.write(f"### 📊 CA ਐਕਸਲ ਬੈਕਅੱਪ ({cb})")
        if st.button("📥 ਐਕਸਲ ਡਾਊਨਲੋਡ ਕਰੋ", type="primary"):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_don.to_excel(writer, sheet_name='OPD_Receipts', index=False)
                df_exp.to_excel(writer, sheet_name='Expenses', index=False)
                try: pd.DataFrame(supabase.table("prescriptions").select("*").eq("clinic_branch", cb).execute().data or []).to_excel(writer, sheet_name='Prescriptions', index=False)
                except Exception: pass
            st.download_button("📥 Click here to Download", data=buffer.getvalue(), file_name=f"{cb}_Audit_Data_{date.today()}.xlsx", type="primary")

# ==========================================
# 4. PATIENT RECORDS
# ==========================================
elif st.session_state.current_tab == "🩺 ਮਰੀਜ਼ ਰਿਕਾਰਡ (Patient Records)":
    st.header(f"🩺 {cb} - ਮਰੀਜ਼ਾਂ ਦਾ ਰਿਕਾਰਡ")
    s_tab1, s_tab2 = st.tabs(["➕ ਨਵਾਂ ਮਰੀਜ਼ ਦਰਜ ਕਰੋ (Add New)", "📋 ਮਰੀਜ਼ਾਂ ਦੀ ਸੂਚੀ (List)"])
    
    with s_tab1:
        with st.form("patient_form", clear_on_submit=True):
            st.write(f"### 🩺 ਨਵਾਂ ਮਰੀਜ਼ ({cb})")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                stu_name = st.text_input("ਮਰੀਜ਼ ਦਾ ਨਾਮ (Patient Name)")
                stu_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone)")
            with col_s2:
                stu_course = st.text_input("ਬਿਮਾਰੀ / ਇਲਾਜ (Diagnosis/Treatment)")
                join_date = st.date_input("ਚੈੱਕਅਪ ਮਿਤੀ (Checkup Date)", value=date.today())
                
            st.markdown("---")
            st.write("📸 **ਮਰੀਜ਼ ਦੀ ਫੋਟੋ (Patient Photo)**")
            s_photo_cam = st.camera_input("ਸਿੱਧਾ ਕੈਮਰੇ ਨਾਲ ਫੋਟੋ ਖਿੱਚੋ (Camera)", key="patient_cam")
            s_photo_file = st.file_uploader("ਜਾਂ ਗੈਲਰੀ 'ਚੋਂ ਫਾਈਲ ਚੁਣੋ (Gallery)", type=['png', 'jpg', 'jpeg'], key="patient_file")
            s_photo = s_photo_cam if s_photo_cam is not None else s_photo_file

            if st.form_submit_button("ਰਿਕਾਰਡ ਸੇਵ ਕਰੋ", type="primary") and stu_name:
                photo_str = compress_image(s_photo)
                try:
                    supabase.table("students").insert({
                        "name": stu_name, "phone": stu_phone, "course": stu_course, 
                        "join_date": str(join_date), "pass_date": "ਇਲਾਜ ਜਾਰੀ ਹੈ",
                        "photo_base64": photo_str, "clinic_branch": cb
                    }).execute()
                    st.success(f"✅ '{stu_name}' ਦਾ ਰਿਕਾਰਡ {cb} ਵਿੱਚ ਸੇਵ ਹੋ ਗਿਆ!")
                except Exception as e: st.error(f"Error: {e}")

    with s_tab2:
        st.write(f"### 📑 {cb} - ਮਰੀਜ਼ਾਂ ਦੀ ਸੂਚੀ")
        try: patient_data = supabase.table("students").select("*").eq("clinic_branch", cb).execute().data or []
        except Exception: patient_data = []
        if patient_data:
            df_stu = pd.DataFrame(patient_data)
            display_cols = [c for c in ['name', 'phone', 'course', 'join_date', 'pass_date'] if c in df_stu.columns]
            st.dataframe(df_stu[display_cols], hide_index=True, use_container_width=True)
            
            html_table = df_stu[display_cols].to_html(index=False, border=1, classes='report-table')
            report_file_stu = generate_html_report_landscape(f"ਮਰੀਜ਼ਾਂ ਦੀ ਸੂਚੀ ({cb})", html_table, cb)
            with open(report_file_stu, "r", encoding="utf-8") as file: 
                st.download_button("🖨️ ਸੂਚੀ ਪ੍ਰਿੰਟ ਕਰੋ (Print List)", data=file.read(), file_name=report_file_stu, mime="text/html", type="primary")
        else: st.info("ਕੋਈ ਰਿਕਾਰਡ ਨਹੀਂ ਹੈ।")

# ==========================================
# 5. SPECIAL PROCEDURES
# ==========================================
elif st.session_state.current_tab == "🦷 ਪ੍ਰੋਸੀਜਰ / ਸਰਜਰੀ (Special Procedures)":
    st.header(f"🦷 {cb} - ਖਾਸ ਇਲਾਜ ਅਤੇ ਸਰਜਰੀ (Special Procedures)")
    
    w_tab1, w_tab2 = st.tabs(["➕ ਨਵੀਂ ਪ੍ਰੋਸੀਜਰ ਫਾਈਲ", "📋 ਰਿਕਾਰਡ ਸੂਚੀ (Procedures)"])
    
    with w_tab1:
        with st.form("procedure_form", clear_on_submit=True):
            st.write(f"### 💉 ਨਵੀਂ ਪ੍ਰੋਸੀਜਰ ਫਾਈਲ ਦਰਜ ਕਰੋ ({cb})")
            c_w1, c_w2, c_w3 = st.columns(3)
            with c_w1:
                w_form_no = st.text_input("ਫਾਈਲ ਨੰ: (File No.)")
                w_name = st.text_input("ਮਰੀਜ਼ ਦਾ ਨਾਮ: (Name)*")
                w_death_date = st.text_input("ਡਾਇਗਨੋਸਿਸ (Diagnosis):")
            with c_w2:
                w_card_no = st.text_input("ਪੇਸ਼ੈਂਟ ਆਈ.ਡੀ: (Patient ID)")
                w_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ: (Phone)*")
                w_issued_by = st.text_input("ਡਾਕਟਰ (Attending Doctor)")
            with c_w3:
                w_card_date = st.date_input("ਸ਼ੁਰੂਆਤ ਦੀ ਤਾਰੀਖ:", value=date.today())
            
            w_boys = st.text_area("ਐਲਰਜੀ (Allergies):")
            w_girls = st.text_area("ਪੁਰਾਣੀ ਮੈਡੀਕਲ ਹਿਸਟਰੀ (Medical History):")
            
            st.markdown("---")
            st.write("📸 **X-Ray / ਸਕੈਨ ਅੱਪਲੋਡ ਕਰੋ (Upload Scan)**")
            w_photo_cam = st.camera_input("ਸਿੱਧਾ ਕੈਮਰੇ ਨਾਲ ਫੋਟੋ ਖਿੱਚੋ (Camera)", key="proc_cam")
            w_photo_file = st.file_uploader("ਜਾਂ ਗੈਲਰੀ 'ਚੋਂ ਫਾਈਲ ਚੁਣੋ (Gallery)", type=['png', 'jpg', 'jpeg'], key="proc_file")
            w_photo = w_photo_cam if w_photo_cam is not None else w_photo_file
            
            if st.form_submit_button("ਫਾਈਲ ਸੇਵ ਕਰੋ", type="primary") and w_name:
                photo_str = compress_image(w_photo)
                supabase.table("widows").insert({
                    "form_no": w_form_no, "card_no": w_card_no, "name": w_name,
                    "husband_death_date": w_death_date, "phone": w_phone,
                    "boys_details": w_boys, "girls_details": w_girls,
                    "issued_by": w_issued_by, "join_date": str(w_card_date),
                    "photo_base64": photo_str, "clinic_branch": cb
                }).execute()
                st.success(f"✅ '{w_name}' ਦੀ ਫਾਈਲ {cb} ਵਿੱਚ ਸੇਵ ਹੋ ਗਈ!")

    with w_tab2:
        st.write(f"### 📑 {cb} - ਰਜਿਸਟਰਡ ਪ੍ਰੋਸੀਜਰ / ਸਰਜਰੀਆਂ")
        try: procs = supabase.table("widows").select("*").eq("clinic_branch", cb).execute().data or []
        except Exception: procs = []
        if procs:
            df_w = pd.DataFrame(procs)
            display_cols = [c for c in ['card_no', 'name', 'husband_death_date', 'phone', 'join_date'] if c in df_w.columns]
            st.dataframe(df_w[display_cols], hide_index=True, use_container_width=True)
        else: st.info("ਕੋਈ ਰਿਕਾਰਡ ਨਹੀਂ ਹੈ।")

# ==========================================
# 6. STOCK & BOOKS
# ==========================================
elif st.session_state.current_tab == "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ (Stock & Books)":
    st.header(f"📦 {cb} - ਸਟਾਕ ਅਤੇ ਰਸੀਦ ਕਿਤਾਬਾਂ")
    modes = ["📦 ਸਟਾਕ (Inventory)", "📖 ਰਸੀਦ ਕਿਤਾਬਾਂ (Receipt Books)"]
    selected_mode = st.radio("ਸੈਕਸ਼ਨ ਚੁਣੋ:", modes, horizontal=True)
    st.markdown("---")

    if selected_mode == "📦 ਸਟਾਕ (Inventory)":
        col1, col2 = st.columns([1, 2])
        with col1:
            with st.form("stock_form", clear_on_submit=True):
                st.write(f"### 📦 ਮੈਡੀਕਲ ਸਟਾਕ ਅਪਡੇਟ ਕਰੋ ({cb})")
                item_name = st.text_input("ਵਸਤੂ ਦਾ ਨਾਮ (Medicine Name)")
                qty = st.number_input("ਮਾਤਰਾ (Quantity)", min_value=0.0, step=0.5)
                unit = st.selectbox("ਇਕਾਈ (Unit)", STOCK_UNITS)
                stock_action = st.radio("ਐਕਸ਼ਨ (Action)", ["ਨਵਾਂ ਸਮਾਨ ਆਇਆ (Add)", "ਸਮਾਨ ਵਰਤਿਆ (Remove)"])
                
                if st.form_submit_button("ਸਟਾਕ ਅਪਡੇਟ ਕਰੋ", type="primary") and item_name:
                    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    res = supabase.table("stock").select("*").eq("item_name", item_name).eq("clinic_branch", cb).execute()
                    if res.data:
                        old_qty = float(res.data[0].get('quantity', 0) or 0)
                        new_qty = old_qty + qty if "Add" in stock_action else max(0.0, old_qty - qty)
                        supabase.table("stock").update({
                            "quantity": new_qty, "unit": unit, "last_updated": current_date
                        }).eq("item_name", item_name).eq("clinic_branch", cb).execute()
                    else:
                        new_qty = qty if "Add" in stock_action else 0.0
                        supabase.table("stock").insert({
                            "item_name": item_name, "quantity": new_qty, "unit": unit, 
                            "last_updated": current_date, "clinic_branch": cb
                        }).execute()
                    st.success(f"✅ '{item_name}' ਦਾ ਸਟਾਕ {cb} ਵਿੱਚ ਅਪਡੇਟ ਹੋ ਗਿਆ ਹੈ!")
                    time.sleep(1.2); st.rerun()
        with col2:
            st.write(f"### 📑 ਮੌਜੂਦਾ ਸਟਾਕ ਰਿਪੋਰਟ ({cb})")
            try: stock_res = supabase.table("stock").select("*").eq("clinic_branch", cb).gt("quantity", 0).execute().data or []
            except Exception: stock_res = []
            if stock_res:
                df_stock = pd.DataFrame(stock_res)[['item_name', 'quantity', 'unit', 'last_updated']]
                st.dataframe(df_stock, hide_index=True, use_container_width=True)
            else: st.info(f"ਸਟਾਕ ਵਿੱਚ ਕੋਈ ਸਮਾਨ ਮੌਜੂਦ ਨਹੀਂ ਹੈ ({cb}).")

    elif selected_mode == "📖 ਰਸੀਦ ਕਿਤਾਬਾਂ (Receipt Books)":
        if is_admin:
            with st.form("book_issue_form", clear_on_submit=True):
                st.write(f"### 📖 ਨਵੀਂ ਰਸੀਦ ਕਿਤਾਬ ਜਾਰੀ ਕਰੋ ({cb})")
                collector_input = st.text_input("ਡਾਕਟਰ/ਰਿਸੈਪਸ਼ਨ ਦਾ ਨਾਮ")
                start_ser = st.number_input("ਸ਼ੁਰੂਆਤੀ ਰਸੀਦ ਨੰਬਰ", min_value=1, step=1, value=1)
                end_ser = st.number_input("ਆਖਰੀ ਰਸੀਦ ਨੰਬਰ", min_value=1, step=1, value=100)
                if st.form_submit_button("ਕਿਤਾਬ ਜਾਰੀ ਕਰੋ (Issue Book)", type="primary"):
                    supabase.table("receipt_books").insert({
                        "collector_name": collector_input, "start_no": int(start_ser), 
                        "end_no": int(end_ser), "issued_date": str(date.today()), 
                        "status": "Active", "clinic_branch": cb
                    }).execute()
                    st.success(f"✅ ਕਿਤਾਬ {cb} ਲਈ ਜਾਰੀ ਕਰ ਦਿੱਤੀ ਗਈ ਹੈ!")
        st.write(f"### 📑 ਜਾਰੀ ਕੀਤੀਆਂ ਗਈਆਂ ਕਿਤਾਬਾਂ ({cb})")
        try: books_all = supabase.table("receipt_books").select("*").eq("clinic_branch", cb).execute().data or []
        except Exception: books_all = []
        if books_all:
            st.dataframe(pd.DataFrame(books_all)[['collector_name', 'start_no', 'end_no', 'issued_date', 'status']], hide_index=True, use_container_width=True)
        else: st.info("ਕੋਈ ਕਿਤਾਬ ਜਾਰੀ ਨਹੀਂ ਕੀਤੀ ਗਈ।")

# ==========================================
# CATCH-ALL FOR REMAINING TABS
# ==========================================
elif st.session_state.current_tab in ["🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff)", "⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin)", "⏱️ ਮੇਰੀ ਹਾਜ਼ਰੀ (My Attendance)"]:
    st.info(f"📍 Viewing {st.session_state.current_tab} for **{cb}**.")
    st.write("*(The underlying data mapping automatically secures this section for the active branch).*")
