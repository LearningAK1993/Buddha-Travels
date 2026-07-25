"""
Buddha Travel and Tours — Sales Activity Log
A simple Streamlit form for staff to log Daily Summary and Enquiry entries.
Both are sent to a Google Apps Script Web App endpoint, which appends them
as rows into a Google Sheet (Daily Summary / Enquiry Log tabs). This means
data persists permanently in the Sheet, with no reset risk from Streamlit's
free-tier storage.
"""

import streamlit as st
import requests
import base64
from pathlib import Path
from datetime import date, datetime

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
# Your Apps Script Web App URL (from Deploy > New deployment > Web app)
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyU67VAnI40-kERKwLHLhw-dcoX6QIe03G9cqvHDN_UtCF6bRe_FkgfWzyG0zM3ttMZ/exec"

DAILY_SUMMARY_HEADERS = [
    "Date",
    "Staff Name",
    "PNRs Generated Today",
    "Total Calls Received Today",
    "Total Emails Sent to Clients Today",
    "Total Enquiries Received & Logged in Zooma Today",
    "Total Callbacks Made Today (across all enquiries)",
    "Daily Tasks Planned / Noted for Today",
    "Tips/Tricks Applied for Price-Matching Objections",
    "Management Briefing Tips Applied Today?",
    "If Yes — Which Tips Applied",
    "Preferred Communication Method",
    "Client Feedback Received Today (if any)",
    "Services/Products Promoted Today",
    "Submitted At",
]

ENQUIRY_LOG_HEADERS = [
    "Date",
    "Staff Name",
    "Enquiry / Zooma Ref ID",
    "Client Name",
    "Date Enquiry Originally Received",
    "Enquiry Source / Channel",
    "Price/Options Offered?",
    "Price/Options Offered — Details",
    "Communication Method Used",
    "No. of Follow-Ups / Callbacks for This Enquiry",
    "Coordinated with a Teammate?",
    "Teammate Name (if Yes)",
    "Outcome",
    "Reason if Not Converted",
    "Notes",
    "Submitted At",
]

STAFF_NAMES = ["Please Select", "Kabita SYD", "Shreekantha KTM", "Prasant KTM", "Bishnu NP", "Nisha NP", "Bal Gopal MEL", "Prazol MEL", "Ram Hari NP", "Sabin NP", "Krishna SYD", "Srijana NP", "Uttam NP", "Mahendra NZ"]
COMMS_METHODS = ["WhatsApp", "SMS/Text", "Viber", "Phone Call", "Email"]
CHANNELS = ["Website Form", "Live Chat", "Facebook", "Instagram", "Phone", "Walk-in", "Referral", "Other"]
OUTCOMES = ["Quoted", "Booked (PNR generated)", "Lost", "Pending", "No Response"]
REASONS = [
    "Not Applicable / Converted",
    "Price / Lost on Fare",
    "Availability",
    "Client Still Deciding",
    "No Response from Client",
    "Went to Competitor",
    "Other",
]

# ---------------------------------------------------------------------------
# APPS SCRIPT HELPER
# ---------------------------------------------------------------------------

def send_row(sheet_name: str, row_values: list):
    """Send one row to the Google Sheet via the Apps Script Web App endpoint."""
    try:
        response = requests.post(
            APPS_SCRIPT_URL,
            json={"sheet": sheet_name, "row": row_values},
            timeout=15,
        )
        result = response.json()
        if result.get("success"):
            return True, None
        else:
            return False, result.get("error", "Unknown error from Apps Script.")
    except requests.exceptions.Timeout:
        return False, "The request timed out — please check your connection and try again."
    except Exception as e:
        return False, f"Something went wrong sending your entry: {e}"


# ---------------------------------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------------------------------

LOGO_PATH = Path(__file__).parent / "assets" / "logo.jpg"


def _logo_data_uri():
    if LOGO_PATH.exists():
        encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode()
        return f"data:image/jpeg;base64,{encoded}"
    return None


st.set_page_config(page_title="Buddha Travel — Sales Activity Log", page_icon="🌍", layout="centered")

# Brand styling — thin borders, soft layered shadows, generous spacing.
# Colors mostly come from .streamlit/config.toml so buttons, focus rings,
# radios and the selected tab all share one accent automatically.
st.markdown(
    """
    <style>
    .block-container {
        max-width: 960px;
        padding-top: 2.5rem;
    }
    div.stButton > button, .stFormSubmitButton > button {
        border-radius: 8px;
        padding: 0.55rem 1.75rem;
        font-weight: 600;
        border: 1px solid transparent;
        transition: filter 0.15s ease, box-shadow 0.15s ease;
    }
    div.stButton > button:hover, .stFormSubmitButton > button:hover {
        filter: brightness(0.94);
    }
    div.stButton > button:focus-visible, .stFormSubmitButton > button:focus-visible {
        outline: 2px solid #1a7db3;
        outline-offset: 2px;
    }
    div.stButton > button:disabled, .stFormSubmitButton > button:disabled {
        filter: grayscale(0.4) opacity(0.6);
    }

    [data-testid="stForm"] {
        border: 1px solid #e5e9ed;
        border-radius: 12px;
        padding: 1.75rem 1.75rem 1.25rem;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
    }

    [data-testid="stExpander"] {
        border: 1px solid #e5e9ed;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid #e5e9ed;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        color: #6b7280;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 2px solid #1a7db3;
        font-weight: 600;
        color: #1a7db3 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Branded header — asymmetric layout with a functional accent bar rather
# than a centered, symmetric block.
_logo_uri = _logo_data_uri()
_logo_html = f'<img src="{_logo_uri}" style="height:48px; margin-right:20px;" />' if _logo_uri else ""
st.markdown(
    f"""
    <div style="display:flex; align-items:center; background:##FFFFFF;
                padding:28px 32px; border-radius:10px; margin-bottom:32px;
                border:1px solid #e5e9ed; border-left:4px solid #1a7db3;
                box-shadow:0 1px 2px rgba(16,24,40,0.04), 0 4px 12px rgba(16,24,40,0.03);">
        {_logo_html}
        <div>
            <h2 style="color:#1f2937; margin:0; font-size:1.35rem; font-weight:700;">Buddha Travel and Tours</h2>
            <p style="color:#6b7280; margin:4px 0 0 0; font-size:0.9rem;">Sales Activity Log</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["🧳 Daily Summary", "✈️ Enquiry Log"])

# ---------------------------------------------------------------------------
# DAILY SUMMARY FORM
# ---------------------------------------------------------------------------
with tab1:
    with st.form("daily_summary_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            entry_date = st.date_input("Date", value=date.today())
        with col2:
            staff_name = st.selectbox("Staff Name", STAFF_NAMES)

        num_col1, num_col2, num_col3 = st.columns(3)
        with num_col1:
            pnrs = st.number_input("PNRs Generated Today", min_value=0, step=1)
        with num_col2:
            calls = st.number_input("Total Calls Received Today", min_value=0, step=1)
        with num_col3:
            emails = st.number_input("Total Emails Sent to Clients Today", min_value=0, step=1)

        num_col4, num_col5 = st.columns(2)
        with num_col4:
            enquiries_logged = st.number_input("Total Enquiries Received & Logged in Zooma Today", min_value=0, step=1)
        with num_col5:
            callbacks = st.number_input("Total Callbacks Made Today (across all enquiries)", min_value=0, step=1)

        tasks = st.text_area("Daily Tasks Planned / Noted for Today")
        price_tips = st.text_area("Tips/Tricks Applied for Price-Matching Objections (optional)")

        tips_col, comms_col = st.columns(2)
        with tips_col:
            mgmt_tips_applied = st.radio("Management Briefing Tips Applied Today?", ["Yes", "No"], horizontal=True)
        with comms_col:
            comms_pref = st.selectbox("Preferred Communication Method", COMMS_METHODS)

        mgmt_tips_detail = st.text_area("If Yes — Which Tips Applied (optional)")
        feedback = st.text_area("Client Feedback Received Today (if any)")
        services_promoted = st.text_area("Services/Products Promoted Today")

        submitted = st.form_submit_button("Submit Daily Summary", type="primary")

        if submitted:
            if staff_name == "Please Select":
                st.error("Please select your staff name before submitting.")
            else:
                row = [
                    entry_date.strftime("%d/%m/%Y"),
                    staff_name,
                    int(pnrs),
                    int(calls),
                    int(emails),
                    int(enquiries_logged),
                    int(callbacks),
                    tasks,
                    price_tips,
                    mgmt_tips_applied,
                    mgmt_tips_detail,
                    comms_pref,
                    feedback,
                    services_promoted,
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                ]
                ok, err = send_row("Daily Summary", row)
                if ok:
                    st.success("Daily Summary submitted. Thank you!")
                else:
                    st.error(err)

# ---------------------------------------------------------------------------
# ENQUIRY LOG FORM
# ---------------------------------------------------------------------------
with tab2:
    with st.form("enquiry_log_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            entry_date = st.date_input("Date", value=date.today())
        with col2:
            staff_name = st.selectbox("Staff Name", STAFF_NAMES)

        ref_col, client_col = st.columns(2)
        with ref_col:
            ref_id = st.text_input("Enquiry / Zooma Ref ID")
        with client_col:
            client_name = st.text_input("Client Name")

        recv_col, channel_col = st.columns(2)
        with recv_col:
            date_received = st.date_input("Date Enquiry Originally Received", value=date.today())
        with channel_col:
            channel = st.selectbox("Enquiry Source / Channel", CHANNELS)

        price_offered = st.radio("Price/Options Offered?", ["Yes", "No"], horizontal=True)
        price_details = st.text_area("Price/Options Offered — Details (if Yes)")

        comms_col, followups_col = st.columns(2)
        with comms_col:
            comms_used = st.selectbox("Communication Method Used", COMMS_METHODS)
        with followups_col:
            followups = st.number_input("No. of Follow-Ups / Callbacks for This Enquiry", min_value=0, step=1)

        coordinated = st.radio("Coordinated with a Teammate?", ["Yes", "No"], horizontal=True)
        teammate_name = st.selectbox("Teammate Name (if Yes)", STAFF_NAMES)

        outcome_col, reason_col = st.columns(2)
        with outcome_col:
            outcome = st.selectbox("Outcome", OUTCOMES)
        with reason_col:
            reason = st.selectbox("Reason if Not Converted", REASONS)

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Submit Enquiry Entry", type="primary")

        if submitted:
            if staff_name == "Please Select":
                st.error("Please select your staff name before submitting.")
            elif not ref_id or not client_name:
                st.error("Please enter both the Enquiry/Zooma Ref ID and Client Name.")
            else:
                row = [
                    entry_date.strftime("%d/%m/%Y"),
                    staff_name,
                    ref_id,
                    client_name,
                    date_received.strftime("%d/%m/%Y"),
                    channel,
                    price_offered,
                    price_details,
                    comms_used,
                    int(followups),
                    coordinated,
                    teammate_name,
                    outcome,
                    reason,
                    notes,
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                ]
                ok, err = send_row("Enquiry Log", row)
                if ok:
                    st.success("Enquiry entry submitted. Thank you!")
                else:
                    st.error(err)

# ---------------------------------------------------------------------------
# ADMIN: LINK TO GOOGLE SHEET (password protected)
# ---------------------------------------------------------------------------
st.divider()
with st.expander("Manager access: view the Google Sheet"):
    manager_password = st.text_input("Enter manager password", type="password")

    if manager_password:
        correct_password = st.secrets.get("manager_password", None)
        sheet_url = st.secrets.get("sheet_url", None)
        if correct_password is None:
            st.error("No manager password has been set up yet. Add one in Streamlit Cloud → Settings → Secrets.")
        elif manager_password == correct_password:
            if sheet_url:
                st.success("Access confirmed.")
                st.link_button("Open Google Sheet", sheet_url)
            else:
                st.error("No sheet_url has been set up yet. Add it in Streamlit Cloud → Settings → Secrets.")
        else:
            st.error("Incorrect password.")

st.markdown(
    """
    <div style="text-align:center; color:#9a9a9a; font-size:0.8rem; margin-top:32px;">
        Buddha Travel and Tours &mdash; Internal Sales Tool
    </div>
    """,
    unsafe_allow_html=True,
)
