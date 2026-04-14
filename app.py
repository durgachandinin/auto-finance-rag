"""
app.py
──────
Streamlit chat interface for the Automotive Finance RAG Assistant.

Run with:
    streamlit run app.py
"""

import os
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Auto Finance Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.source-card {
    background: #f8f9fa;
    border-left: 3px solid #1f77b4;
    border-radius: 4px;
    padding: 8px 12px;
    margin: 4px 0;
    font-size: 0.82em;
    color: #444;
}
.metric-chip {
    display: inline-block;
    background: #e8f4f8;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 0.78em;
    color: #1f77b4;
    margin-right: 6px;
}
.stChatMessage { max-width: 800px; }
</style>
""", unsafe_allow_html=True)


# ── Load RAG components (cached so they only load once) ───────────────────────
@st.cache_resource(show_spinner="Loading knowledge base...")
def load_rag():
    """Load retriever once and cache for the session."""
    from retriever import Retriever
    return Retriever()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚗 Auto Finance RAG")
    st.caption("Powered by FAISS + OpenAI")
    st.divider()

    # API key check
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key and api_key != "your_openai_api_key_here":
        st.success("OpenAI API key loaded ✓")
    else:
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Your key is only stored in session memory."
        )
        if api_key_input:
            os.environ["OPENAI_API_KEY"] = api_key_input
            st.success("API key set for this session ✓")

    st.divider()

    # Retrieval settings
    st.subheader("Retrieval settings")
    k_chunks = st.slider(
        "Chunks to retrieve (k)",
        min_value=1, max_value=6, value=3,
        help="More chunks = more context but higher token cost"
    )

    show_sources = st.toggle("Show source excerpts", value=True)
    show_tokens  = st.toggle("Show token usage", value=False)

    st.divider()

    # Index info
    index_path = Path("faiss_index/index.faiss")
    meta_path  = Path("faiss_index/metadata.pkl")

    if index_path.exists():
        import pickle
        with open(meta_path, "rb") as f:
            meta = pickle.load(f)
        unique_sources = len(set(c["source_name"] for c in meta))
        st.metric("Chunks indexed", len(meta))
        st.metric("Documents", unique_sources)
    else:
        st.warning("No index found. Run `python ingest.py` first.")

    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages      = []
        st.session_state.chat_history  = []
        st.rerun()

    st.divider()

    # Suggested questions
    st.subheader("Try asking...")
    example_questions = [
        "What APR for a 750 credit score, new car, 60 months?",
        "How much down payment do I need?",
        "What is the late payment fee?",
        "Can I pay off my loan early?",
        "Do I need GAP insurance?",
        "How does refinancing work?",
        "What documents do I need to apply?",
        "What is the maximum loan-to-value ratio?",
    ]
    for q in example_questions:
        if st.button(q, use_container_width=True, key=f"example_{q[:20]}"):
            st.session_state.pending_question = q
            st.rerun()


# ── Main area ─────────────────────────────────────────────────────────────────
st.title("🚗 Automotive Finance Assistant")
st.caption(
    "Ask questions about loan rates, eligibility, fees, refinancing, and more. "
    "Answers are grounded in your finance documents."
)

# Initialise session state
if "messages" not in st.session_state:
    st.session_state.messages     = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# Check if index exists before loading
if not index_path.exists():
    st.error(
        "**Knowledge base not found.**\n\n"
        "Run the following commands to build it:\n"
        "```bash\n"
        "python generate_sample_data.py\n"
        "python ingest.py\n"
        "```"
    )
    st.stop()

# Load RAG pipeline
retriever = load_rag()

# Render conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and show_sources and "sources" in msg:
            with st.expander(f"📄 Sources ({len(msg['sources'])} chunks retrieved)", expanded=False):
                for src in msg["sources"]:
                    score_pct = f"{src['score'] * 100:.1f}%"
                    st.markdown(
                        f'<div class="source-card">'
                        f'<b>{src["source_name"]}</b> &nbsp;'
                        f'<span class="metric-chip">rank #{src["rank"]}</span>'
                        f'<span class="metric-chip">similarity {score_pct}</span>'
                        f'<br><br>{src["text"][:300]}...'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        if msg["role"] == "assistant" and show_tokens and "usage" in msg:
            st.caption(
                f"Tokens: {msg['usage']['total_tokens']} total  "
                f"({msg['usage']['prompt_tokens']} prompt + "
                f"{msg['usage']['completion_tokens']} completion)"
            )


# ── Handle input ───────────────────────────────────────────────────────────────
question = st.chat_input("Ask about rates, fees, eligibility, refinancing...")

# Sidebar button injects into pending_question
if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None

if question:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            from chain import answer as rag_answer

            start = time.time()
            result = rag_answer(
                question=question,
                retriever=retriever,
                k=k_chunks,
                chat_history=st.session_state.chat_history,
            )
            elapsed = time.time() - start

        st.markdown(result["answer"])

        if show_sources:
            with st.expander(
                f"📄 Sources ({len(result['sources'])} chunks retrieved, "
                f"{elapsed:.1f}s)",
                expanded=False
            ):
                for src in result["sources"]:
                    score_pct = f"{src['score'] * 100:.1f}%"
                    st.markdown(
                        f'<div class="source-card">'
                        f'<b>{src["source_name"]}</b> &nbsp;'
                        f'<span class="metric-chip">rank #{src["rank"]}</span>'
                        f'<span class="metric-chip">similarity {score_pct}</span>'
                        f'<br><br>{src["text"][:300]}...'
                        f'</div>',
                        unsafe_allow_html=True
                    )

        if show_tokens:
            st.caption(
                f"Tokens: {result['usage']['total_tokens']} total  "
                f"({result['usage']['prompt_tokens']} prompt + "
                f"{result['usage']['completion_tokens']} completion)"
            )

    # Save to session state
    st.session_state.messages.append({
        "role":    "assistant",
        "content": result["answer"],
        "sources": result["sources"],
        "usage":   result["usage"],
    })

    # Update chat history for multi-turn context (last 6 turns max)
    st.session_state.chat_history.append({"role": "user",      "content": question})
    st.session_state.chat_history.append({"role": "assistant", "content": result["answer"]})
    if len(st.session_state.chat_history) > 12:
        st.session_state.chat_history = st.session_state.chat_history[-12:]

    st.rerun()
