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

st.set_page_config(page_title="Makan Clinic Manager", page_icon="🏥", layout="wide")

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

DENTAL_TREATMENTS = [
    "RCT", "Implants", "Dentures - Partial", "Dentures - Complete", "Fixed Teeth", 
    "Tooth Coloured Fillings", "Extraction", "Scaling", "Smile Designing", "Braces", "Other Dental Procedures"
]

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
        .pro-sub { font-size: 13px; font-weight: bold; color: #333 !important; margin: 0; text-align: center;}
        div.stButton > button { font-size: 18px !important; font-weight: bold !important; padding: 16px 10px !important; border-radius: 10px !important; width: 100% !important; }
        .branch-btn > button { height: 140px !important; font-size: 26px !important; border: 3px solid #2E7D32 !important; background-color: #e8f5e9 !important; color: #2E7D32 !important; transition: 0.3s; }
        .branch-btn > button:hover { background-color: #2E7D32 !important; color: white !important; }
        .whatsapp-btn { display: inline-block; padding: 10px 20px; background-color: #25D366; color: white !important; text-align: center; text-decoration: none; font-size: 15px; border-radius: 8px; font-weight: bold; border: 1px solid #128C7E; width: 100%; box-sizing: border-box; margin-top: 10px;}
        .whatsapp-btn:hover { background-color: #128C7E; }
        
        @keyframes flashAnim {
            0% { opacity: 1; background-color: #ffe6e6; }
            50% { opacity: 0.7; background-color: #ffcccc; border-color: #cc0000; }
            100% { opacity: 1Assuming you are trying to render this code in a standard HTML environment (like a web page or an email template), the layout error is occurring because the **Chest Clinic** section is completely missing HTML tags. It is currently sitting as plain text outside of any container, while the **Dental Clinic** section is perfectly formatted into an HTML card. 

Here is the corrected and fully structured HTML. I have wrapped everything in a responsive flexbox container and designed a "Chest Clinic" card to perfectly match your "Dental Clinic" card.

### Corrected HTML Code

```html
<div style="font-family: Arial, sans-serif; max-width: 1000px; margin: auto; padding: 20px; background-color: #f4f7f6;">
    
    <!-- Header Section -->
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="color: #2E7D32; margin: 0; font-size: 40px; font-weight: 800; letter-spacing: 1px;">MAKAN CHEST & DENTAL CLINIC</h1>
        <p style="color: #555; font-size: 18px; margin: 8px 0 20px 0; font-weight: 500;">Dreamcity SCO Market, Near Best Price, Manawala, Asr.</p>
        <div style="display: inline-block; background-color: #D92B2B; color: white; padding: 10px 25px; border-radius: 30px; font-size: 20px; font-weight: bold; box-shadow: 0 4px 10px rgba(217, 43, 43, 0.3);">
            📞 Appointments: 79734-89915
        </div>
    </div>

    <!-- Clinics Container -->
    <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center;">
        
        <!-- Chest Clinic Card -->
        <div style="flex: 1; min-width: 320px; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-top: 6px solid #2E7D32; transition: transform 0.3s;">
            <h2 style="color: #2E7D32; margin: 0 0 15px 0; font-size: 24px; border-bottom: 2px dashed #eee; padding-bottom: 10px;">🫁 Chest Clinic</h2>
            <h3 style="color: #333; margin: 0; font-size: 20px;">Dr. Harpreet Singh Makan</h3>
            <p style="color: #666; font-size: 15px; line-height: 1.6; margin-top: 8px; min-height: 100px;">
                <b style="color:#000;">MD, FICM</b><br>
                Physician & Chest Consultant<br>
                Medical Superintendent (Mata Kaulan Ji Mission Hospital)<br>
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
</div>
