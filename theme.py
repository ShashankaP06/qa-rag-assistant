"""Forge-inspired dark theme overrides for Streamlit."""

import streamlit as st

FORGE_CSS = """
<style>
:root {
    --forge-bg: #0e0e1a;
    --forge-bg-alt: #12122b;
    --forge-sidebar: #1c1c3c;
    --forge-purple: #7b5bf2;
    --forge-blue: #2d5cf7;
    --forge-green: #28a745;
    --forge-red: #721c24;
    --forge-gold: #ffc107;
    --forge-text-muted: #a0a0b8;
}

.stApp {
    background: linear-gradient(180deg, var(--forge-bg) 0%, var(--forge-bg-alt) 100%);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1c1c3c 0%, #16162e 100%);
    border-right: 1px solid rgba(123, 91, 242, 0.25);
}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] small {
    color: var(--forge-text-muted) !important;
}

h1, h2, h3 {
    color: #ffffff !important;
}

.stMarkdown p, .stMarkdown li {
    color: #e8e8f0;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #8b6cf5 0%, var(--forge-purple) 50%, #6a4bd9 100%) !important;
    border: 1px solid rgba(157, 133, 247, 0.6) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

.stButton > button[kind="primary"]:hover {
    border-color: var(--forge-blue) !important;
    box-shadow: 0 0 12px rgba(45, 92, 247, 0.35);
}

.stButton > button[kind="secondary"] {
    background: rgba(45, 92, 247, 0.15) !important;
    border: 1px solid rgba(45, 92, 247, 0.45) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
}

div[data-testid="stFileUploader"] section {
    border: 1px dashed rgba(123, 91, 242, 0.45) !important;
    border-radius: 8px !important;
    background: rgba(28, 28, 60, 0.5) !important;
}

div[data-baseweb="select"] > div,
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stChatInput"] textarea {
    background-color: rgba(28, 28, 60, 0.85) !important;
    border: 1px solid rgba(123, 91, 242, 0.3) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}

div[data-testid="stExpander"] details {
    border: 1px solid rgba(45, 92, 247, 0.35) !important;
    border-radius: 8px !important;
    background: rgba(28, 28, 60, 0.4) !important;
}

div[data-testid="stMetric"] {
    background: rgba(28, 28, 60, 0.55);
    border: 1px solid rgba(123, 91, 242, 0.2);
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
}

[data-testid="stAlert"][data-baseweb="notification"] {
    border-radius: 8px !important;
}

div[data-testid="stNotification"][data-status="success"],
.stSuccess {
    border-left: 4px solid var(--forge-green) !important;
}

div[data-testid="stNotification"][data-status="warning"],
.stWarning {
    border-left: 4px solid var(--forge-gold) !important;
}

div[data-testid="stNotification"][data-status="error"],
.stError {
    border-left: 4px solid #c0392b !important;
    background: rgba(114, 28, 36, 0.25) !important;
}

div[data-testid="stNotification"][data-status="info"],
.stInfo {
    border-left: 4px solid var(--forge-blue) !important;
}

hr {
    border-color: rgba(123, 91, 242, 0.2) !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(45, 92, 247, 0.25);
    border-radius: 8px;
    overflow: hidden;
}
</style>
"""


def inject_forge_theme() -> None:
    st.markdown(FORGE_CSS, unsafe_allow_html=True)
