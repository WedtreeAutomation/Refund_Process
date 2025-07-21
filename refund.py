import streamlit as st
import xmlrpc.client
from datetime import datetime, date
from itertools import combinations
import re
import logging
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# === Page Config ===
st.set_page_config(
    page_title="POS Refund Automation",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Enhanced Custom CSS ===
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    .branch-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .branch-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .branch-card:hover {
        border-color: #667eea;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.15);
        transform: translateY(-5px);
    }
    
    .branch-card:hover::before {
        transform: scaleX(1);
    }
    
    .branch-card h4 {
        color: #667eea;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.3rem;
    }
    
    .order-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .order-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(102, 126, 234, 0.05), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .order-card:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.1);
    }
    
    .order-card:hover::before {
        opacity: 1;
    }
    
    .success-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid #28a745;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(40, 167, 69, 0.1);
        animation: slideInFromLeft 0.5s ease-out;
    }
    
    @keyframes slideInFromLeft {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .error-card {
        background: linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%);
        border-left: 4px solid #dc3545;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(220, 53, 69, 0.1);
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 10s linear infinite;
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .metric-card:hover {
        transform: translateY(-10px) scale(1.05);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.4);
    }
    
    .metric-card h2, .metric-card h3 {
        position: relative;
        z-index: 1;
    }
    
    .metric-card h3 {
        font-size: 1rem;
        font-weight: 400;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .metric-card h2 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
        transition: all 0.3s ease;
        transform: translate(-50%, -50%);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 4px solid #ffc107;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(255, 193, 7, 0.2);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* Sidebar Enhancements */
    .sidebar .element-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Step Headers */
    .step-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .step-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .step-header:hover::before {
        left: 100%;
    }
    
    /* Enhanced Dataframe Styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: none;
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 1rem;
        text-align: center;
    }
    
    .dataframe td {
        padding: 0.75rem;
        text-align: center;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .dataframe tr:hover {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Connection Status */
    .connection-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(40, 167, 69, 0.2);
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Loading Spinner Enhancement */
    .stSpinner {
        border-color: #667eea;
    }
    
    /* Selectbox Enhancement */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Number Input Enhancement */
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Text Input Enhancement */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Checkbox Enhancement */
    .stCheckbox > label {
        background: white;
        padding: 0.75rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
        margin: 0.25rem 0;
    }
    
    .stCheckbox > label:hover {
        border-color: #667eea;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }
    
    /* Progress Bar Enhancement */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Info/Success/Error Message Enhancement */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header p {
            font-size: 1rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
        
        .metric-card h2 {
            font-size: 1.5rem;
        }
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Header with Animation
st.markdown("""
<div class="main-header">
    <h1>💳 POS Refund Automation System</h1>
    <p>Streamlined refund processing for multiple branches with intelligent order matching</p>
</div>
""", unsafe_allow_html=True)

# === Initialize Session State ===
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'models' not in st.session_state:
    st.session_state.models = None
if 'uid' not in st.session_state:
    st.session_state.uid = None
if 'all_orders' not in st.session_state:
    st.session_state.all_orders = []
if 'filtered_orders' not in st.session_state:
    st.session_state.filtered_orders = []
if 'selected_orders' not in st.session_state:
    st.session_state.selected_orders = []
if 'order_selections' not in st.session_state:
    st.session_state.order_selections = {}
if 'delete_ref_pos_reference' not in st.session_state:
    st.session_state.delete_ref_pos_reference = ""
if 'delete_any_pos_reference' not in st.session_state:
    st.session_state.delete_any_pos_reference = ""
if 'selected_branch' not in st.session_state:
    st.session_state.selected_branch = None
if 'user_authenticated' not in st.session_state:
    st.session_state.user_authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'user_code' not in st.session_state:
    st.session_state.user_code = ""
if 'current_session' in st.session_state:
    del st.session_state.current_session
if 'session_sequence' in st.session_state:
    del st.session_state.session_sequence

# === Environment Variables ===
@st.cache_data
def load_config():
    return {
        'url': os.getenv('ODOO_URL'),
        'db': os.getenv('ODOO_DB'),
        'username': os.getenv('ODOO_USERNAME'),
        'password': os.getenv('ODOO_PASSWORD'),
        'user_email': os.getenv('USER_EMAIL'),
        'user_code': os.getenv('USER_CODE')
    }

def authenticate_user(email, code):
    """Authenticate user with email and code"""
    config = load_config()
    return email == config['user_email'] and code == config['user_code']

# === Branch Configs ===
@st.cache_data
def get_branch_configs():
    return {
        "TN": {
            "source_configs": ["TN BILLING 1", "TN BILLING 2", "TN BILLING 3"],
            "target_config": "TN BILLING 4",
            "payment_method": "Cash 4",
            "company_id": 3
        },
        "CBE": {
            "source_configs": ["CB BILLING 1", "CB BILLING 2", "Local Expo CBE"],
            "target_config": "CB BILLING 3",
            "payment_method": "Cash 3",
            "company_id": 2
        },
        "VIZAG": {
            "source_configs": ["Vizag Billing 1", "Vizag Billing 2", "Local Expo VZG"],
            "target_config": "Vizag Billing 3",
            "payment_method": "Cash 3",
            "company_id": 4
        },
        "JAYANAGAR": {
            "source_configs": ["JYR Billing 1", "JYR Billing 2"],
            "target_config": "JYR Billing 3",
            "payment_method": "Cash 3",
            "company_id": 7
        },
        "HYDERABAD": {
            "source_configs": ["HYD BILLING - 1", "HYD BILLING - 2", "HYD BILLING - 3"],
            "target_config": "HYD BILLING - 4",
            "payment_method": "Cash 4",
            "company_id": 8
        },
        "MALLESWARAM": {
            "source_configs": ["MLM Billing 1", "MLM Billing 2"],
            "target_config": "MLM Billing 3",
            "payment_method": "Cash 3",
            "company_id": 6
        },
        "SAREE TRAILS": {
            "source_configs": ["PUNE 1", "PUNE 2", "PUNE 3", "PUNE 4", "PUNE 5", "PUNE 6", "PUNE 7", "PUNE 8", "PUNE 9", "PUNE 10", "PUNE 11", "PUNE 12", "PUNE 13", "PUNE 14", "PUNE 15"],
            "target_config": "PUNE 9",
            "payment_method": "Cash 9",
            "company_id": 5
        }
    }

# === Helper Functions ===
def get_pos_config(models, db, uid, password, name):
    ids = models.execute_kw(db, uid, password, 'pos.config', 'search', [[['name', '=', name]]])
    return models.execute_kw(db, uid, password, 'pos.config', 'read', [ids], {
        'fields': ['id', 'name', 'payment_method_ids', 'company_id']
    })[0] if ids else None

def get_payment_method_by_name_and_company(models, db, uid, password, name, company_id):
    ids = models.execute_kw(db, uid, password, 'pos.payment.method', 'search', [[
        ['name', '=', name], ['company_id', '=', company_id]
    ]])
    return models.execute_kw(db, uid, password, 'pos.payment.method', 'read', [ids])[0] if ids else None

def close_existing_sessions(models, db, uid, password, config_id):
    session_ids = models.execute_kw(db, uid, password, 'pos.session', 'search', [[
        ['config_id', '=', config_id], ['state', '!=', 'closed']
    ]])
    for session_id in session_ids:
        models.execute_kw(db, uid, password, 'pos.session', 'write', [[session_id], {'state': 'closing_control'}])
        models.execute_kw(db, uid, password, 'pos.session', 'close_session_from_ui', [[session_id]])

def generate_pos_reference(models, db, uid, password, session_name, config_id, order_index):
    """
    Generate pos_reference in format: {session_id_number}-001-{nth_refund_in_session:04d}
    The nth_refund is determined by counting how many refunds have already been created in this session.
    """
    # Extract session number
    session_id_number = None
    if "Session" in session_name:
        session_id_number = session_name.split()[-1]
    elif "/" in session_name:
        session_id_number = session_name.split("/")[-1]
    else:
        numbers = re.findall(r'\d+', session_name)
        if numbers:
            session_id_number = numbers[-1]
    
    if not session_id_number:
        raise ValueError(f"Could not extract session number from: {session_name}")

    # Count existing refund orders in the current session
    order_ids = models.execute_kw(db, uid, password, 'pos.order', 'search_read', [[
        ['session_id.name', '=', session_name],
        ['pos_reference', 'ilike', f"{session_id_number}-001-"]
    ]], {'fields': ['pos_reference'], 'order': 'id asc'})

    existing_refund_count = len(order_ids)
    nth_refund = existing_refund_count + 1

    return f"{int(session_id_number):05d}-001-{nth_refund:04d}"

# === Authentication ===
def authenticate():
    config = load_config()
    try:
        common = xmlrpc.client.ServerProxy(f"{config['url']}/xmlrpc/2/common")
        uid = common.authenticate(config['db'], config['username'], config['password'], {})
        if uid:
            models = xmlrpc.client.ServerProxy(f"{config['url']}/xmlrpc/2/object")
            st.session_state.authenticated = True
            st.session_state.models = models
            st.session_state.uid = uid
            st.session_state.config = config
            return True
        return False
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        return False

# === Delete Refund Function ===
def delete_any_order(pos_reference):
    if not pos_reference:
        st.error("Please enter a valid POS reference")
        return
    
    try:
        models = st.session_state.models
        uid = st.session_state.uid
        password = st.session_state.config['password']
        db = st.session_state.config['db']
        
        with st.spinner(f"Deleting refund with reference {pos_reference}..."):
            # Step 1: Search POS order
            order_ids = models.execute_kw(db, uid, password, 'pos.order', 'search', [[['pos_reference', '=', pos_reference]]])
            if not order_ids:
                st.error(f"No POS order found with reference '{pos_reference}'")
                return

            order_id = order_ids[0]
            st.info(f"Found POS Order ID: {order_id} with reference: {pos_reference}")

            # Step 2: Unlink payments
            payment_ids = models.execute_kw(db, uid, password, 'pos.payment', 'search', [[['pos_order_id', '=', order_id]]])
            if payment_ids:
                models.execute_kw(db, uid, password, 'pos.payment', 'unlink', [payment_ids])
                st.info(f"Deleted {len(payment_ids)} payment(s)")

            # Step 3: Force cancel the order (required before deletion)
            models.execute_kw(db, uid, password, 'pos.order', 'write', [[order_id], {'state': 'cancel'}])
            st.info("Order state set to 'cancel'")

            # Step 4: Now delete it
            models.execute_kw(db, uid, password, 'pos.order', 'unlink', [[order_id]])
            st.success(f"POS Order with reference '{pos_reference}' deleted successfully!")
            st.session_state.delete_ref_pos_reference = ""  # Clear input box
            
            # Instead of modifying session state, return a value that will trigger a rerun
            return True
            
    except Exception as e:
        st.error(f"Error deleting refund: {str(e)}")
        return False

def delete_refund_order(pos_reference):
    if not pos_reference:
        st.error("Please enter a valid POS reference")
        return False

    try:
        models = st.session_state.models
        uid = st.session_state.uid
        password = st.session_state.config['password']
        db = st.session_state.config['db']

        with st.spinner(f"Processing refund with reference {pos_reference}..."):

            # === Step 1: Find refund order by pos_reference ===
            refund_ids = models.execute_kw(db, uid, password, 'pos.order', 'search', [[['pos_reference', '=', pos_reference]]])
            if not refund_ids:
                st.error(f"No refund order found with reference '{pos_reference}'")
                return False

            refund_order = models.execute_kw(db, uid, password, 'pos.order', 'read', [refund_ids], {
                'fields': ['id', 'name', 'note', 'pos_reference']
            })[0]
            refund_order_id = refund_order['id']
            refund_name = refund_order['name']

            if not refund_name.endswith("REFUND"):
                st.warning("The order doesn't appear to be a refund (missing 'REFUND' in name). Skipping note cleanup.")
            else:
                # === Step 2: Find and clean note of original order ===
                original_name = refund_name.replace(" REFUND", "").strip()
                original_ids = models.execute_kw(db, uid, password, 'pos.order', 'search', [[['name', '=', original_name]]])

                if not original_ids:
                    st.warning(f"⚠️ Could not find original order with name '{original_name}'")
                else:
                    original_order = models.execute_kw(db, uid, password, 'pos.order', 'read', [original_ids], {'fields': ['id', 'note']})[0]
                    original_note = original_order.get('note') or ''
                    cleaned_lines = [line for line in original_note.split('\n') if 'REFUNDED' not in line.upper()]
                    cleaned_note = '\n'.join(cleaned_lines).strip()

                    if cleaned_note != original_note:
                        models.execute_kw(db, uid, password, 'pos.order', 'write', [[original_order['id']], {'note': cleaned_note}])
                        st.success(f"✅ Cleaned note in original order: {original_name}")
                    else:
                        st.info(f"ℹ️ Original order '{original_name}' note already clean.")

                # === Step 3: Clean refund order note as well ===
                refund_note = refund_order.get('note') or ''
                cleaned_refund_note = "\n".join([line for line in refund_note.split("\n") if 'REFUNDED' not in line.upper()]).strip()

                if cleaned_refund_note != refund_note:
                    models.execute_kw(db, uid, password, 'pos.order', 'write', [[refund_order_id], {'note': cleaned_refund_note}])
                    st.success(f"✅ Cleaned note in refund order: {refund_name}")
                else:
                    st.info(f"ℹ️ Refund order '{refund_name}' note already clean.")

            # === Step 4: Unlink refund order payments ===
            payment_ids = models.execute_kw(db, uid, password, 'pos.payment', 'search', [[['pos_order_id', '=', refund_order_id]]])
            if payment_ids:
                models.execute_kw(db, uid, password, 'pos.payment', 'unlink', [payment_ids])
                st.info(f"🗑️ Deleted {len(payment_ids)} payment(s) from refund order")

            # === Step 5: Cancel and delete refund order ===
            models.execute_kw(db, uid, password, 'pos.order', 'write', [[refund_order_id], {'state': 'cancel'}])
            models.execute_kw(db, uid, password, 'pos.order', 'unlink', [[refund_order_id]])
            st.success(f"🗑️ Deleted refund order: {refund_name}")
            st.session_state.delete_ref_pos_reference = ""  # Clear input box
            return True

    except Exception as e:
        st.error(f"❌ Error deleting refund order: {str(e)}")
        return False

# === Main App ===
def main():
    # Sidebar
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔐 User Authentication")
        if not st.session_state.user_authenticated:
            with st.form("login_form"):
                st.markdown("**Enter your credentials:**")
                email = st.text_input("Email", placeholder="user@example.com")
                code = st.text_input("Access Code", type="password", placeholder="Enter access code")
                
                if st.form_submit_button("🔓 Login", use_container_width=True):
                    if authenticate_user(email, code):
                        st.session_state.user_authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_code = code
                        st.success("✅ User authenticated!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials!")
        else:
            st.success(f"✅ Welcome, {st.session_state.user_email}")
            if st.button("🔓 Logout", use_container_width=True):
                st.session_state.user_authenticated = False
                st.session_state.authenticated = False
                st.session_state.models = None
                st.session_state.uid = None
                st.rerun()
        
        if st.session_state.user_authenticated:
            st.markdown("---")
            st.markdown("### 🔐 Odoo Connection")
            if not st.session_state.authenticated:
                if st.button("🔌 Connect to Odoo", use_container_width=True):
                    with st.spinner("Connecting to Odoo..."):
                        if authenticate():
                            st.success("✅ Connected successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Connection failed!")
            else:
                st.success("✅ Connected to Odoo")
                if st.button("🔌 Disconnect", use_container_width=True):
                    st.session_state.authenticated = False
                    st.session_state.models = None
                    st.session_state.uid = None
                    st.rerun()
            
            # Delete Refund Section
            if st.session_state.authenticated:
                st.markdown("---")
                st.markdown("### 🗑️ Delete Any Order")
                
                # Second text input for any orders
                any_pos_reference = st.text_input(
                    "Enter any POS Reference to delete",
                    key="delete_any_pos_reference",
                    value=st.session_state.get("delete_any_pos_reference", "")
                )
                if st.button("❌ Delete Any Order", use_container_width=True):
                    if delete_any_order(any_pos_reference):
                        st.rerun()

                st.markdown("---")
                st.markdown("### 🗑️ Delete Refund Order")
                
                # First text input for refund orders
                refund_pos_reference = st.text_input(
                    "Enter POS Reference to delete (Refund)",
                    key="delete_ref_pos_reference",
                    value=st.session_state.get("delete_ref_pos_reference", "")
                )
                if st.button("❌ Delete Refund", use_container_width=True):
                    if delete_refund_order(refund_pos_reference):
                        st.rerun()

    # Main content
    if not st.session_state.user_authenticated:
        st.info("👆 Please authenticate using the sidebar to get started.")
        
        # Show branch information
        st.markdown("### 🏢 Available Branches")
        branch_configs = get_branch_configs()
        
        cols = st.columns(3)
        for i, (branch, config) in enumerate(branch_configs.items()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="branch-card">
                    <h4>{branch}</h4>
                    <p><strong>Source:</strong> {len(config['source_configs'])} configs</p>
                    <p><strong>Target:</strong> {config['target_config']}</p>
                    <p><strong>Payment:</strong> {config['payment_method']}</p>
                </div>
                """, unsafe_allow_html=True)
        return

    if not st.session_state.authenticated:
        st.info("👆 Please connect to Odoo using the sidebar to get started.")
        return

    # Connected - Show main interface
    st.markdown("### 🎯 Step 1: Select Branch & Date")
    
    col1, col2 = st.columns(2)
    
    with col1:
        branch_configs = get_branch_configs()
        selected_branch = st.selectbox(
            "Select Branch",
            options=list(branch_configs.keys()),
            format_func=lambda x: f"🏢 {x}",
            key="branch_select"
        )
        
        # Clear data if branch changed
        if st.session_state.selected_branch != selected_branch:
            st.session_state.all_orders = []
            st.session_state.filtered_orders = []
            st.session_state.selected_orders = []
            st.session_state.selected_branch = selected_branch
        
    with col2:
        today = date.today()
        col2a, col2b = st.columns(2)
        with col2a:
            start_date = st.date_input(
                "Start Date",
                value=today,
                max_value=today,
                key="start_date_select"
            )
        with col2b:
            end_date = st.date_input(
                "End Date",
                value=today,
                max_value=today,
                key="end_date_select"
            )
        
        if start_date > end_date:
            st.error("Start date must be before or equal to end date")

    if st.button("🔍 Load Orders", use_container_width=True):
        if start_date <= end_date:
            load_orders(selected_branch, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        else:
            st.error("Please select a valid date range")

    if st.session_state.all_orders:
        st.markdown("### 📋 Step 2: Loaded Orders")
        
        # Display all loaded orders first
        df_all = pd.DataFrame(st.session_state.all_orders)
        df_all_display = df_all[['pos_reference', 'amount_total', 'config_name', 'payment_methods']].copy()
        df_all_display.columns = ['Reference', 'Amount (₹)', 'Config', 'Payment Methods']
        df_all_display.index = df_all_display.index + 1
        st.dataframe(df_all_display, use_container_width=True)
        
        # Show summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Orders", len(st.session_state.all_orders))
        with col2:
            st.metric("Total Amount", f"₹{sum(order['amount_total'] for order in st.session_state.all_orders):,.2f}")
        with col3:
            st.metric("Average Amount", f"₹{sum(order['amount_total'] for order in st.session_state.all_orders) / len(st.session_state.all_orders):,.2f}")
        
        st.markdown("### 💰 Step 3: Filter Orders by Amount")
        
        col1, col2 = st.columns(2)
        with col1:
            min_amount = st.number_input("Minimum Amount (₹)", min_value=0.0, value=0.0, step=100.0)
        with col2:
            max_amount = st.number_input("Maximum Amount (₹)", min_value=0.0, value=10000.0, step=100.0)
        
        if st.button("🔽 Filter Orders", use_container_width=True):
            filter_orders(min_amount, max_amount)
    
    if st.session_state.filtered_orders:
        st.markdown("### 🔍 Step 4: Filtered Orders")
        
        # Display filtered orders in a nice table
        df = pd.DataFrame(st.session_state.filtered_orders)
        df_display = df[['pos_reference', 'amount_total', 'config_name', 'payment_methods']].copy()
        df_display.columns = ['Reference', 'Amount (₹)', 'Config', 'Payment Methods']
        
        st.dataframe(df_display, use_container_width=True)
        
        # Show filtered summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Filtered Orders", len(st.session_state.filtered_orders))
        with col2:
            st.metric("Total Amount", f"₹{sum(order['amount_total'] for order in st.session_state.filtered_orders):,.2f}")
        with col3:
            st.metric("Average Amount", f"₹{sum(order['amount_total'] for order in st.session_state.filtered_orders) / len(st.session_state.filtered_orders):,.2f}")
        
        st.markdown("### 🎯 Step 5: Find Best Refund Combination")
        
        col1, col2 = st.columns(2)
        with col1:
            refund_target = st.number_input("Target Refund Amount (₹)", min_value=0.0, step=100.0)
        with col2:
            if st.button("🔍 Find Best Match", use_container_width=True):
                find_best_combination(refund_target)

    if st.session_state.selected_orders:
        st.markdown("### ✅ Step 6: Select Orders for Refund")
        
        # Reset order selections
        st.session_state.order_selections = {}
        
        # Display checkboxes for each selected order
        for order in st.session_state.selected_orders:
            checkbox_key = f"order_select_{order['pos_reference']}"
            st.session_state.order_selections[checkbox_key] = st.checkbox(
                f"{order['pos_reference']} | ₹{order['amount_total']:,.2f} | {order['config_name']}",
                value=True,
                key=checkbox_key
            )
        
        # Calculate selected amounts
        selected_orders = [
            order for order in st.session_state.selected_orders 
            if st.session_state.order_selections.get(f"order_select_{order['pos_reference']}", False)
        ]
        
        if selected_orders:
            total_amount = sum(order['amount_total'] for order in selected_orders)
            
            # Show metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Target Amount</h3>
                    <h2>₹{refund_target:,.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Match Amount</h3>
                    <h2>₹{total_amount:,.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Difference</h3>
                    <h2>₹{abs(refund_target - total_amount):,.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Show selected orders
            st.markdown("**Selected Orders:**")
            for order in selected_orders:
                st.markdown(f"""
                <div class="order-card">
                    <strong>{order['pos_reference']}</strong> | ₹{order['amount_total']:,.2f} | {order['config_name']} | {order['payment_methods']}
                </div>
                """, unsafe_allow_html=True)
            
            # Confirmation
            st.markdown("### 🚀 Step 7: Process Refund")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Process Refund", type="primary", use_container_width=True):
                    st.session_state.selected_orders = selected_orders
                    process_refund(selected_branch)
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.selected_orders = []
                    st.rerun()

def load_orders(branch, start_date, end_date):
    """Load orders for the selected branch and date range"""
    with st.spinner("Loading orders..."):
        try:
            branch_configs = get_branch_configs()
            cfg = branch_configs[branch]
            source_configs = cfg['source_configs']
            
            models = st.session_state.models
            uid = st.session_state.uid
            password = st.session_state.config['password']
            db = st.session_state.config['db']
            
            # Get only Cash payment method IDs
            cash_methods = models.execute_kw(db, uid, password, 'pos.payment.method', 'search_read', 
                [[['name', 'ilike', 'Cash']]], 
                {'fields': ['id']}
            )
            cash_ids = [m['id'] for m in cash_methods]
            
            if not cash_ids:
                st.error("No Cash payment methods found")
                return
                
            all_orders = []
            
            for config_name in source_configs:
                config = get_pos_config(models, db, uid, password, config_name)
                if not config:
                    continue
                    
                order_ids = models.execute_kw(db, uid, password, 'pos.order', 'search', [[
                    ['config_id', '=', config['id']],
                    ['payment_ids.payment_method_id', 'in', cash_ids],
                    ['state', '=', 'done'],
                    ['date_order', '>=', f"{start_date} 00:00:00"],
                    ['date_order', '<=', f"{end_date} 23:59:59"],
                    ['note', 'not ilike', 'REFUNDED']
                ]])
                
                orders = models.execute_kw(db, uid, password, 'pos.order', 'read', [order_ids], {
                    'fields': ['id', 'name', 'pos_reference', 'amount_total', 'config_id', 'payment_ids', 'note']
                })
                
                for order in orders:
                    # Verify all payments are cash (not mixed with customer account/bank)
                    payment_lines = models.execute_kw(db, uid, password, 'pos.payment', 'search_read', 
                        [[['pos_order_id', '=', order['id']]]], 
                        {'fields': ['payment_method_id', 'amount']}
                    )
                    
                    # Check if all payments are cash
                    all_cash = all(p['payment_method_id'][0] in cash_ids for p in payment_lines)
                    if not all_cash:
                        continue
                        
                    config_data = models.execute_kw(db, uid, password, 'pos.config', 'read', [[order['config_id'][0]]], {'fields': ['name']})[0]
                    payment_methods = ", ".join(p['payment_method_id'][1] for p in payment_lines)
                    order['config_name'] = config_data['name']
                    order['payment_methods'] = payment_methods
                    all_orders.append(order)
            
            st.session_state.all_orders = all_orders
            st.success(f"✅ Loaded {len(all_orders)} cash orders for {branch} from {start_date} to {end_date}")
            
        except Exception as e:
            st.error(f"❌ Error loading orders: {str(e)}")

def filter_orders(min_amt, max_amt):
    """Filter orders by amount range"""
    filtered = [o for o in st.session_state.all_orders if min_amt <= o['amount_total'] <= max_amt]
    st.session_state.filtered_orders = filtered
    st.success(f"✅ Filtered to {len(filtered)} orders in range ₹{min_amt:,.2f} - ₹{max_amt:,.2f}")

def find_best_combination(refund_target):
    """Fast greedy approach to find best combination close to target"""
    with st.spinner("Finding best combination..."):
        orders = sorted(st.session_state.filtered_orders, key=lambda x: x['amount_total'], reverse=True)

        best_combo = []
        current_total = 0.0

        for order in orders:
            if current_total + order['amount_total'] <= refund_target:
                best_combo.append(order)
                current_total += order['amount_total']
                if abs(current_total - refund_target) < 1e-2:  # Allow small float difference
                    break

        if best_combo:
            st.session_state.selected_orders = best_combo
            st.success(f"✅ Found best combination with {len(best_combo)} orders (Total ₹{current_total:,.2f})")
        else:
            st.error("❌ No suitable combination found")

def process_refund(branch):
    """Process the refund for selected orders"""
    with st.spinner("Processing refund..."):
        try:
            branch_configs = get_branch_configs()
            cfg = branch_configs[branch]
            target_config_name = cfg['target_config']
            payment_method_name = cfg['payment_method']
            company_id = cfg['company_id']
            
            models = st.session_state.models
            uid = st.session_state.uid
            password = st.session_state.config['password']
            db = st.session_state.config['db']
            
            # Get target config and payment method
            target_config = get_pos_config(models, db, uid, password, target_config_name)
            payment_method = get_payment_method_by_name_and_company(models, db, uid, password, payment_method_name, company_id)
            
            if not payment_method:
                st.error("❌ Payment method not found")
                return
            
            # Close any existing sessions
            close_existing_sessions(models, db, uid, password, target_config['id'])

            # Ensure payment method is attached to the POS config
            if payment_method['id'] not in target_config['payment_method_ids']:
                models.execute_kw(db, uid, password, 'pos.config', 'write', [[target_config['id']], {
                    'payment_method_ids': [(4, payment_method['id'])]
                }])
            
            # Create and open a new session
            session_id = models.execute_kw(db, uid, password, 'pos.session', 'create', [{'config_id': target_config['id']}])
            models.execute_kw(db, uid, password, 'pos.session', 'write', [[session_id], {'state': 'opened'}])
            session_name = models.execute_kw(db, uid, password, 'pos.session', 'read', [[session_id]], {'fields': ['name']})[0]['name']
            
            refund_details = []
            
            for index, selected_order in enumerate(st.session_state.selected_orders):
                # Read original order details
                original = models.execute_kw(db, uid, password, 'pos.order', 'read', [[selected_order['id']]], {'fields': ['lines', 'partner_id', 'name']})[0]
                order_lines = models.execute_kw(db, uid, password, 'pos.order.line', 'read', [original['lines']], {
                    'fields': ['product_id', 'qty', 'price_unit', 'discount', 'full_product_name', 'pack_lot_ids']
                })
                
                refund_lines = []
                total = 0.0
                
                # Build refund lines (negative quantities)
                for line in order_lines:
                    qty = -line['qty']
                    price = line['price_unit']
                    discount = line.get('discount', 0)
                    subtotal = qty * price * (1 - discount/100)
                    refund_lines.append((0, 0, {
                        'product_id': line['product_id'][0],
                        'qty': qty,
                        'price_unit': price,
                        'discount': discount,
                        'price_subtotal': subtotal,
                        'price_subtotal_incl': subtotal,
                        'full_product_name': line.get('full_product_name', ''),
                        'pack_lot_ids': [(6, 0, line.get('pack_lot_ids', []))]
                    }))
                    total += subtotal
                
                # Get original config (for pos_reference format)
                original_config = get_pos_config(models, db, uid, password, selected_order['config_name'])
                pos_reference = generate_pos_reference(models, db, uid, password, session_name, original_config['id'], index)
                
                refund_name = f"{original['name']} REFUND"
                
                refund_vals = {
                    'name': refund_name,
                    'pos_reference': f"Order {pos_reference}",
                    'config_id': target_config['id'],
                    'session_id': session_id,
                    'partner_id': original['partner_id'][0] if original['partner_id'] else False,
                    'lines': refund_lines,
                    'payment_ids': [(0, 0, {
                        'amount': total,
                        'payment_method_id': payment_method['id']
                    })],
                    'amount_paid': total,
                    'amount_total': total,
                    'amount_tax': 0.0,
                    'amount_return': 0.0,
                    'state': 'done'
                }
                
                refund_order_id = models.execute_kw(db, uid, password, 'pos.order', 'create', [refund_vals])
                refund_details.append({
                    'name': refund_name,
                    'reference': pos_reference,
                    'amount': total
                })
                
                # Update original order note
                note_append = f"[REFUNDED to {refund_name} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
                updated_note = (selected_order.get('note') or '') + ' ' + note_append
                models.execute_kw(db, uid, password, 'pos.order', 'write', [[selected_order['id']], {'note': updated_note}])
                # Also write the note into the refund order
                models.execute_kw(db, uid, password, 'pos.order', 'write', [[refund_order_id], {'note': note_append}])

            # Close refund session
            models.execute_kw(db, uid, password, 'pos.session', 'write', [[session_id], {'state': 'closing_control'}])
            models.execute_kw(db, uid, password, 'pos.session', 'close_session_from_ui', [[session_id]])
            
            # UI output
            st.success("🎉 Refund processed successfully!")
            for detail in refund_details:
                st.markdown(f"""
                <div class="success-card">
                    <strong>✅ Refund Created:</strong> {detail['name']} | Receipt: {detail['reference']} | Amount: ₹{detail['amount']:,.2f}
                </div>
                """, unsafe_allow_html=True)
            
            st.info(f"🔒 Refund session closed for {target_config_name}")
            
            # Clear selections after processing
            st.session_state.selected_orders = []
            st.session_state.filtered_orders = []
            st.session_state.all_orders = []
        
        except Exception as e:
            st.error(f"❌ Error processing refund: {str(e)}")

if __name__ == "__main__":
    main()
