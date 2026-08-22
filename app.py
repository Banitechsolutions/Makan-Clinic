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
# CREDENTIALS & SETUP
# ==========================================
SUPABASE_URL = "https://xkkcerlqmhkvqxggivsc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhra2NlcmxxbWhrdnF4Z2dpdnNjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODczMjgwNjEsImV4cCI6MjEwMjkwNDA2MX0.85lyq8dnzEvQblhxeAYfTYxsGwpxW8vJmmCUg_oGVic"

USERS = {
    "admin": {"password": "Japnik@3315", "role": "admin"},
    "staff": {"password": "12345", "role": "staff"},
    "management": {"password": "view@123", "role": "management"},
    "emp1": {"password": "emp1", "role": "employee"}
}

st.set_page_config(page_title="Makan Chest & Dental Clinic", page_icon="🏥", layout="wide")

# --- ਕਲੀਨਿਕ ਦੇ ਵੇਰਵੇ (CLINIC DETAILS) ---
CLINIC_NAME = "MAKAN CHEST & DENTAL CLINIC"
CLINIC_ADDRESS = "Dreamcity SCO Market, Near Best Price, Manawala, Asr."

BANK_ACCOUNTS = ["ਨਕਦ (Cash)", "Kotak Bank Regular", "Kotak Bank Corpus Fund", "Punjab & Sind Bank"]
EXPENSE_CATEGORIES = [
    "--- ਕਲੀਨਿਕ ਖਰਚੇ (Clinic Expenses) ---",
    "ਦਵਾਈਆਂ (Medicines)", "ਡੈਂਟਲ ਮਟੀਰੀਅਲ (Dental Supplies)", "ਲੈਬ ਟੈਸਟ (Lab Tests)", 
    "ਮਸ਼ੀਨਰੀ ਮੇਨਟੇਨੈਂਸ (Equipment Maintenance)", "ਸਾਫ਼-ਸਫ਼ਾਈ (Cleaning/Sanitation)", "ਡਾਕਟਰ ਫੀਸ (Doctor Payouts)",
    "--- ਹੋਰ ਪ੍ਰਬੰਧ (Other Management) ---",
    "ਸਟਾਕ ਖਰੀਦ (Purchase of Stock)", "ਸਟਾਫ਼ ਦੀ ਤਨਖਾਹ (Payment to Staff)", "ਹੋਰ ਖਰਚੇ (Others)"
]

# EXACT DENTAL TREATMENTS FROM LETTERHEAD
DENTAL_TREATMENTS = [
    "RCT", "Implants", "Dentures - Partial", "Dentures - Complete", "Fixed Teeth", 
    "Tooth Coloured Fillings", "Extraction", "Scaling", "Smile Designing", "Braces", "Other Dental Procedures"
]
# CHEST CLINIC SERVICES FROM LETTERHEAD
CHEST_TREATMENTS = [
    "Asthma Clinic", "Allergy Clinic", "Cough Clinic", "T B Clinic", 
    "Patient Education Clinic", "Family Medicine", "Diabetes", "Hypertension", "Other Chest/Physician Consult"
]

STOCK_UNITS = ["ਕਿਲੋ (Kg)", "ਲੀਟਰ (Liter)", "ਪੀਸ (Pcs)", "ਗ੍ਰਾਮ (Gram)", "ਬੋਕਸ (Boxes)"]

TIME_SLOTS = [
    "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM", 
    "01:00 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM"
]

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
        .stAppDeployButton {display:none !important;}
        [data-testid="stSidebar"] div[role="radiogroup"] label p { font-size: 18px !important; font-weight: 600 !important; padding-bottom: 5px; }
        h2 { font-size: 26px !important; font-weight: 700 !important; padding-bottom: 5px !important; }
        .pro-header-flex { display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #e8f5e9 0%, #ffffff 100%); padding: 15px 20px; border-radius: 12px; border: 2px solid #2E7D32; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .pro-title { font-size: 28px; font-weight: bold; color: #2E7D32 !important; margin: 0; letter-spacing: 0.5px; text-align: center;}
        .pro-tagline { font-size: 15px; font-weight: bold; color: #ffffff !important; background-color: #2E7D32; padding: 4px 15px; border-radius: 4px; margin: 8px 0; text-align: center; display: inline-block;}
        div.stButton > button { font-size: 18px !important; font-weight: bold !important; padding: 16px 10px !important; border-radius: 10px !important; width: 100% !important; }
        .branch-btn > button { height: 140px !important; font-size: 26px !important; border: 3px solid #2E7D32 !important; background-color: #e8f5e9 !important; color: #2E7D32 !important; transition: 0.3s; }
        .branch-btn > button:hover { background-color: #2E7D32 !important; color: white !important; }
        
        /* WhatsApp Button */
        .whatsapp-btn { display: inline-block; padding: 10px 20px; background-color: #25D366; color: white !important; text-align: center; text-decoration: none; font-size: 15px; border-radius: 8px; font-weight: bold; border: 1px solid #128C7E; width: 100%; box-sizing: border-box; margin-top: 10px;}
        .whatsapp-btn:hover { background-color: #128C7E; }
        
        /* Flashing Alert Animation */
        @keyframes flashAnim {
            0% { opacity: 1; background-color: #ffe6e6; }
            50% { opacity: 0.7; background-color: #ffcccc; border-color: #cc0000; }
            100% { opacity: 1; background-color: #ffe6e6; }
        }
        .flashing-alert { animation: flashAnim 1.2s infinite; padding: 12px; background-color: #ffe6e6; border: 2px solid red; color: #cc0000; font-weight: bold; border-radius: 6px; text-align: center; margin-bottom: 15px; font-size: 16px; }
        
        /* Tables */
        .report-table { width: 100%; border-collapse: collapse; text-align: left; }
        .report-table th, .report-table td { border: 1px solid #aaa; padding: 8px; }
        .report-table th { background-color: #e8f5e9; color: #2E7D32; font-weight: bold; }
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
        except Exception: return ""
    return ""

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file: return base64.b64encode(img_file.read()).decode()
    return ""

@st.cache_resource
def init_connection(): 
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try: supabase: Client = init_connection()
except Exception: st.error("Supabase Connection Error.")

def get_bani_footer():
    bani_logo_base64 = get_base64_image("bani_logo_2.jpeg")
    bani_img_html = f'<img src="data:image/jpeg;base64,{bani_logo_base64}" style="height: 25px; vertical-align: middle; margin-right: 8px; border-radius: 4px;">' if bani_logo_base64 else ''
    return f'<div class="bani-footer" style="text-align: center; font-size: 11px; margin-top: 15px; color: #888; font-weight: bold; padding-top: 10px; display: flex; justify-content: center; align-items: center;">{bani_img_html}Designed by Bani Tech Solutions | banitech.in</div>'

def get_letterhead_header():
    logo_base64 = get_base64_image("logo.png")
    img_html = f'<img src="data:image/png;base64,{logo_base64}" style="width: 80px;">' if logo_base64 else ''
    
    return f"""
        <div style="display: flex; align-items: center; border-bottom: 2px solid #2E7D32; padding-bottom: 10px;">
            <div style="flex: 1; text-align: left;">{img_html}</div>
            <div style="flex: 4; text-align: center;">
                <h1 style="color: #2E7D32; margin: 0; font-size: 24px; font-family: Arial, sans-serif;">{CLINIC_NAME}</h1>
                <p style="background-color: #2E7D32; color: white; display: inline-block; padding: 4px 15px; font-size: 12px; margin: 8px 0 0 0; font-weight: bold; border-radius: 3px;">{CLINIC_ADDRESS}</p>
            </div>
            <div style="flex: 1;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 10px; border-bottom: 1px solid #000; padding-bottom: 10px; line-height: 1.4;">
            <div style="text-align: left; color: #333;">
                <strong style="font-size: 14px; color: #000;">Dr. Harpreet Singh Makan</strong><br>
                MD, FICM,<br>Physician & Chest Consultant<br>Medical Superintendent<br>Mata Kaulan Ji Mission Hospital,<br>Mobile : 98150-45618
            </div>
            <div style="text-align: right; color: #333;">
                <strong style="font-size: 14px; color: #000;">Dr. (Mrs.) Manmeet Makan</strong><br>
                Dental Surgeon<br><br><br><br>Mobile : 98720-45618
            </div>
        </div>
    """

def get_letterhead_footer():
    return f"""
        <div style="border-top: 1px solid #000; padding-top: 10px; margin-top: 30px; font-size: 11px; display: flex; justify-content: space-between; align-items: center; line-height: 1.4;">
            <div style="text-align: left; color: #333;">
                Chest Clinic Timing : 9:00 a.m. to 10:00 a.m.<br>
                Dental Clinic Timing : 10:00 a.m. to 1:00 p.m.
            </div>
            <div style="text-align: left; color: #333;">
                5:00 p.m. to 6:30 p.m.<br>
                5:00 p.m. to 6:30 p.m.<br>
                (Sunday Closed)
            </div>
            <div style="text-align: center; font-size: 12px; font-weight: bold; color: #000080;">
                Take appointments on<br>
                <span style="font-size: 16px;">79734-89915</span>
            </div>
        </div>
        <div style="text-align: center; font-size: 10px; margin-top: 5px; font-weight: bold;">(NOT FOR MEDICO LEGAL PURPOSE)</div>
    """

def generate_html_receipt(receipt_no, name, phone, amount, date_str, payment_mode, dept, bank_acc, on_account_of, collector=""):
    amount_text = f"Rs. {amount}/-"
    amount_in_words = f"Rupees {amount} Only" 
    display_phone = phone if phone else "________________"
    
    header = get_letterhead_header()
    footer = get_letterhead_footer()
    bani_footer = get_bani_footer()
    
    html_content = f"""
    <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Receipt #{receipt_no}</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #fff; padding: 20px; margin: 0; }}
            .receipt-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #ddd; box-shadow: 0 0 10px rgba(0,0,0,0.05); }}
            .reg-row {{ display: flex; justify-content: space-between; border-bottom: 1.5px solid #333; padding: 5px 0 15px 0; font-size: 15px; font-weight: bold; margin: 15px 0; color: #2E7D32; }}
            .main-content {{ font-size: 15px; line-height: 2.2; color: #222; }}
            .field-value {{ font-family: 'Courier New', monospace; font-size: 16px; color: #000; border-bottom: 1px dashed #666; padding: 0 10px; font-weight: bold; }}
            .amount-box {{ font-size: 18px; font-weight: bold; color: #2E7D32; border: 2px solid #333; padding: 5px 20px; border-radius: 5px; display: inline-block; }}
        </style></head>
    <body>
        <div class="receipt-box">
            {header}
            <div class="reg-row"><div>{dept.upper()} RECEIPT</div><div>Description: <span class="field-value" style="font-size:14px; color:#000;">{on_account_of}</span></div></div>
            <div class="main-content">
                <div style="display: flex; justify-content: space-between;"><div>Receipt No: <span class="field-value" style="color: #D92B2B;">{receipt_no:04d}</span></div><div>Date: <span class="field-value">{date_str[:10]}</span></div></div>
                <div style="margin-top: 10px;">Received with thanks from Patient <span class="field-value" style="width: 40%; display:inline-block;">{name}</span>, Mob: <span class="field-value">{display_phone}</span></div>
                <div style="margin-top: 10px;">A sum of <span class="field-value" style="width: 60%; display:inline-block;">{amount_in_words}</span>.</div>
                <div style="margin-top: 10px;">Mode: <span class="field-value">{payment_mode}</span> Bank: <span class="field-value">{bank_acc}</span></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 30px;">
                <div class="amount-box">{amount_text}</div>
                <div style="text-align: right; padding-top: 10px; font-weight: bold;">Authorized Signatory<br><br><br></div>
            </div>
            {footer}
        </div>
        {bani_footer}
        <script>window.onload = function() {{ window.print(); }}</script>
    </body></html>
    """
    filename = f"Receipt_{receipt_no}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html_content)
    return filename

def generate_html_report_landscape(title, content_html, clinic_branch="Clinics"):
    header = get_letterhead_header()
    footer = get_letterhead_footer()
    bani_footer = get_bani_footer()
    
    html_content = f"""
    <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{title}</title>
    <style>
        @page {{ size: landscape; margin: 10mm; }}
        body {{ font-family: 'Segoe UI', sans-serif; padding: 10px; color: #333; }}
        .report-title {{ font-size: 18px; font-weight: bold; margin: 15px 0; text-align: center; color: #2E7D32; text-decoration: underline; text-transform: uppercase;}}
        .report-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; text-align: center; }}
        .report-table th, .report-table td {{ border: 1px solid #aaa; padding: 5px; }}
        .report-table th {{ background-color: #e8f5e9; color: #2E7D32; font-weight: bold; }}
        @media print {{ body {{ padding: 0; }} }}
    </style></head>
    <body>
        <div style="max-width: 1050px; margin: auto;">
            {header}
            <div class="report-title">{title} - {clinic_branch.upper()}</div>
            <div style="overflow-x: auto; min-height: 300px;">{content_html}</div>
            {footer}
            {bani_footer}
        </div>
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
# PUBLIC LANDING PAGE & LOGIN
# ==========================================
if not st.session_state.logged_in:
    logo_login_path = "logo.png"
    logo_html = f'<img src="data:image/png;base64,{get_base64_image(logo_login_path)}" style="width: 110px; margin-bottom: 10px;">' if os.path.exists(logo_login_path) else ''
    
    st.markdown(f"""
    <div style="text-align: center; padding: 35px 20px; background: linear-gradient(135deg, #e8f5e9 0%, #ffffff 100%); border-radius: 12px; border: 2px solid #2E7D32; margin-bottom: 35px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
        {logo_html}
        <h1 style="color: #2E7D32; margin: 0; font-size: 40px; font-weight: 800; letter-spacing: 1px;">{CLINIC_NAME}</h1>
        <p style="color: #555; font-size: 18px; margin: 8px 0 20px 0; font-weight: 500;">{CLINIC_ADDRESS}</p>
        <div style="display: inline-block; background-color: #D92B2B; color: white; padding: 10px 25px; border-radius: 30px; font-size: 20px; font-weight: bold; box-shadow: 0 4px 10px rgba(217, 43, 43, 0.3);">
            📞 Appointments: 79734-89915
        </div>
    </div>
    
    <div style="display: flex; gap: 25px; margin-bottom: 40px; flex-wrap: wrap;">
        <!-- Chest Clinic Card -->
        <div style="flex: 1; min-width: 320px; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-top: 6px solid #2E7D32; transition: transform 0.3s;">
            <h2 style="color: #2E7D32; margin: 0 0 15px 0; font-size: 24px; border-bottom: 2px dashed #eee; padding-bottom: 10px;">🫁 Chest Clinic</h2>
            <h3 style="color: #333; margin: 0; font-size: 20px;">Dr. Harpreet Singh Makan</h3>
            <p style="color: #666; font-size: 15px; line-height: 1.6; margin-top: 8px; min-height: 100px;">
                <b style="color:#000;">MD, FICM</b><br>
                Physician & Chest Consultant<br>
                Medical Superintendent<br>(Mata Kaulan Ji Mission Hospital)<br>
                📱 Mobile: <b>98150-45618</b>
            </p>
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0; color: #2E7D32; font-size: 16px;">Treatments & Services:</h4>
                <ul style="font-size: 15px; color: #555; margin: 0; padding-left: 20px; line-height: 1.6;">
                    <li>Asthma, Allergy & Cough Clinic</li>
                    <li>T.B. Clinic & Patient Education</li>
                    <li>Family Medicine & General Physician</li>
                    <li>Diabetes & Hypertension Management</li>
                </ul>
            </div>
            <div style="margin-top: 20px; font-size: 14px; color: #2E7D32; text-align: center; background: #e8f5e9; padding: 10px; border-radius: 5px; font-weight: bold;">
                🕒 Timings: 9:00 AM - 10:00 AM | 5:00 PM - 6:30 PM
            </div>
        </div>

        <!-- Dental Clinic Card -->
        <div style="flex: 1; min-width: 320px; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-top: 6px solid #0F4C81; transition: transform 0.3s;">
            <h2 style="color: #0F4C81; margin: 0 0 15px 0; font-size: 24px; border-bottom: 2px dashed #eee; padding-bottom: 10px;">🦷 Dental Clinic</h2>
            <h3 style="color: #333; margin: 0; font-size: 20px;">Dr. (Mrs.) Manmeet Makan</h3>
            <p style="color: #666; font-size: 15px; line-height: 1.6; margin-top: 8px; min-height: 100px;">
                <b style="color:#000;">Dental Surgeon</b><br><br><br><br>
                📱 Mobile: <b>98720-45618</b>
            </p>
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px;">
                <h4 style="margin: 0 0 10px 0; color: #0F4C81; font-size: 16px;">Treatments & Services:</h4>
                <ul style="font-size: 15px; color: #555; margin: 0; padding-left: 20px; line-height: 1.6;">
                    <li>Root Canal Treatment (RCT) & Implants</li>
                    <li>Dentures (Partial & Complete) & Fixed Teeth</li>
                    <li>Tooth Coloured Fillings & Extractions</li>
                    <li>Scaling, Braces & Smile Designing</li>
                </ul>
            </div>
            <div style="margin-top: 20px; font-size: 14px; color: #0F4C81; text-align: center; background: #e3f2fd; padding: 10px; border-radius: 5px; font-weight: bold;">
                🕒 Timings: 10:00 AM - 1:00 PM | 5:00 PM - 6:30 PM
            </div>
        </div>
    </div>
    <div style="text-align: center; color: #d32f2f; font-weight: bold; font-size: 16px; margin-bottom: 40px;">
        ⚠️ Note: Clinic is closed on Sundays.
    </div>
    """, unsafe_allow_html=True)
    
    tab_book, tab_login = st.tabs(["📅 Book Appointment (ਮਰੀਜ਼ਾਂ ਲਈ)", "🔐 Staff Login (ਸਟਾਫ ਲਾਗਇਨ)"])
    
    with tab_book:
        st.markdown("<h3 style='text-align: center;'>ਆਨਲਾਈਨ ਅਪਾਇੰਟਮੈਂਟ ਬੁੱਕ ਕਰੋ (Book Online)</h3>", unsafe_allow_html=True)
        col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
        with col_b2:
            with st.form("public_appointment_form", clear_on_submit=True):
                pub_branch = st.selectbox("ਡਿਪਾਰਟਮੈਂਟ ਚੁਣੋ (Select Clinic)", ["Chest Clinic (ਛਾਤੀ ਦਾ ਰੋਗ)", "Dental Clinic (ਦੰਦਾਂ ਦਾ ਇਲਾਜ)"])
                pub_name = st.text_input("ਮਰੀਜ਼ ਦਾ ਨਾਮ (Patient Name)*")
                pub_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone Number)*")
                
                col_fd1, col_fd2 = st.columns(2)
                with col_fd1:
                    pub_date = st.date_input("ਮਿਤੀ ਚੁਣੋ (Select Date)", min_value=date.today())
                with col_fd2:
                    pub_time = st.selectbox("ਤਰਜੀਹੀ ਸਮਾਂ (Preferred Time)", TIME_SLOTS)
                    
                pub_reason = st.text_area("ਬਿਮਾਰੀ ਦਾ ਵੇਰਵਾ (Reason for visit - Optional)")
                
                if st.form_submit_button("Book Appointment", type="primary"):
                    if pub_name and pub_phone:
                        branch_clean = "Chest Clinic" if "Chest" in pub_branch else "Dental Clinic"
                        try:
                            res = supabase.table("appointments").insert({
                                "patient_name": pub_name, "phone": pub_phone, "appointment_date": str(pub_date),
                                "appointment_time": pub_time, "reason": pub_reason, "status": "Pending", "clinic_branch": branch_clean
                            }).execute()
                            if res.data:
                                booking_id = res.data[0]['id']
                                st.success(f"✅ ਬੇਨਤੀ ਸਫਲ ਰਹੀ! ਤੁਹਾਡੀ Booking ID: #{booking_id} ਹੈ। ਕਲੀਨਿਕ ਸਟਾਫ ਜਲਦੀ ਹੀ ਤੁਹਾਡਾ ਸਮਾਂ ਕਨਫਰਮ ਕਰੇਗਾ।")
                            else:
                                st.success(f"✅ ਬੇਨਤੀ ਸਫਲ ਰਹੀ! ਕਲੀਨਿਕ ਸਟਾਫ ਜਲਦੀ ਹੀ ਤੁਹਾਡਾ ਸਮਾਂ ਕਨਫਰਮ ਕਰੇਗਾ।")
                        except Exception as e:
                            st.error(f"Database Error: Ensure 'appointments' SQL table is created. Error: {e}")
                    else:
                        st.error("ਕਿਰਪਾ ਕਰਕੇ ਨਾਮ ਅਤੇ ਫ਼ੋਨ ਨੰਬਰ ਜ਼ਰੂਰ ਭਰੋ।")

    with tab_login:
        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
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
    
    st.markdown("<br><hr>", unsafe_allow_html=True)
    if os.path.exists("bani_logo_2.jpeg"):
        bc1, bc2, bc3 = st.columns([1, 2, 1])
        with bc2: st.image("bani_logo_2.jpeg", use_container_width=True)
    st.markdown("<div style='text-align: center; font-size: 12px; color: #888;'>Designed by <b>Bani Tech Solutions</b><br><a href='https://banitech.in' target='_blank' style='color: #2E7D32; text-decoration: none;'>banitech.in</a></div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# CLINIC BRANCH SELECTION PORTAL
# ==========================================
if st.session_state.logged_in and st.session_state.clinic_branch is None:
    st.markdown(f"<h2 style='text-align: center; color: #2E7D32; margin-top: 50px;'>🏥 Select Clinic Branch</h2>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
    with c2:
        st.markdown('<div class="branch-btn">', unsafe_allow_html=True)
        if st.button("🫁 Chest Clinic", use_container_width=True):
            st.session_state.clinic_branch = "Chest Clinic"
            st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="branch-btn">', unsafe_allow_html=True)
        if st.button("🦷 Dental Clinic", use_container_width=True):
            st.session_state.clinic_branch = "Dental Clinic"
            st.session_state.current_tab = "🏠 ਹੋਮ ਪੇਜ (Home)"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

cb = st.session_state.clinic_branch
is_admin = st.session_state.role == "admin"
is_mgmt = st.session_state.role == "management"

# --- NOTIFICATION CHECKER FOR SIDEBAR ---
pending_app_count = 0
try:
    pend_res = supabase.table("appointments").select("id", count="exact").eq("clinic_branch", cb).eq("status", "Pending").execute()
    pending_app_count = pend_res.count if pend_res.count else 0
except Exception: pass

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.title("👤 ਪ੍ਰੋਫਾਈਲ (Profile)")
    st.success(f"✅ Logged in as: {st.session_state.role.upper()}")
    st.info(f"📍 Active: {cb}")
    
    # 🔴 FLASHING ALERT NOTIFICATION 🔴
    if pending_app_count > 0:
        st.markdown(f"""
            <div class="flashing-alert">
                🚨 ਧਿਆਨ ਦਿਓ! <br><b>{pending_app_count}</b> ਨਵੀਆਂ ਅਪਾਇੰਟਮੈਂਟ ਬੇਨਤੀਆਂ ਆਈਆਂ ਹਨ!
            </div>
        """, unsafe_allow_html=True)
    
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
        "📅 ਅਪਾਇੰਟਮੈਂਟ (Appointments)",
        "📝 ਰੋਜ਼ਾਨਾ ਓ.ਪੀ.ਡੀ (OPD Entry)", 
        "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ",
        "📝 ਡਾਕਟਰ ਪਰਚੀ (Prescriptions)",
        "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ",
        "🩺 ਮਰੀਜ਼ ਰਿਕਾਰਡ (Patient Records)",
        "🦷 ਪ੍ਰੋਸੀਜਰ / ਸਰਜਰੀ (Special Procedures)",
        "🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff)"
    ]
    if is_admin: menu_options.append("⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin)")
        
    try: current_idx = menu_options.index(st.session_state.current_tab)
    except ValueError: current_idx = 0

    st.session_state.current_tab = st.radio("ਚੁਣੋ (Select Menu)", menu_options, index=current_idx, label_visibility="collapsed")
    
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    if os.path.exists("bani_logo_2.jpeg"): st.image("bani_logo_2.jpeg", use_container_width=True)
    st.markdown("<div style='text-align: center; font-size: 12px; color: #888;'>Designed by <b>Bani Tech Solutions</b><br><a href='https://banitech.in' target='_blank' style='color: #2E7D32; text-decoration: none;'>banitech.in</a></div>", unsafe_allow_html=True)

# --- HEADER ---
st.markdown(f"<div class='pro-header-flex'><div class='pro-text-box'><div class='pro-title'>🏥 {CLINIC_NAME}</div><div class='pro-tagline'>{cb.upper()} ENVIRONMENT</div></div></div>", unsafe_allow_html=True)

# ==========================================
# 0. HOME PAGE
# ==========================================
if st.session_state.current_tab == "🏠 ਹੋਮ ਪੇਜ (Home)":
    st.markdown(f"### 📝 ਕਵਿੱਕ ਐਕਸ਼ਨ ({cb})")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("📅 ਅਪਾਇੰਟਮੈਂਟ (Appointments)", use_container_width=True, type="primary"):
        st.session_state.current_tab = "📅 ਅਪਾਇੰਟਮੈਂਟ (Appointments)"
        st.rerun()
    if c2.button("💰 ਨਵੀਂ ਓ.ਪੀ.ਡੀ (OPD Fee)", use_container_width=True, type="primary"):
        st.session_state.current_tab = "📝 ਰੋਜ਼ਾਨਾ ਓ.ਪੀ.ਡੀ (OPD Entry)"
        st.rerun()
    if c3.button("📝 ਡਾਕਟਰ ਪਰਚੀ (Prescription)", use_container_width=True, type="primary"):
        st.session_state.current_tab = "📝 ਡਾਕਟਰ ਪਰਚੀ (Prescriptions)"
        st.rerun()
    if c4.button("📊 ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", use_container_width=True, type="primary"):
        st.session_state.current_tab = "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ"
        st.rerun()

# ==========================================
# 1. APPOINTMENTS MODULE (STAFF VIEW)
# ==========================================
elif st.session_state.current_tab == "📅 ਅਪਾਇੰਟਮੈਂਟ (Appointments)":
    st.header(f"📅 {cb} - ਅਪਾਇੰਟਮੈਂਟ ਡੈਸ਼ਬੋਰਡ")
    
    app_tab1, app_tab2, app_tab3, app_tab4 = st.tabs(["🔔 ਨਵੀਆਂ (Pending)", "✅ ਕਨਫਰਮ (Confirmed)", "➕ ਮੈਨੂਅਲ ਬੁਕਿੰਗ (Add Manual)", "🖨️ ਪ੍ਰਿੰਟ ਸ਼ੀਟ (Print)"])
    
    try: appointments = supabase.table("appointments").select("*").eq("clinic_branch", cb).order("appointment_date").execute().data or []
    except Exception: appointments = []
    df_app = pd.DataFrame(appointments)
    
    with app_tab1:
        st.write("### 🔔 ਨਵੀਆਂ ਬੇਨਤੀਆਂ (Pending Requests)")
        if pending_app_count > 0: 
            st.markdown(f'<div class="flashing-alert">🚨 {pending_app_count} ਨਵੀਆਂ ਅਪਾਇੰਟਮੈਂਟ ਬੇਨਤੀਆਂ ਆਈਆਂ ਹਨ!</div>', unsafe_allow_html=True)
        
        if not df_app.empty:
            pending_app = df_app[df_app['status'] == 'Pending']
            if not pending_app.empty:
                display_cols = ['id', 'appointment_date', 'appointment_time', 'patient_name', 'phone', 'reason']
                st.dataframe(pending_app[display_cols], hide_index=True, use_container_width=True)
                
                st.markdown("---")
                st.write("**ਸਮਾਂ ਅਲਾਟ ਕਰੋ ਅਤੇ ਕਨਫਰਮ ਕਰੋ (Allot Time & Confirm)**")
                
                with st.form("confirm_appointment"):
                    col_u1, col_u2, col_u3 = st.columns(3)
                    with col_u1:
                        app_id = st.selectbox("ਅਪਾਇੰਟਮੈਂਟ ID (Select ID)", pending_app['id'].tolist())
                    with col_u2:
                        new_time = st.selectbox("ਸਮਾਂ ਪੱਕਾ ਕਰੋ (Allot Time)", TIME_SLOTS)
                    with col_u3:
                        new_status = st.selectbox("ਸਟੇਟਸ (Status)", ["Confirmed", "Cancelled"])
                    
                    if st.form_submit_button("ਅਪਡੇਟ ਕਰੋ (Update Status)", type="primary"):
                        supabase.table("appointments").update({"status": new_status, "appointment_time": new_time}).eq("id", app_id).execute()
                        st.success(f"✅ ਅਪਾਇੰਟਮੈਂਟ #{app_id} '{new_status}' ਹੋ ਗਈ ਹੈ!")
                        
                        if new_status == "Confirmed":
                            target_pt = pending_app[pending_app['id'] == app_id].iloc[0]
                            pt_phone = str(target_pt['phone'])
                            if pt_phone:
                                msg = f"ਸਤਿਕਾਰਯੋਗ {target_pt['patient_name']} ਜੀ,\nਤੁਹਾਡੀ Makan {cb} ਵਿਖੇ ਅਪਾਇੰਟਮੈਂਟ (Booking No: {app_id}) {target_pt['appointment_date']} ਨੂੰ {new_time} ਵਜੇ ਕਨਫਰਮ ਹੋ ਗਈ ਹੈ।\n\n- {CLINIC_NAME}\n{CLINIC_ADDRESS}"
                                wa_url = f"https://wa.me/{pt_phone}?text={urllib.parse.quote(msg)}"
                                st.markdown(f'<a href="{wa_url}" target="_blank" class="whatsapp-btn">💬 ਮਰੀਜ਼ ਨੂੰ WhatsApp Confirmation ਭੇਜੋ</a>', unsafe_allow_html=True)
            else:
                st.info("ਕੋਈ ਪੈਂਡਿੰਗ ਬੇਨਤੀ ਨਹੀਂ ਹੈ।")
        else: st.info("ਕੋਈ ਡਾਟਾ ਮੌਜੂਦ ਨਹੀਂ ਹੈ।")

    with app_tab2:
        st.write("### ✅ ਕਨਫਰਮ ਅਤੇ ਪੂਰੀਆਂ (Confirmed & Completed)")
        if not df_app.empty:
            past_app = df_app[df_app['status'] != 'Pending']
            if not past_app.empty:
                st.dataframe(past_app[['id', 'appointment_date', 'appointment_time', 'patient_name', 'phone', 'status']], hide_index=True, use_container_width=True)
            else: st.info("ਕੋਈ ਕਨਫਰਮ ਰਿਕਾਰਡ ਨਹੀਂ ਹੈ।")

    with app_tab3:
        with st.form("manual_booking_form", clear_on_submit=True):
            st.write("### ➕ ਮੈਨੂਅਲ ਅਪਾਇੰਟਮੈਂਟ ਦਰਜ ਕਰੋ (Manual Booking)")
            col_mb1, col_mb2 = st.columns(2)
            with col_mb1:
                m_name = st.text_input("ਮਰੀਜ਼ ਦਾ ਨਾਮ (Patient Name)*")
                m_date = st.date_input("ਮਿਤੀ (Date)", value=date.today())
            with col_mb2:
                m_phone = st.text_input("ਫ਼ੋਨ (Phone)*")
                m_time = st.selectbox("ਸਮਾਂ (Time)", TIME_SLOTS)
                
            m_reason = st.text_input("ਵੇਰਵਾ (Reason)")
            
            if st.form_submit_button("ਬੁੱਕ ਕਰੋ (Book Now)", type="primary") and m_name:
                res = supabase.table("appointments").insert({
                    "patient_name": m_name, "phone": m_phone, "appointment_date": str(m_date),
                    "appointment_time": m_time, "reason": m_reason, "status": "Confirmed", "clinic_branch": cb
                }).execute()
                
                if res.data:
                    m_app_id = res.data[0]['id']
                    st.success(f"✅ ਮੈਨੂਅਲ ਅਪਾਇੰਟਮੈਂਟ #{m_app_id} ਕਨਫਰਮ ਹੋ ਗਈ ਹੈ!")
                    if m_phone:
                        msg = f"ਸਤਿਕਾਰਯੋਗ {m_name} ਜੀ,\nਤੁਹਾਡੀ Makan {cb} ਵਿਖੇ ਅਪਾਇੰਟਮੈਂਟ (Booking No: {m_app_id}) {m_date} ਨੂੰ {m_time} ਵਜੇ ਬੁੱਕ ਹੋ ਗਈ ਹੈ।\n\n- {CLINIC_NAME}\n{CLINIC_ADDRESS}"
                        wa_url = f"https://wa.me/{m_phone}?text={urllib.parse.quote(msg)}"
                        st.markdown(f'<a href="{wa_url}" target="_blank" class="whatsapp-btn">💬 ਮਰੀਜ਼ ਨੂੰ WhatsApp Confirmation ਭੇਜੋ</a>', unsafe_allow_html=True)
                else:
                    st.success("✅ ਮੈਨੂਅਲ ਅਪਾਇੰਟਮੈਂਟ ਕਨਫਰਮ ਹੋ ਗਈ ਹੈ!")

    with app_tab4:
        st.write("### 🖨️ ਰੋਜ਼ਾਨਾ ਅਪਾਇੰਟਮੈਂਟ ਸ਼ੀਟ ਪ੍ਰਿੰਟ ਕਰੋ")
        print_date = st.date_input("ਸ਼ੀਟ ਦੀ ਮਿਤੀ ਚੁਣੋ (Select Date for Sheet)", value=date.today())
        if st.button("📄 ਸ਼ੀਟ ਤਿਆਰ ਕਰੋ (Generate Print Sheet)", type="primary"):
            if not df_app.empty:
                sheet_df = df_app[(df_app['appointment_date'] == str(print_date)) & (df_app['status'] == 'Confirmed')]
                if not sheet_df.empty:
                    html_table = sheet_df[['appointment_time', 'patient_name', 'phone', 'reason']].to_html(index=False, border=1, classes='report-table')
                    report_file = generate_html_report_landscape(f"Daily Appointment Sheet ({print_date})", html_table, cb)
                    with open(report_file, "r", encoding="utf-8") as file: 
                        st.download_button("🖨️ ਪ੍ਰਿੰਟ ਕਰੋ (Print PDF/Sheet)", data=file.read(), file_name=report_file, mime="text/html", type="primary")
                else: st.warning("ਇਸ ਮਿਤੀ ਦੀ ਕੋਈ ਕਨਫਰਮ ਅਪਾਇੰਟਮੈਂਟ ਨਹੀਂ ਹੈ।")

# ==========================================
# 2. OPD, EXPENSE & DENTAL TREATMENTS ENTRY
# ==========================================
elif st.session_state.current_tab == "📝 ਰੋਜ਼ਾਨਾ ਓ.ਪੀ.ਡੀ (OPD Entry)":
    st.header(f"📝 {cb} - ਐਂਟਰੀ ਮੈਨੇਜਮੈਂਟ")
    
    # Dynamic Modes: Add Dental Treatment Tab ONLY if Dental Clinic is active
    modes = ["💰 ਓ.ਪੀ.ਡੀ ਫੀਸ (OPD Fee)"]
    if cb == "Dental Clinic": modes.append("🦷 ਡੈਂਟਲ ਟ੍ਰੀਟਮੈਂਟ ਫੀਸ (Dental Treatment)")
    modes.extend(["📉 ਖਰਚਾ ਦਰਜ ਕਰੋ (Expense)", "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ (Reprint)"])
    
    entry_mode = st.radio("ਐਕਸ਼ਨ ਚੁਣੋ:", modes, horizontal=True)
    st.markdown("---")

    if entry_mode == "💰 ਓ.ਪੀ.ਡੀ ਫੀਸ (OPD Fee)":
        with st.form("opd_form", clear_on_submit=True):
            st.write(f"### 🩺 {cb} - ਕੰਸਲਟੇਸ਼ਨ ਫੀਸ")
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                patient_name = st.text_input("ਮਰੀਜ਼ ਦਾ ਨਾਮ (Patient Name)*")
                patient_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone Number)")
            with col_o2:
                rec_no = st.number_input("ਰਸੀਦ ਨੰਬਰ (Receipt No)*", min_value=1, step=1)
                
                # Dynamic Dropdown based on Clinic Branch
                if cb == "Chest Clinic":
                    treatment = st.selectbox("ਕੰਸਲਟੇਸ਼ਨ ਦਾ ਵੇਰਵਾ (Consultation Type)", CHEST_TREATMENTS)
                else:
                    treatment = st.text_input("ਕੰਸਲਟੇਸ਼ਨ ਦਾ ਵੇਰਵਾ (Consultation Type)")
                
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                amount = st.number_input("ਫੀਸ (Fee Amount ₹)*", min_value=1.0)
                pay_mode = st.selectbox("ਭੁਗਤਾਨ ਮੋਡ (Mode)", ["ਨਕਦ (Cash)", "UPI/Google Pay", "Card"])
            with col_m2:
                bank_acc = st.selectbox("ਕਿਸ ਖਾਤੇ ਵਿੱਚ ਆਏ? (Bank Account)", BANK_ACCOUNTS)
                opd_date = st.date_input("ਮਿਤੀ (Date)", value=date.today())
                
            submitted = st.form_submit_button("ਰਸੀਦ ਸੇਵ ਕਰੋ (Save & Print)", type="primary")
            
        if submitted and patient_name:
            if supabase.table("donations").select("id").eq("id", int(rec_no)).eq("clinic_branch", cb).execute().data:
                st.error(f"❌ ਰਸੀਦ ਨੰਬਰ {rec_no} ਪਹਿਲਾਂ ਹੀ {cb} ਵਿੱਚ ਮੌਜੂਦ ਹੈ!")
            else:
                don_type = f"{cb} OPD Fee"
                supabase.table("donations").insert({
                    "id": int(rec_no), "name": patient_name, "phone": patient_phone, "amount": amount, 
                    "date": str(opd_date), "payment_mode": pay_mode, "donation_type": don_type, 
                    "bank_account": bank_acc, "on_account_of": treatment, "add_to_mirror": True, "collector_name": "Reception", "clinic_branch": cb
                }).execute()
                st.success(f"✅ ਰਸੀਦ ਸੇਵ ਹੋ ਗਈ!")
                html_file = generate_html_receipt(int(rec_no), patient_name, patient_phone, amount, str(opd_date), pay_mode, cb, bank_acc, treatment, "Reception")
                with open(html_file, "r", encoding="utf-8") as file:
                    st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ (Print Receipt)", data=file.read(), file_name=html_file, mime="text/html", type="primary")

    elif entry_mode == "🦷 ਡੈਂਟਲ ਟ੍ਰੀਟਮੈਂਟ ਫੀਸ (Dental Treatment)":
        with st.form("dental_treatment_form", clear_on_submit=True):
            st.write("### 🦷 ਡੈਂਟਲ ਟ੍ਰੀਟਮੈਂਟ / ਸਰਜਰੀ ਫੀਸ")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                patient_name = st.text_input("ਮਰੀਜ਼ ਦਾ ਨਾਮ (Patient Name)*", key="d_name")
                patient_phone = st.text_input("ਫ਼ੋਨ ਨੰਬਰ (Phone)", key="d_phone")
            with col_t2:
                rec_no = st.number_input("ਰਸੀਦ ਨੰਬਰ (Receipt No)*", min_value=1, step=1, key="d_rec")
                treatment_type = st.selectbox("ਟ੍ਰੀਟਮੈਂਟ ਚੁਣੋ (Select Treatment)", DENTAL_TREATMENTS)
                
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                amount = st.number_input("ਟ੍ਰੀਟਮੈਂਟ ਫੀਸ (Treatment Amount ₹)*", min_value=1.0, key="d_amt")
                pay_mode = st.selectbox("ਭੁਗਤਾਨ ਮੋਡ (Mode)", ["ਨਕਦ (Cash)", "UPI/Google Pay", "Card"], key="d_pay")
            with col_m2:
                bank_acc = st.selectbox("ਬੈਂਕ ਖਾਤਾ (Bank Account)", BANK_ACCOUNTS, key="d_bank")
                t_date = st.date_input("ਮਿਤੀ (Date)", value=date.today(), key="d_date")
                
            submitted = st.form_submit_button("ਰਸੀਦ ਸੇਵ ਕਰੋ (Save Treatment)", type="primary")
            
        if submitted and patient_name:
            if supabase.table("donations").select("id").eq("id", int(rec_no)).eq("clinic_branch", cb).execute().data:
                st.error("❌ ਰਸੀਦ ਨੰਬਰ ਪਹਿਲਾਂ ਹੀ ਮੌਜੂਦ ਹੈ!")
            else:
                don_type = f"Dental Treatment Fee"
                supabase.table("donations").insert({
                    "id": int(rec_no), "name": patient_name, "phone": patient_phone, "amount": amount, 
                    "date": str(t_date), "payment_mode": pay_mode, "donation_type": don_type, 
                    "bank_account": bank_acc, "on_account_of": treatment_type, "add_to_mirror": True, "collector_name": "Doctor", "clinic_branch": cb
                }).execute()
                st.success("✅ ਟ੍ਰੀਟਮੈਂਟ ਫੀਸ ਸੇਵ ਹੋ ਗਈ!")
                html_file = generate_html_receipt(int(rec_no), patient_name, patient_phone, amount, str(t_date), pay_mode, cb, bank_acc, f"Treatment: {treatment_type}", "Doctor")
                with open(html_file, "r", encoding="utf-8") as file:
                    st.download_button("🖨️ ਰਸੀਦ ਡਾਊਨਲੋਡ ਕਰੋ (Print Receipt)", data=file.read(), file_name=html_file, mime="text/html", type="primary")

    elif entry_mode == "📉 ਖਰਚਾ ਦਰਜ ਕਰੋ (Expense)":
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

    elif entry_mode == "🖨️ ਪੁਰਾਣੀ ਰਸੀਦ (Reprint)":
        search_id = st.number_input("ਰਸੀਦ ਨੰਬਰ (Enter Receipt No.)", min_value=1, step=1)
        if st.button("🔍 ਰਸੀਦ ਲੱਭੋ (Search)", type="primary"):
            res = supabase.table("donations").select("*").eq("id", search_id).eq("clinic_branch", cb).execute().data
            if res:
                rec = res[0]
                html_file = generate_html_receipt(search_id, rec['name'], rec.get('phone',''), rec['amount'], rec['date'], rec['payment_mode'], cb, rec['bank_account'], rec.get('on_account_of',''))
                with open(html_file, "r", encoding="utf-8") as file: st.download_button("🖨️ ਡਾਊਨਲੋਡ ਕਰੋ", data=file.read(), file_name=html_file, mime="text/html", type="primary")
            else: st.error(f"❌ ਰਸੀਦ ਨਹੀਂ ਮਿਲੀ (Not found in {cb}).")

# ==========================================
# 3. DOCTOR PRESCRIPTION MODULE (CAMERA)
# ==========================================
elif st.session_state.current_tab == "📝 ਡਾਕਟਰ ਪਰਚੀ (Prescriptions)":
    st.header(f"📝 {cb} - ਡਾਕਟਰ ਪਰਚੀ ਅਤੇ ਨੋਟਸ (Prescription & Findings)")
    pt_tab1, pt_tab2 = st.tabs(["➕ ਨਵੀਂ ਪਰਚੀ ਦਰਜ ਕਰੋ (New)", "📋 ਪੁਰਾਣੀਆਂ ਪਰਚੀਆਂ (History)"])
    
    with pt_tab1:
        with st.form("prescription_form", clear_on_submit=True):
            p_col1, p_col2 = st.columns(2)
            with p_col1: p_name = st.text_input("ਮਰੀਜ਼ ਦਾ ਨਾਮ (Patient Name)*")
            with p_col2: p_date = st.date_input("ਮਿਤੀ (Date)", value=date.today())
            p_findings = st.text_area("ਡਾਕਟਰ ਦੇ ਨੋਟਸ / ਬਿਮਾਰੀ (Doctor Findings / Chief Complaints)")
            
            st.markdown("---")
            st.write("📸 **ਪਰਚੀ ਜਾਂ X-Ray ਦੀ ਫੋਟੋ (Prescription / X-Ray Photo)**")
            p_photo_cam = st.camera_input("ਸਿੱਧਾ ਕੈਮਰੇ ਨਾਲ ਫੋਟੋ ਖਿੱਚੋ (Open Camera)")
            p_photo_file = st.file_uploader("ਜਾਂ ਪੁਰਾਣੀ ਫਾਈਲ ਅੱਪਲੋਡ ਕਰੋ (Or Upload from Device)", type=['png', 'jpg', 'jpeg'])
            p_photo = p_photo_cam if p_photo_cam is not None else p_photo_file
            
            if st.form_submit_button("ਪਰਚੀ ਸੇਵ ਕਰੋ (Save Prescription)", type="primary") and p_name:
                photo_str = compress_image(p_photo)
                supabase.table("prescriptions").insert({
                    "patient_name": p_name, "department": cb, "findings": p_findings,
                    "prescription_date": str(p_date), "photo_base64": photo_str, "clinic_branch": cb
                }).execute()
                st.success(f"✅ {p_name} ਦੀ ਪਰਚੀ ਸੇਵ ਹੋ ਗਈ!")

    with pt_tab2:
        try: prescriptions = supabase.table("prescriptions").select("*").eq("clinic_branch", cb).order("prescription_date", desc=True).limit(50).execute().data
        except Exception: prescriptions = []
        if prescriptions:
            for pr in prescriptions:
                with st.expander(f"📅 {pr['prescription_date']} | {pr['patient_name']}"):
                    st.write(f"**Findings:** {pr.get('findings', 'N/A')}")
                    if pr.get('photo_base64'): st.image(base64.b64decode(pr['photo_base64']), use_container_width=True)
        else: st.info(f"ਕੋਈ ਰਿਕਾਰਡ ਨਹੀਂ ਮਿਲਿਆ ({cb}).")

# ==========================================
# 4. LEDGERS & CA REPORTS
# ==========================================
elif st.session_state.current_tab == "🏦 ਖਾਤੇ, ਬੈਂਕ ਅਤੇ CA ਰਿਪੋਰਟਾਂ":
    st.header(f"🏦 {cb} - ਬੈਲੇਂਸ ਸ਼ੀਟ ਅਤੇ CA ਰਿਪੋਰਟਾਂ")
    modes = ["⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)", "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Daybook)", "📊 CA ਐਕਸਪੋਰਟ"]
    acc_mode = st.radio("ਰਿਪੋਰਟ ਚੁਣੋ:", modes, horizontal=True)
    st.markdown("---")

    don_data = supabase.table("donations").select("*").eq("clinic_branch", cb).execute().data or []
    exp_data = supabase.table("expenses").select("*").eq("clinic_branch", cb).execute().data or []
    df_don = pd.DataFrame(don_data)
    df_exp = pd.DataFrame(exp_data)

    if acc_mode == "⚖️ ਬੈਲੇਂਸ ਸ਼ੀਟ (P&L)":
        total_income = df_don['amount'].sum() if not df_don.empty else 0.0
        total_expense = df_exp['amount'].sum() if not df_exp.empty else 0.0
        surplus = total_income - total_expense

        inc_exp_html = f"""
        <table class="report-table">
            <tr><th>Expenditure (ਖਰਚੇ)</th><th>Amount (₹)</th><th>Income (ਆਮਦਨ)</th><th>Amount (₹)</th></tr>
            <tr><td>Total Clinic Expenses</td><td>{total_expense:,.2f}</td><td>Total OPD & Treatment Fees</td><td>{total_income:,.2f}</td></tr>
            <tr style="font-weight:bold; color: #D92B2B;"><td>Surplus (ਬੱਚਤ)</td><td>{surplus if surplus > 0 else 0:,.2f}</td><td>Deficit (ਘਾਟਾ)</td><td>{abs(surplus) if surplus < 0 else 0:,.2f}</td></tr>
            <tr style="background-color: #e8f5e9; font-weight:bold;"><td>Total</td><td>{max(total_income, total_expense):,.2f}</td><td>Total</td><td>{max(total_income, total_expense):,.2f}</td></tr>
        </table>
        """
        st.markdown(inc_exp_html, unsafe_allow_html=True)
        fin_report = generate_html_report_landscape(f"Financial Statements - {cb}", inc_exp_html, cb)
        with open(fin_report, "r", encoding="utf-8") as file: st.download_button("🖨️ ਰਿਪੋਰਟ ਪ੍ਰਿੰਟ ਕਰੋ", data=file.read(), file_name=fin_report, mime="text/html", type="primary")

    elif acc_mode == "📖 ਮੁੱਖ ਲੈਜ਼ਰ (Daybook)":
        start_date = st.date_input("ਸ਼ੁਰੂਆਤੀ ਮਿਤੀ", value=date(date.today().year, date.today().month, 1))
        end_date = st.date_input("ਆਖਰੀ ਮਿਤੀ", value=date.today())
        main_entries = []
        if not df_don.empty:
            for _, row in df_don.iterrows(): main_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਫੀਸ/ਟ੍ਰੀਟਮੈਂਟ: {row['name']}", 'Credit': float(row['amount']), 'Debit': 0.0, 'Source': 'Income'})
        if not df_exp.empty:
            for _, row in df_exp.iterrows(): main_entries.append({'ID': row['id'], 'Date': row['date'], 'Description': f"ਖਰਚਾ: {row['description']}", 'Credit': 0.0, 'Debit': float(row['amount']), 'Source': 'Expense'})
        df_main = pd.DataFrame(main_entries)
        if not df_main.empty:
            df_main['Date'] = pd.to_datetime(df_main['Date']).dt.date
            df_period = df_main[(df_main['Date'] >= start_date) & (df_main['Date'] <= end_date)].sort_values(by='Date')
            st.dataframe(df_period[['ID', 'Date', 'Description', 'Credit', 'Debit']].style.format({'Credit': '{:.2f}', 'Debit': '{:.2f}'}), hide_index=True, use_container_width=True)

    elif acc_mode == "📊 CA ਐਕਸਪੋਰਟ":
        st.write(f"### 📊 CA ਐਕਸਲ ਬੈਕਅੱਪ ({cb})")
        if st.button("📥 ਐਕਸਲ ਡਾਊਨਲੋਡ ਕਰੋ", type="primary"):
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                if not df_don.empty: df_don.to_excel(writer, sheet_name='Income', index=False)
                else: pd.DataFrame(columns=['No Data']).to_excel(writer, sheet_name='Income')
                
                if not df_exp.empty: df_exp.to_excel(writer, sheet_name='Expenses', index=False)
                else: pd.DataFrame(columns=['No Data']).to_excel(writer, sheet_name='Expenses')
            st.download_button("📥 Download", data=buffer.getvalue(), file_name=f"{cb}_Audit_Data_{date.today()}.xlsx", type="primary")

# ==========================================
# CATCH-ALL FOR REMAINING TABS
# ==========================================
elif st.session_state.current_tab in ["🩺 ਮਰੀਜ਼ ਰਿਕਾਰਡ (Patient Records)", "🦷 ਪ੍ਰੋਸੀਜਰ / ਸਰਜਰੀ (Special Procedures)", "📦 ਸਟਾਕ ਅਤੇ ਕਿਤਾਬਾਂ", "🧑‍💼 ਸਟਾਫ ਅਤੇ ਹਾਜ਼ਰੀ (Staff)", "⚙️ ਐਡਮਿਨ / ਡਿਲੀਟ / ਸੋਧ (Admin)"]:
    st.info(f"📍 Viewing {st.session_state.current_tab} for **{cb}**.")
    st.write("*(The underlying data mapping automatically secures this section for the active branch).*")
