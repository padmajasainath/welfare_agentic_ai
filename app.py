import streamlit as st
import event_store
import threading
import time
from datetime import datetime
from orchestrator import start_orchestrator
 
# Page Config
st.set_page_config(page_title="AERIS Live Pulse", layout="wide")
 
# Theme / Aesthetics - Luxury Silk & Gold (Etihad Signature)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
 
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
   
    .stApp {
        background: linear-gradient(135deg, #FDFBF7 0%, #E6E2D3 100%);
        background-attachment: fixed;
    }
 
    /* Frosted Glass Card */
    .ae-card-wrapper {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(203, 178, 121, 0.4);
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(182, 172, 142, 0.2);
    }
 
    .ae-header {
        border-bottom: 2px solid rgba(203, 178, 121, 0.3);
        padding-bottom: 20px;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
 
    .ae-title {
        color: #1A1A1A;
        font-weight: 600;
        font-size: 1.8rem;
        margin: 0;
        letter-spacing: -0.5px;
    }
 
    .ae-badge-pulse {
        background: #D32F2F;
        color: white;
        padding: 8px 18px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.3);
        animation: pulse-light 2s infinite;
    }
 
    @keyframes pulse-light {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.9; }
        100% { transform: scale(1); opacity: 1; }
    }
 
    .metric-pill {
        background: rgba(203, 178, 121, 0.15);
        border: 1px solid rgba(203, 178, 121, 0.2);
        padding: 15px 25px;
        border-radius: 12px;
        text-align: center;
    }
 
    .agent-box-crew {
        background: rgba(76, 175, 80, 0.08);
        border: 1px solid rgba(76, 175, 80, 0.2);
        padding: 20px;
        border-radius: 15px;
    }
 
    .agent-box-welfare {
        background: rgba(2, 136, 209, 0.08);
        border: 1px solid rgba(2, 136, 209, 0.2);
        padding: 20px;
        border-radius: 15px;
    }
 
    .sidebar-title {
        color: #B3995D;
        font-weight: 600;
        font-size: 1.2rem;
        letter-spacing: 1px;
    }
 
    /* Override Streamlit elements for light mode consistency */
    [data-testid="stSidebar"] {
        background-color: #F7F5F0;
        border-right: 1px solid #E6E2D3;
    }
   
    h1, h2, h3, h4, h5, p {
        color: #1A1A1A !important;
    }
    </style>
""", unsafe_allow_html=True)
 
# Start Orchestrator in a Background Thread
if 'orchestrator_started' not in st.session_state:
    thread = threading.Thread(target=start_orchestrator, daemon=True)
    thread.start()
    st.session_state.orchestrator_started = True
 
# Premium Silk Header
st.markdown('<div style="margin-bottom: 50px; padding: 20px 0;">', unsafe_allow_html=True)
c_logo, c_title = st.columns([1, 4])
with c_logo:
    st.image("https://www.etihad.com/content/dam/eag/etihadairways/etihadcom/Global/logo/header/header-text-image-web.svg", width=180)
with c_title:
    st.markdown('<h1 style="color: #1A1A1A; margin: 0; font-size: 3rem; font-weight: 600;">AERIS <span style="color: #B3995D; font-weight: 300;">LIVE PULSE</span></h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; font-size: 1.1rem; letter-spacing: 2px; margin-top: -10px;">ETIHAD INTELLIGENT OPERATIONS COMMAND</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
 
with st.sidebar:
    # Etihad Branding & Status
    st.image("https://www.etihad.com/content/dam/eag/etihadairways/etihadcom/Global/logo/header/header-text-image-web.svg", use_container_width=True)
    st.markdown('<div style="background: #FAF9F6; border: 1px solid #B3995D; color: #B3995D; padding: 10px; border-radius: 8px; text-align: center; font-weight: 600; letter-spacing: 2px; font-size: 0.8rem; margin-top: 10px;">AERIS ACTIVE</div>', unsafe_allow_html=True)
   
    st.markdown("---")
    st.markdown(f'<p style="color: #666; font-size: 0.8rem; font-weight:600;">SERVER DATE (UTC)</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size: 1.1rem; font-weight: 400; color: #1A1A1A;">{datetime.utcnow().date()}</p>', unsafe_allow_html=True)
 
    st.markdown("---")
    st.markdown('<p class="sidebar-title">🤖 ETIHAD AI ASSISTANT</p>', unsafe_allow_html=True)
   
    # Initialize chatbot in session state
    from agents.chatbot_agent import ChatbotAgent
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = ChatbotAgent()
   
    if "chat_response" not in st.session_state:
        st.session_state.chat_response = None
   
    with st.form("chat_form"):
        user_query = st.text_area("Ask about Etihad, Fleet, or Policies:", height=100)
        submitted = st.form_submit_button("Ask Assistant")
       
        if submitted and user_query:
            with st.spinner("Consulting knowledge base..."):
                response = st.session_state.chatbot.run(user_query)
                st.session_state.chat_response = response
       
    if st.session_state.chat_response:
        st.markdown(f"**Answer:**\n{st.session_state.chat_response}")
 
# Main Feed - Using st.fragment for smooth background updates without page reset
@st.fragment(run_every=3)
def display_dashboard():
    events = event_store.get_events()
   
    if not events:
        st.markdown('<div style="text-align: center; padding: 100px; border: 1px dashed #CBB279; border-radius: 16px; color: #8C8C8C;">AWAITING SIGNAL DATA...</div>', unsafe_allow_html=True)
   
    for event in events:
        # Luxury Card Container
        with st.container(border=True):
            # Header Row
            h_col1, h_col2 = st.columns([3, 1])
            with h_col1:
                st.markdown(f'<h2 style="margin:0; color:#1A1A1A;">✈️ AERIS | FLIGHT {event["flight"]}</h2>', unsafe_allow_html=True)
            with h_col2:
                st.markdown('<div style="background:#D32F2F; color:white; padding:6px 15px; border-radius:20px; text-align:center; font-weight:600; font-size:0.8rem;">DISRUPTION ACTIVE</div>', unsafe_allow_html=True)
           
            st.markdown('<div style="margin: 15px 0; border-bottom: 2px solid rgba(203, 178, 121, 0.2);"></div>', unsafe_allow_html=True)
 
            # Metric Row
            met1, met2, met3 = st.columns(3)
            with met1:
                st.markdown(f'<p style="color:#8C8C8C; font-size:0.75rem; margin:0; font-weight:600;">ORIGIN</p><p style="color:#1A1A1A; font-size:1.3rem; margin:0; font-weight:600;">{event["station"]}</p>', unsafe_allow_html=True)
            with met2:
                st.markdown(f'<p style="color:#8C8C8C; font-size:0.75rem; margin:0; font-weight:600;">DURATION</p><p style="color:#B3995D; font-size:1.3rem; margin:0; font-weight:600;">{event["delay"]:.0f} Mins</p>', unsafe_allow_html=True)
            with met3:
                st.markdown(f'<p style="color:#8C8C8C; font-size:0.75rem; margin:0; font-weight:600;">SEVERITY</p><p style="color:#D32F2F; font-size:1.3rem; margin:0; font-weight:600;">T1 ALERT</p>', unsafe_allow_html=True)
 
            st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
 
            # Agent Insights Row
            ag1, ag2 = st.columns(2)
            with ag1:
                with st.container(border=True):
                    st.markdown('<p style="color:#2E7D32; font-weight:700; font-size:0.9rem; margin-bottom:10px;">👮 CREW IMPACT AGENT</p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color:#1A1A1A; font-size:1.1rem; margin-bottom:10px;"><b>{event["crew_risk"]}</b> Conflict Detected</p>', unsafe_allow_html=True)
                    with st.expander("🔍 VIEW RECOVERY DETAILS", expanded=False):
                        st.markdown(event["crew_rec"])
            with ag2:
                with st.container(border=True):
                    st.markdown('<p style="color:#01579B; font-weight:700; font-size:0.9rem; margin-bottom:10px;">🏨 WELFARE AGENT</p>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color:#1A1A1A; font-size:1.1rem; margin-bottom:10px;"><b>{event["welfare"]["total_impacted"]}</b> Guests Impacted</p>', unsafe_allow_html=True)
                    with st.expander("📊 TACTICAL WELFARE VIEW", expanded=False):
                        st.markdown(event["welfare"]["welfare_summary"])
                    st.markdown(f'<p style="color:#666; font-size:0.75rem; margin-top:5px;">Requirement: {event["welfare"]["hotel_required"]} Hotels | {event["welfare"]["meals_required"]} Meals</p>', unsafe_allow_html=True)
 
            st.markdown('<p style="color:#8C8C8C; font-size:0.75rem; margin-top:20px; font-weight:700; text-transform:uppercase;">Passenger Proactive Communication</p>', unsafe_allow_html=True)
            st.info(event['passenger_msg'])
 
            with st.expander("📡 AIRPORT OPS BRIEFING", expanded=False):
                st.code(event['ops_msg'], language="text")
           
            with st.expander("☎️ CALL-CENTER SUMMARY", expanded=False):
                st.markdown(event.get('call_center_msg', "No summary available."))
 
            with st.expander("📶 WHATSAPP BROADCAST STATUS", expanded=True):
                recipients = event.get('recipients', [])
                if not recipients:
                    st.warning("No contact data found for this flight in PNR records.")
                else:
                    for rec in recipients:
                        st.success(f"✅ DELIVERED: {rec['name']} ({rec['phone']}) - PNR: {rec['pnr']}")
                    st.caption(f"Broadcast completed for {len(recipients)} guests.")
 
            with st.expander("📝 MANAGEMENT INTERVENTION STRATEGY", expanded=False):
                st.success(event['management_insight'])
 
        # Elegant spacing
        st.markdown('<div style="height:40px;"></div>', unsafe_allow_html=True)
 
# Run the fragment
display_dashboard()
 
 
