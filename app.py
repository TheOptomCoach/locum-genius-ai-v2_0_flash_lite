"""
Locum Genius AI — Premium Streamlit Interface
A gold-accented dark-mode chat UI for UK locum optometrists.
"""
import os
import sys
import streamlit as st

# Allow imports from this directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat import query_rag, load_store_name, extract_citations

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Locum Genius AI",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── Premium CSS (Dark Mode + Gold Accents) ────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@300;400;600;700&display=swap');

    /* ── Root Variables ── */
    :root {
        --bg-primary:    #000000;
        --bg-secondary:  #0a0a0a;
        --bg-card:       #000000;
        --bg-input:      #111111;
        --accent:        #daa520; /* Golden accent */
        --accent-light:  rgba(218, 165, 32, 0.1);
        --accent-dark:   #b8860b;
        --text-primary:  #ffffff;
        --text-muted:    #a1a1aa;
        --text-dim:      #71717a;
        --border:        #27272a;
        --user-bubble:   linear-gradient(135deg, #1e1e1e 0%, #000000 100%);
        --accent-glow:   rgba(218, 165, 32, 0.05);
    }

    /* ── Global Reset ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
        background-color: var(--bg-primary) !important;
    }

    .stApp {
        background-color: var(--bg-primary) !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, .stDeployButton { display: none !important; }
    header[data-testid="stHeader"] { background: transparent !important; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 2px; }

    /* ── Hero Header ── */
    .hero-wrapper {
        text-align: center;
        padding: 2rem 0 1.5rem 0;
        position: relative;
    }

    .hero-badge {
        display: inline-block;
        background: var(--accent-light);
        border: 1px solid var(--accent);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        color: var(--accent-dark);
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }

    .hero-title {
        font-family: 'Sora', sans-serif !important;
        font-size: 2.6rem !important;
        font-weight: 700 !important;
        color: var(--accent) !important;
        margin: 0 0 0.6rem 0 !important;
        padding: 0 !important;
        line-height: 1.15 !important;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: var(--text-primary);
        font-weight: 400;
        letter-spacing: 0.01em;
        margin-bottom: 0.5rem;
    }

    .hero-divider {
        width: 60px;
        height: 3px;
        background: var(--accent);
        margin: 1.2rem auto 0;
        border-radius: 2px;
    }

    /* ── Suggestion Chips ── */
    .chips-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        padding: 0.8rem 0 1.5rem 0;
    }

    .chip {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 7px 16px;
        font-size: 0.82rem;
        color: var(--text-primary);
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .chip:hover {
        border-color: var(--accent);
        color: var(--accent);
        background: var(--accent-light);
    }

    /* ── Chat Messages ── */
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin-bottom: 1.2rem !important;
    }

    /* User bubbles — Blue Gradient + White Text */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse !important;
    }
    
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {
         color: white !important;
    }

    /* ── Citation Card ── */
    .citation-card {
        margin-top: 12px;
        padding: 12px 16px;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent);
        border-radius: 8px;
        font-size: 0.82rem;
    }

    .citation-header {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 8px;
    }

    .citation-item {
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--text-muted);
        padding: 4px 0;
        font-size: 0.82rem;
    }

    .citation-item::before {
        content: "📄";
        font-size: 0.85rem;
    }

    /* ── Input ── */
    .stChatInputContainer {
        padding-bottom: 2.5rem !important;
        background: transparent !important;
    }

    .stChatInputContainer > div {
        background: var(--bg-input) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        transition: border-color 0.2s ease !important;
    }

    .stChatInputContainer > div:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-light) !important;
    }

    .stChatInputContainer textarea {
        background: transparent !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        border: none !important;
    }

    .stChatInputContainer textarea::placeholder {
        color: var(--text-dim) !important;
    }

    /* ── Thinking animation ── */
    @keyframes shimmer {
        0%   { opacity: 0.3; }
        50%  { opacity: 1; }
        100% { opacity: 0.3; }
    }

    .thinking-pulse {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: var(--accent);
        font-size: 0.9rem;
        font-style: italic;
        animation: shimmer 1.8s ease-in-out infinite;
    }

    /* ── Status widget ── */
    .stStatusWidget {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }

    /* ── Clear Button ── */
    .clear-btn-container {
        position: absolute;
        top: 2rem;
        right: 0;
    }

    /* ── Error banner ── */
    .error-banner {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-radius: 8px;
        padding: 12px 16px;
        color: #fca5a5;
        font-size: 0.88rem;
        text-align: center;
        margin: 1rem 0;
    }

    /* ── Watermark ── */
    .watermark {
        text-align: center;
        color: var(--text-primary);
        opacity: 0.6;
        font-size: 0.72rem;
        padding: 0.5rem 0 0;
        letter-spacing: 0.05em;
    }

    /* ── Override Streamlit button ── */
    .stButton > button {
        background: var(--bg-card) !important;
        color: var(--text-muted) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        font-size: 1.1rem !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        background: var(--accent-light) !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []


# ─── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
    <div class="hero-badge">OptometryPro</div>
    <h1 class="hero-title">Locum Genius AI 🧠</h1>
    <p class="hero-subtitle">Your AI-powered expert for UK locum optometry work</p>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)


# ─── Clear Chat ────────────────────────────────────────────────────────────────
if st.session_state.messages:
    col1, col2, col3 = st.columns([8, 2, 1])
    with col2:
        if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


# ─── Suggestion Chips (only when chat is empty) ────────────────────────────────
SUGGESTIONS = [
    "What equipment does Blue Pharamacy Optician use?",
    "How does Costco handle referrals?",
    "What are the CMG's for glaucoma suspect?",
    "Light Green Supermarket Optician payment process for locums?",
    "Purple Multiple's dry eye protocol?",
    "Can I do contact lens fits at Green Multiple?",
]

if not st.session_state.messages:
    chips_html = '<div class="chips-container">' + "".join(
        f'<div class="chip">{s}</div>' for s in SUGGESTIONS
    ) + "</div>"
    st.markdown(chips_html, unsafe_allow_html=True)


# ─── Check Store is Ready ──────────────────────────────────────────────────────
store_name = load_store_name()
if not store_name:
    st.markdown("""
    <div class="error-banner">
        ⚠️ Knowledge base not yet indexed.<br>
        <strong>Run:</strong> <code>python indexer.py</code> from the <code>locum-genius-ai/</code> folder first.
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── Render Existing Messages ──────────────────────────────────────────────────
def render_citations(citations: list[dict]) -> str:
    if not citations:
        return ""
    items = "".join(f'<div class="citation-item">{c["title"]}</div>' for c in citations)
    return f'<div class="citation-card"><div class="citation-header">Sources Referenced</div>{items}</div>'


for msg in st.session_state.messages:
    avatar = "🧑‍⚕️" if msg["role"] == "user" else "🧠"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if "citations" in msg and msg["citations"]:
            st.markdown(render_citations(msg["citations"]), unsafe_allow_html=True)


# ─── Chat Input ───────────────────────────────────────────────────────────────
prompt = st.chat_input(
    "Ask about any UK optical chain, COO guidelines, or clinical protocols..."
)

if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍⚕️"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant", avatar="🧠"):
        thinking_slot = st.empty()
        thinking_slot.markdown(
            '<div class="thinking-pulse">Locum Genius AI is thinking...</div>',
            unsafe_allow_html=True
        )

        response = query_rag(prompt)
        thinking_slot.empty()

        if response and response.text:
            st.markdown(response.text)
            citations = extract_citations(response)

            if citations:
                st.markdown(render_citations(citations), unsafe_allow_html=True)

            # Store in history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.text,
                "citations": citations
            })

            st.rerun()

        else:
            err = "⚠️ I couldn't retrieve an answer. Please rephrase your question or check your connection."
            st.markdown(f'<div class="error-banner">{err}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": err, "citations": []})


# ─── Watermark ────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="watermark">Locum Genius AI · OptometryPro.co.uk · Powered by Google Gemini</div>',
    unsafe_allow_html=True
)
