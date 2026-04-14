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

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    font-family: 'Inter', sans-serif !important;
    color: #ececec !important;
}}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {{ display: none !important; }}

.block-container {{ padding: 0 !important; max-width: 100% !important; }}
[data-testid="stMain"]  {{ padding: 0 !important; background: #0f0f1a !important; }}
[data-testid="stAppViewContainer"] {{ background: #0f0f1a !important; }}

/* ── text inputs (landing form) ── */
.stTextInput > div > div > input {{
    background: #12121e !important;
    border: 1px solid #2a2a40 !important;
    border-radius: 9px !important;
    color: #ececec !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    padding: 11px 14px !important;
    height: 44px !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,0.15) !important;
}}
.stTextInput > div > div > input::placeholder {{ color: #44445a !important; }}
.stTextInput label {{ display: none !important; }}

/* ── all buttons default ── */
.stButton > button {{
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 9px !important;
    transition: all 0.15s !important;
}}

/* landing CTA button */
.signup-btn .stButton > button {{
    background: #7c6af7 !important;
    border: none !important;
    color: #fff !important;
    font-size: 15px !important;
    padding: 13px 0 !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
}}
.signup-btn .stButton > button:hover {{ background: #6a58e6 !important; }}

/* ── chat input ── */
[data-testid="stChatInput"] {{
    background: #1e1e2e !important;
    border-top: 1px solid #2a2a3d !important;
    padding: 12px 20px !important;
}}
[data-testid="stChatInput"] textarea {{
    background: #2a2a3d !important;
    border: 1px solid #3a3a55 !important;
    color: #ececec !important;
    font-family: 'Inter', sans-serif !important;
    border-radius: 12px !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,0.15) !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{ color: #555570 !important; }}

/* ── sidebar ── */
[data-testid="stSidebar"] {{
    background: #161622 !important;
    border-right: 1px solid #2a2a3d !important;
    padding: 0 !important;
}}
[data-testid="stSidebar"] > div:first-child {{ padding-top: 0 !important; }}
[data-testid="stSidebarContent"] {{ padding: 0 !important; }}

[data-testid="stSidebar"] .stButton > button {{
    background: transparent !important;
    border: none !important;
    color: #7777a0 !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    border-radius: 8px !important;
    padding: 9px 12px !important;
    text-align: left !important;
    width: 100% !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: #2a2a3d !important;
    color: #ececec !important;
}}

/* new-chat button in sidebar */
.sb-new .stButton > button {{
    background: #2a2a3d !important;
    color: #ececec !important;
    border: 1px solid #3a3a55 !important;
    font-size: 13px !important;
    padding: 9px 14px !important;
    width: 100% !important;
}}
.sb-new .stButton > button:hover {{ background: #32324a !important; }}

::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: #2a2a3d; border-radius: 4px; }}

/* ── landing layout ── */
.land-bg {{
    position: fixed; inset: 0; z-index: 0;
    background-image: url('{car_src}');
    background-size: cover;
    background-position: center 35%;
    filter: brightness(0.32) saturate(0.65);
}}
.land-overlay {{
    position: fixed; inset: 0; z-index: 1;
    background: linear-gradient(
        110deg,
        rgba(10,10,20,0.05) 0%,
        rgba(10,10,20,0.45) 40%,
        rgba(10,10,20,0.94) 58%,
        rgba(10,10,20,0.99) 100%
    );
}}
.land-left {{
    position: relative; z-index: 2;
    padding: 60px 52px 52px;
    display: flex; flex-direction: column;
    justify-content: flex-end; min-height: 100vh;
}}
.l-wordmark {{
    font-size: 15px; font-weight: 700;
    color: rgba(255,255,255,0.9);
    letter-spacing: -0.01em;
    margin-bottom: 40px;
}}
.l-headline {{
    font-size: 52px; font-weight: 700;
    color: #fff; letter-spacing: -0.03em;
    line-height: 1.08; margin-bottom: 20px;
}}
.l-headline span {{ color: #a99ef7; }}
.l-sub {{
    font-size: 16px; color: rgba(255,255,255,0.5);
    line-height: 1.65; max-width: 420px; margin-bottom: 44px;
}}
.l-pills {{
    display: flex; gap: 10px; flex-wrap: wrap;
}}
.l-pill {{
    display: flex; align-items: center; gap: 9px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 9px; padding: 10px 16px;
    font-size: 13px; color: rgba(255,255,255,0.72);
    backdrop-filter: blur(8px);
}}

/* ── signup card — solid dark panel ── */
.land-right {{
    position: relative; z-index: 2;
    display: flex; align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 40px 32px;
    background: #0c0c1a;
    border-left: 1px solid #1e1e32;
}}
[data-testid="stHorizontalBlock"] > div:nth-child(2),
[data-testid="stHorizontalBlock"] > div:nth-child(2) > div,
[data-testid="stHorizontalBlock"] > div:nth-child(2) > div > div {{
    background: #0c0c1a !important;
    min-height: 100vh !important;
    z-index: 2; position: relative;
}}
[data-testid="stHorizontalBlock"] > div:nth-child(2) {{
    border-left: 1px solid #1e1e32 !important;
    padding: 0 40px !important;
}}
.sc-title {{
    font-size: 26px; font-weight: 700;
    color: #ececec; letter-spacing: -0.02em;
    margin-bottom: 6px;
    font-family: 'Inter', sans-serif;
}}
.sc-sub {{
    font-size: 13px; color: #44445a;
    margin-bottom: 28px; line-height: 1.5;
    font-family: 'Inter', sans-serif;
}}
.sc-label {{
    font-size: 11px; font-weight: 500;
    color: #666680; text-transform: uppercase;
    letter-spacing: 0.07em; margin-bottom: 6px;
    margin-top: 16px;
    font-family: 'Inter', sans-serif;
}}
.sc-divider {{
    border: none; border-top: 1px solid #2a2a3d;
    margin: 4px 0 20px;
}}
.sc-footer {{
    text-align: center; font-size: 12px;
    color: #44445a; margin-top: 18px;
    font-family: 'Inter', sans-serif;
}}
.sc-footer a {{ color: #7c6af7; text-decoration: none; }}

/* ── chat page ── */
.chat-topbar {{
    padding: 14px 28px;
    border-bottom: 1px solid #2a2a3d;
    background: #1e1e2e;
    display: flex; align-items: center; justify-content: space-between;
}}
.ct-title {{ font-size: 15px; font-weight: 600; color: #ececec; }}
.ct-sub   {{ font-size: 11px; color: #3a3a55; margin-top: 1px; }}
.ct-badge {{
    display: flex; align-items: center; gap: 6px;
    background: rgba(124,106,247,0.1);
    border: 1px solid rgba(124,106,247,0.22);
    border-radius: 20px; padding: 5px 12px;
    font-size: 11px; color: #a99ef7;
}}
.ct-dot {{ width: 5px; height: 5px; background: #7c6af7; border-radius: 50%;
    animation: blink 2.5s ease-in-out infinite; }}
@keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:0.2}} }}

.chat-messages {{
    flex: 1; overflow-y: auto;
    padding: 36px 10% 20px;
    display: flex; flex-direction: column; gap: 0;
}}
.cmsg-row {{
    display: flex; align-items: flex-start; gap: 14px;
    max-width: 760px; width: 100%; padding: 8px 0;
}}
.cmsg-row.user {{ flex-direction: row-reverse; margin-left: auto; }}
.cmsg-av {{
    width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; margin-top: 2px;
}}
.cmsg-av.ai {{
    background: linear-gradient(135deg, #7c6af7, #a99ef7); color: #fff;
}}
.cmsg-av.u {{
    background: linear-gradient(135deg, #3a3a55, #4a4a65); color: #ececec;
}}
.cmsg-body {{ flex: 1; min-width: 0; }}
.cmsg-name {{
    font-size: 12px; font-weight: 600; color: #ececec; margin-bottom: 6px;
}}
.cmsg-row.user .cmsg-name {{ text-align: right; color: #7777a0; }}
.cmsg-text {{ font-size: 14px; line-height: 1.75; color: #d0d0e8; }}
.cmsg-row.user .cmsg-text {{
    background: #2a2a3d; border-radius: 14px 14px 4px 14px;
    padding: 10px 14px; display: inline-block;
    color: #ececec; float: right;
}}
.cmsg-sep {{ border: none; border-top: 1px solid #1a1a28; margin: 4px 0; }}

.empty-chat {{
    text-align: center; padding: 70px 20px;
}}
.ec-title {{
    font-size: 20px; font-weight: 600;
    color: #ececec; margin-bottom: 8px;
}}
.ec-sub {{ font-size: 14px; color: #3a3a55; line-height: 1.65; }}

.think-row {{
    display: flex; align-items: center; gap: 14px;
    padding: 8px 0;
}}
.think-dots {{ display: flex; gap: 5px; padding: 4px 0; }}
.think-dot {{
    width: 6px; height: 6px; border-radius: 50%; background: #7c6af7;
    animation: tdot 1.4s ease-in-out infinite;
}}
.think-dot:nth-child(2) {{ animation-delay: 0.2s; }}
.think-dot:nth-child(3) {{ animation-delay: 0.4s; }}
@keyframes tdot {{
    0%,80%,100% {{ opacity:0.15; transform:scale(0.75); }}
    40%          {{ opacity:1;   transform:scale(1);    }}
}}

.chat-disc {{
    text-align: center; font-size: 11px;
    color: #22223a; padding: 8px 0 10px;
}}

/* sidebar components */
.sb-logo {{
    display: flex; align-items: center; gap: 10px;
    padding: 18px 14px 14px;
    border-bottom: 1px solid #2a2a3d;
}}
.sb-logo-name {{ font-size: 14px; font-weight: 600; color: #ececec; }}
.sb-section {{
    font-size: 10px; color: #3a3a55;
    text-transform: uppercase; letter-spacing: 0.1em;
    padding: 14px 14px 6px; font-weight: 500;
}}
.sb-topic {{
    display: flex; align-items: center; gap: 8px;
    padding: 7px 14px; font-size: 12px; color: #555570;
}}
.sb-dot {{ width: 4px; height: 4px; border-radius: 50%; background: #3a3a55; flex-shrink:0; }}
.sb-bottom {{
    border-top: 1px solid #2a2a3d;
    padding: 12px 10px;
}}
.sb-user {{
    display: flex; align-items: center; gap: 10px;
    padding: 8px 10px; border-radius: 8px;
}}
.sb-av {{
    width: 28px; height: 28px; border-radius: 50%;
    background: linear-gradient(135deg, #7c6af7, #a99ef7);
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 600; color: #fff; flex-shrink: 0;
}}
.sb-uname {{ font-size: 13px; color: #ececec; font-weight: 500; }}
.sb-urole {{ font-size: 11px; color: #555570; }}
</style>
""", unsafe_allow_html=True)


# ── RAG loader ────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_rag():
    from retriever import Retriever
    return Retriever()


# ══════════════════════════════════════════════════════════════════════════════
#  LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.entered:

    # Fixed background layers
    st.markdown('<div class="land-bg"></div><div class="land-overlay"></div>',
                unsafe_allow_html=True)

    # Two-column layout: left = hero text, right = signup form
    left_col, right_col = st.columns([1.1, 0.7], gap="small")

    # ── Left: hero ────────────────────────────────────────────────────────────
    with left_col:
        st.markdown("""
        <div class="land-left">
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

    # ── Right: real Streamlit form ────────────────────────────────────────────
    with right_col:
        st.markdown('<div class="land-right">', unsafe_allow_html=True)

        st.markdown('<div style="width:100%;max-width:380px;margin:0 auto">',
                    unsafe_allow_html=True)

        st.markdown('<div class="sc-title">Create account</div>', unsafe_allow_html=True)
        st.markdown('<div class="sc-sub">Sign up to access your automotive finance assistant</div>',
                    unsafe_allow_html=True)

        st.markdown('<div class="sc-label">Full name</div>', unsafe_allow_html=True)
        name = st.text_input("name", placeholder="Jane Smith",
                             label_visibility="collapsed", key="reg_name")

        st.markdown('<div class="sc-label">Email address</div>', unsafe_allow_html=True)
        email = st.text_input("email", placeholder="jane@example.com",
                              label_visibility="collapsed", key="reg_email")

        st.markdown('<div class="sc-label">Password</div>', unsafe_allow_html=True)
        password = st.text_input("password", type="password", placeholder="••••••••",
                                 label_visibility="collapsed", key="reg_pass")

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

        st.markdown('<div class="signup-btn">', unsafe_allow_html=True)
        if st.button("Create Account  →", key="signup_btn", use_container_width=True):
            st.session_state.entered = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            '<div class="sc-footer">Already have an account? '
            '<a href="#">Sign in</a></div>',
            unsafe_allow_html=True
        )

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  CHAT VIEW
# ══════════════════════════════════════════════════════════════════════════════
if not index_path.exists():
    st.error("Knowledge base not found. Run `python ingest.py` to set up.")
    st.stop()

retriever = load_rag()

# Show sidebar
st.markdown("""
<style>
[data-testid="stSidebar"] { display: flex !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown("""
    <div class="sb-logo">
        <div class="sb-logo-name">DriveFinance AI</div>
    </div>
    """, unsafe_allow_html=True)

    # New chat
    st.markdown('<div class="sb-new">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat history
    if st.session_state.conversations:
        st.markdown('<div class="sb-section">Recent</div>', unsafe_allow_html=True)
        for i, conv in enumerate(st.session_state.conversations[:12]):
            title   = conv["title"]
            display = title[:38] + "…" if len(title) > 38 else title
            if st.button(f"  {display}", key=f"conv_{i}", use_container_width=True):
                st.session_state.messages     = conv["messages"]
                st.session_state.chat_history = conv["history"]
                st.rerun()
    else:
        st.markdown(
            '<div style="padding:12px 14px;font-size:12px;color:#3a3a55">'
            'No conversations yet</div>',
            unsafe_allow_html=True
        )

    # Topics
    st.markdown('<div class="sb-section">Topics</div>', unsafe_allow_html=True)
    for t in ["Loan rates & APR", "Credit eligibility", "Down payments",
              "Fees & closing costs", "Refinancing", "Early payoff",
              "GAP insurance", "Required documents"]:
        st.markdown(
            f'<div class="sb-topic"><span class="sb-dot"></span>{t}</div>',
            unsafe_allow_html=True
        )

    # Quick questions
    st.markdown('<div class="sb-section">Common questions</div>', unsafe_allow_html=True)
    for q in [
        "APR for 750 credit score, new car?",
        "Minimum down payment needed?",
        "What is the late payment fee?",
        "Can I pay off my loan early?",
        "Do I need GAP insurance?",
        "How does refinancing work?",
        "What documents do I need?",
    ]:
        if st.button(q, key=f"sq_{q[:18]}", use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()

    # User footer
    st.markdown("""
    <div class="sb-bottom">
        <div class="sb-user">
            <div class="sb-av">U</div>
            <div>
                <div class="sb-uname">My Account</div>
                <div class="sb-urole">Finance Assistant</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Chat main area ────────────────────────────────────────────────────────────
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
        <div class="ec-sub">
            Ask about loan rates, down payments, fees,<br>
            refinancing options, or any finance question.
        </div>
    </div>
    """, unsafe_allow_html=True)
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

st.markdown("""
<div class="chat-disc">
    Answers grounded in official finance documents · DriveFinance AI © 2025
</div>
""", unsafe_allow_html=True)


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
             background:linear-gradient(135deg,#7c6af7,#a99ef7);
             display:flex;align-items:center;justify-content:center;
             font-size:11px;font-weight:700;color:#fff;flex-shrink:0">DF</div>
        <div class="think-dots">
          <div class="think-dot"></div>
          <div class="think-dot"></div>
          <div class="think-dot"></div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    from chain import answer as rag_answer
    result = rag_answer(
        question=question, retriever=retriever,
        k=3, chat_history=st.session_state.chat_history,
    )
    thinking.empty()

    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
    st.session_state.chat_history += [
        {"role": "user",      "content": question},
        {"role": "assistant", "content": result["answer"]},
    ]
    if len(st.session_state.chat_history) > 12:
        st.session_state.chat_history = st.session_state.chat_history[-12:]

    st.rerun()