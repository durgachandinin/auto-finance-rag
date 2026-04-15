"""
app.py  ·  DriveFinance AI
Run:  streamlit run app.py
"""

import os, base64, pickle
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="DriveFinance AI",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── car image ─────────────────────────────────────────────────────────────────
def img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

car_path = Path("car.jpg")
car_src  = f"data:image/jpeg;base64,{img_b64(str(car_path))}" if car_path.exists() else ""

# ── session state ─────────────────────────────────────────────────────────────
for k, v in {
    "messages": [], "chat_history": [],
    "pending_question": None,
    "entered": False,
    "conversations": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

index_path = Path("faiss_index/index.faiss")

# ── RAG loader ────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_rag():
    from retriever import Retriever
    return Retriever()


# ══════════════════════════════════════════════════════════════════════════════
#  LANDING PAGE
#  Strategy: inject CSS that makes Streamlit's OWN block-container
#  a full-viewport flex row. The background image goes on the body.
#  Left half = pure HTML hero. Right half = a tight dark card
#  that Streamlit widgets render inside.
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.entered:

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    html, body {{
        font-family: 'Inter', sans-serif !important;
        height: 100%; overflow: hidden;
    }}

    /* Car image on the body itself */
    body {{
        background-image: url('{car_src}') !important;
        background-size: cover !important;
        background-position: center 35% !important;
    }}

    /* Dark overlay on body via pseudo — use html instead */
    html::before {{
        content: '';
        position: fixed; inset: 0; z-index: 0;
        background: rgba(8,8,18,0.52);
        pointer-events: none;
    }}

    /* Hide all Streamlit chrome */
    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stSidebar"] {{ display: none !important; }}

    /* Make the app viewport fill the screen */
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"] {{
        background: transparent !important;
        height: 100vh !important;
        overflow: hidden !important;
    }}

    [data-testid="stMain"] {{
        background: transparent !important;
        padding: 0 !important;
        height: 100vh !important;
        overflow: hidden !important;
    }}

    /* The block container becomes a full-height flex row */
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
        height: 100vh !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: stretch !important;
        position: relative !important;
        z-index: 1 !important;
    }}

    /* ── LEFT HERO ── */
    .land-hero {{
        flex: 1.1;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding: 0 56px 60px 56px;
        background: linear-gradient(
            to right,
            rgba(8,8,18,0.0) 0%,
            rgba(8,8,18,0.0) 100%
        );
        position: relative; z-index: 2;
    }}
    .l-wordmark {{
        font-size: 14px; font-weight: 700;
        color: rgba(255,255,255,0.85);
        letter-spacing: 0.01em; margin-bottom: 36px;
    }}
    .l-headline {{
        font-size: 50px; font-weight: 700;
        color: #fff; letter-spacing: -0.03em;
        line-height: 1.1; margin-bottom: 18px;
    }}
    .l-headline span {{ color: #a99ef7; }}
    .l-sub {{
        font-size: 15px; color: rgba(255,255,255,0.5);
        line-height: 1.65; max-width: 400px; margin-bottom: 40px;
    }}
    .l-pills {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .l-pill {{
        display: flex; align-items: center; gap: 8px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 9px; padding: 9px 15px;
        font-size: 13px; color: rgba(255,255,255,0.7);
    }}

    /* ── RIGHT FORM PANEL ── */
    /* Streamlit places each top-level element in a div.element-container.
       We target the SECOND child of block-container as the right panel. */
    .block-container > div:nth-child(2) {{
        flex: 0 0 440px !important;
        width: 440px !important;
        background: #0c0c1c !important;
        border-left: 1px solid #1a1a2e !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        padding: 52px 44px !important;
        overflow-y: auto !important;
        position: relative; z-index: 2;
    }}

    /* All text elements inside form panel */
    .f-title {{
        font-size: 26px; font-weight: 700;
        color: #ececec; letter-spacing: -0.02em;
        margin-bottom: 6px;
        font-family: 'Inter', sans-serif;
    }}
    .f-sub {{
        font-size: 13px; color: #44445a;
        margin-bottom: 28px; line-height: 1.5;
        font-family: 'Inter', sans-serif;
    }}
    .f-label {{
        font-size: 11px; font-weight: 500;
        color: #555575; text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 6px; margin-top: 16px;
        font-family: 'Inter', sans-serif;
        display: block;
    }}
    .f-footer {{
        text-align: center; font-size: 12px;
        color: #44445a; margin-top: 18px;
        font-family: 'Inter', sans-serif;
    }}
    .f-footer a {{ color: #7c6af7; text-decoration: none; }}

    /* Streamlit text inputs — compact, no extra margin */
    .stTextInput {{
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }}
    .stTextInput > div {{
        margin: 0 !important; padding: 0 !important;
    }}
    .stTextInput > div > div {{
        margin: 0 !important; padding: 0 !important;
    }}
    .stTextInput > div > div > input {{
        background: #12121e !important;
        border: 1px solid #252538 !important;
        border-radius: 9px !important;
        color: #ececec !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        padding: 11px 14px !important;
        height: 44px !important;
        width: 100% !important;
        display: block !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: #7c6af7 !important;
        box-shadow: 0 0 0 3px rgba(124,106,247,0.14) !important;
        outline: none !important;
    }}
    .stTextInput > div > div > input::placeholder {{
        color: #363650 !important;
    }}
    .stTextInput label {{ display: none !important; }}

    /* Remove all vertical spacing Streamlit adds between widgets */
    .element-container {{
        margin: 0 !important;
        padding: 0 !important;
    }}
    [data-testid="stVerticalBlock"] > div {{
        gap: 0 !important;
    }}

    /* CTA button */
    .stButton > button {{
        background: #7c6af7 !important;
        border: none !important;
        color: #fff !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 13px 0 !important;
        border-radius: 10px !important;
        width: 100% !important;
        margin-top: 20px !important;
        letter-spacing: 0.01em !important;
        transition: background 0.15s !important;
        cursor: pointer !important;
    }}
    .stButton > button:hover {{ background: #6a58e6 !important; }}
    </style>
    """, unsafe_allow_html=True)

    # ── LEFT: hero HTML ────────────────────────────────────────────────────────
    st.markdown("""
    <div class="land-hero">
        <div class="l-wordmark">DriveFinance AI</div>
        <div class="l-headline">Smart answers for<br><span>your auto loan</span></div>
        <div class="l-sub">
            Get instant, accurate answers about financing rates, eligibility,
            fees, and refinancing — powered by your official finance documents.
        </div>
        <div class="l-pills">
            <div class="l-pill">💬 &nbsp;Plain-English answers</div>
            <div class="l-pill">📋 &nbsp;Document-grounded</div>
            <div class="l-pill">⚡ &nbsp;Instant responses</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── RIGHT: form widgets ────────────────────────────────────────────────────
    # Streamlit places this as the second top-level child — targeted by CSS above
    with st.container():
        st.markdown('<div class="f-title">Create account</div>', unsafe_allow_html=True)
        st.markdown('<div class="f-sub">Sign up to access your automotive finance assistant</div>',
                    unsafe_allow_html=True)

        st.markdown('<span class="f-label">Full name</span>', unsafe_allow_html=True)
        st.text_input("fullname", placeholder="Jane Smith",
                      label_visibility="collapsed", key="reg_name")

        st.markdown('<span class="f-label">Email address</span>', unsafe_allow_html=True)
        st.text_input("email", placeholder="jane@example.com",
                      label_visibility="collapsed", key="reg_email")

        st.markdown('<span class="f-label">Password</span>', unsafe_allow_html=True)
        st.text_input("password", type="password", placeholder="••••••••",
                      label_visibility="collapsed", key="reg_pass")

        if st.button("Create Account  →", key="signup_btn", use_container_width=True):
            st.session_state.entered = True
            st.rerun()

        st.markdown(
            '<div class="f-footer">Already have an account? <a href="#">Sign in</a></div>',
            unsafe_allow_html=True)

    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  CHAT VIEW
# ══════════════════════════════════════════════════════════════════════════════

# Global CSS for chat view
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
    background: #1e1e2e !important;
    color: #ececec !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stMain"] { padding: 0 !important; background: #1e1e2e !important; }

[data-testid="stSidebar"] {
    background: #161622 !important;
    border-right: 1px solid #2a2a3d !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebarContent"] { padding: 0 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #7777a0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    border-radius: 8px !important;
    padding: 9px 12px !important;
    text-align: left !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #2a2a3d !important; color: #ececec !important;
}

[data-testid="stChatInput"] {
    background: #1e1e2e !important;
    border-top: 1px solid #2a2a3d !important;
    border: none !important;
    padding: 12px 20px !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] > div {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea {
    background: #2a2a3d !important;
    border: 1px solid #3a3a55 !important;
    color: #ececec !important;
    font-family: 'Inter', sans-serif !important;
    border-radius: 12px !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #3a3a55 !important;
    box-shadow: none !important;
    outline: none !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #555570 !important; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2a3d; border-radius: 4px; }

.chat-topbar {
    padding: 14px 28px;
    border-bottom: 1px solid #2a2a3d;
    background: #1e1e2e;
    display: flex; align-items: center; justify-content: space-between;
}
.ct-title { font-size: 15px; font-weight: 600; color: #ececec; }
.ct-sub   { font-size: 11px; color: #3a3a55; margin-top: 1px; }
.ct-badge {
    display: flex; align-items: center; gap: 6px;
    background: rgba(124,106,247,0.1);
    border: 1px solid rgba(124,106,247,0.22);
    border-radius: 20px; padding: 5px 12px;
    font-size: 11px; color: #a99ef7;
}
.ct-dot { width: 5px; height: 5px; background: #7c6af7; border-radius: 50%;
    animation: blink 2.5s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

.chat-messages { padding: 36px 10% 20px; display: flex; flex-direction: column; gap: 0; }
.cmsg-row {
    display: flex; align-items: flex-start; gap: 14px;
    max-width: 760px; width: 100%; padding: 8px 0;
}
.cmsg-row.user { flex-direction: row-reverse; margin-left: auto; }
.cmsg-av {
    width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; margin-top: 2px;
}
.cmsg-av.ai { background: linear-gradient(135deg,#7c6af7,#a99ef7); color:#fff; }
.cmsg-av.u  { background: linear-gradient(135deg,#3a3a55,#4a4a65); color:#ececec; }
.cmsg-body  { flex:1; min-width:0; }
.cmsg-name  { font-size:12px; font-weight:600; color:#ececec; margin-bottom:6px; }
.cmsg-row.user .cmsg-name { text-align:right; color:#7777a0; }
.cmsg-text  { font-size:14px; line-height:1.75; color:#d0d0e8; }
.cmsg-row.user .cmsg-text {
    background:#2a2a3d; border-radius:14px 14px 4px 14px;
    padding:10px 14px; display:inline-block; color:#ececec; float:right;
}
.cmsg-sep { border:none; border-top:1px solid #1a1a28; margin:4px 0; }

.empty-chat { text-align:center; padding:70px 20px; }
.ec-title { font-size:20px; font-weight:600; color:#ececec; margin-bottom:8px; }
.ec-sub   { font-size:14px; color:#3a3a55; line-height:1.65; }

.think-row { display:flex; align-items:center; gap:14px; padding:8px 0; }
.think-dots { display:flex; gap:5px; padding:4px 0; }
.think-dot {
    width:6px; height:6px; border-radius:50%; background:#7c6af7;
    animation: tdot 1.4s ease-in-out infinite;
}
.think-dot:nth-child(2) { animation-delay:0.2s; }
.think-dot:nth-child(3) { animation-delay:0.4s; }
@keyframes tdot {
    0%,80%,100% { opacity:0.15; transform:scale(0.75); }
    40%          { opacity:1;   transform:scale(1);    }
}
.chat-disc { text-align:center; font-size:11px; color:#22223a; padding:8px 0 10px; }

.sb-logo { display:flex; align-items:center; gap:10px; padding:18px 14px 14px; border-bottom:1px solid #2a2a3d; }
.sb-logo-name { font-size:14px; font-weight:600; color:#ececec; }
.sb-section { font-size:10px; color:#3a3a55; text-transform:uppercase; letter-spacing:0.1em; padding:14px 14px 6px; font-weight:500; }
.sb-topic { display:flex; align-items:center; gap:8px; padding:7px 14px; font-size:12px; color:#555570; }
.sb-dot { width:4px; height:4px; border-radius:50%; background:#3a3a55; flex-shrink:0; }
.sb-bottom { border-top:1px solid #2a2a3d; padding:12px 10px; }
.sb-user { display:flex; align-items:center; gap:10px; padding:8px 10px; border-radius:8px; }
.sb-av { width:28px; height:28px; border-radius:50%; background:linear-gradient(135deg,#7c6af7,#a99ef7); display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:600; color:#fff; flex-shrink:0; }
.sb-uname { font-size:13px; color:#ececec; font-weight:500; }
.sb-urole { font-size:11px; color:#555570; }
</style>
""", unsafe_allow_html=True)

if not index_path.exists():
    st.error("Knowledge base not found. Run `python ingest.py` to set up.")
    st.stop()

retriever = load_rag()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-logo"><div class="sb-logo-name">DriveFinance AI</div></div>',
                unsafe_allow_html=True)

    if st.button("＋  New conversation", key="new_chat", use_container_width=True):
        if st.session_state.messages:
            first_q = next(
                (m["content"][:48] for m in st.session_state.messages if m["role"] == "user"),
                "Conversation"
            )
            st.session_state.conversations.insert(0, {
                "title":    first_q,
                "messages": st.session_state.messages.copy(),
                "history":  st.session_state.chat_history.copy(),
            })
        st.session_state.messages     = []
        st.session_state.chat_history = []
        st.rerun()

    if st.session_state.conversations:
        st.markdown('<div class="sb-section">Recent</div>', unsafe_allow_html=True)
        for i, conv in enumerate(st.session_state.conversations[:12]):
            title   = conv["title"]
            display = title[:36] + "…" if len(title) > 36 else title
            if st.button(f"  {display}", key=f"conv_{i}", use_container_width=True):
                st.session_state.messages     = conv["messages"]
                st.session_state.chat_history = conv["history"]
                st.rerun()
    else:
        st.markdown('<div style="padding:10px 14px;font-size:12px;color:#3a3a55">No conversations yet</div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Topics</div>', unsafe_allow_html=True)
    for t in ["Loan rates & APR", "Credit eligibility", "Down payments",
              "Fees & closing costs", "Refinancing", "Early payoff",
              "GAP insurance", "Required documents"]:
        st.markdown(f'<div class="sb-topic"><span class="sb-dot"></span>{t}</div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Common questions</div>', unsafe_allow_html=True)
    for q in ["APR for 750 credit score, new car?", "Minimum down payment needed?",
              "What is the late payment fee?", "Can I pay off my loan early?",
              "Do I need GAP insurance?", "How does refinancing work?",
              "What documents do I need?"]:
        if st.button(q, key=f"sq_{q[:18]}", use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()

    st.markdown("""
    <div class="sb-bottom">
        <div class="sb-user">
            <div class="sb-av">U</div>
            <div><div class="sb-uname">My Account</div><div class="sb-urole">Finance Assistant</div></div>
        </div>
    </div>""", unsafe_allow_html=True)

# ── Main chat ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="chat-topbar">
  <div>
    <div class="ct-title">Automotive Finance Assistant</div>
    <div class="ct-sub">Powered by your finance documents</div>
  </div>
  <div class="ct-badge"><span class="ct-dot"></span>AI Online</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="empty-chat">
        <div class="ec-title">How can I help you today?</div>
        <div class="ec-sub">Ask about loan rates, down payments, fees,<br>refinancing, or any finance question.</div>
    </div>""", unsafe_allow_html=True)
else:
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="cmsg-row user">
                <div class="cmsg-av u">U</div>
                <div class="cmsg-body">
                    <div class="cmsg-name">You</div>
                    <div class="cmsg-text">{msg['content']}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="cmsg-row">
                <div class="cmsg-av ai">DF</div>
                <div class="cmsg-body">
                    <div class="cmsg-name">DriveFinance AI</div>
                    <div class="cmsg-text">{msg['content']}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        if i < len(st.session_state.messages) - 1:
            st.markdown('<hr class="cmsg-sep"/>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-disc">Answers grounded in official finance documents · DriveFinance AI © 2025</div>',
            unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
question = st.chat_input("Message DriveFinance AI…")

if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    thinking = st.empty()
    thinking.markdown("""
    <div style="padding:8px 10%">
      <div class="think-row">
        <div class="cmsg-av ai" style="width:32px;height:32px;border-radius:50%;
             background:linear-gradient(135deg,#7c6af7,#a99ef7);display:flex;
             align-items:center;justify-content:center;font-size:11px;
             font-weight:700;color:#fff;flex-shrink:0">DF</div>
        <div class="think-dots">
          <div class="think-dot"></div><div class="think-dot"></div><div class="think-dot"></div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    from chain import answer as rag_answer
    result = rag_answer(question=question, retriever=retriever,
                        k=3, chat_history=st.session_state.chat_history)
    thinking.empty()

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
    st.session_state.chat_history += [
        {"role": "user",      "content": question},
        {"role": "assistant", "content": result["answer"]},
    ]
    if len(st.session_state.chat_history) > 12:
        st.session_state.chat_history = st.session_state.chat_history[-12:]
    st.rerun()