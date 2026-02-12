# ------------------------------------------------------------------------------
import os, re, sys, zipfile, subprocess, io, tempfile, shutil, contextlib, html
import streamlit as st
from dotenv import load_dotenv
from crewai import Crew, Process

from agents.coder_agent import CoderAgentFactory
from agents.tester_agent import TesterAgentFactory
from agents.reviewer_agent import ReviewerAgentFactory
from agents.docs_agent import DocsAgentFactory
from agents.bugfix_agent import BugFixAgentFactory

load_dotenv()
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

st.set_page_config(page_title="DevFlow.AI", page_icon="D", layout="wide",
                   initial_sidebar_state="collapsed")

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
  --bg: #070b14;
  --bg-2: #0c1220;
  --surface: #121a2c;
  --surface-2: #171f34;
  --border: #27314a;
  --text: #eef3ff;
  --muted: #9ca9c6;
  --accent: #2dd4bf;
  --accent-2: #60a5fa;
  --ok: #34d399;
  --warn: #f59e0b;
  --fail: #f87171;
  --mono: 'IBM Plex Mono', monospace;
}

html, body, [class*="css"] {
  font-family: 'Manrope', sans-serif !important;
  color: var(--text) !important;
  background:
    radial-gradient(1200px 600px at 8% -5%, rgba(45, 212, 191, 0.08), transparent 55%),
    radial-gradient(900px 500px at 95% 8%, rgba(96, 165, 250, 0.09), transparent 50%),
    linear-gradient(180deg, var(--bg), var(--bg-2)) !important;
}
html { font-size: 15px; }

section[data-testid="stSidebar"],
button[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
header[data-testid="stHeader"],
#MainMenu, .stDeployButton, footer,
div[data-testid="stDecoration"] { display: none !important; }

.block-container {
  max-width: none !important;
  width: auto !important;
  margin: 0 390px 0 24px !important;
  padding: 28px 20px 70px !important;
  overflow-x: hidden !important;
}

div[data-testid="stVerticalBlock"] { gap: 1.05rem !important; }

a { color: var(--accent); }

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: rgba(18, 26, 44, 0.78);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px 16px;
  backdrop-filter: blur(8px);
}
.topbar-left { display: flex; align-items: center; gap: 12px; }
.topbar-logo {
  width: 42px;
  height: 42px;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--accent), #0ea5e9);
  color: #05131a;
  font-weight: 800;
}
.topbar-brand {
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.4px;
  color: var(--text);
}
.topbar-brand span { color: #ff9c66; }
.topbar-pills { display: flex; gap: 8px; flex-wrap: wrap; }
.pill {
  background: rgba(255, 255, 255, 0.03);
  color: var(--muted);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 11px;
  font-weight: 600;
}
.pill-acc { color: var(--accent); border-color: rgba(45, 212, 191, 0.35); }
.pill-green { color: var(--ok); border-color: rgba(52, 211, 153, 0.35); }

.hero {
  margin: 18px 0 22px;
  border: 1px solid var(--border);
  border-radius: 22px;
  padding: 34px 30px;
  background:
    radial-gradient(100% 220% at 0% 0%, rgba(45, 212, 191, 0.10), transparent 45%),
    radial-gradient(90% 180% at 100% 0%, rgba(96, 165, 250, 0.10), transparent 42%),
    linear-gradient(145deg, #11192c, #0d1323);
}
.hero h1 {
  margin: 0;
  font-size: clamp(30px, 4.2vw, 52px);
  line-height: 1.02;
  letter-spacing: -1.2px;
  color: var(--text);
}
.hero h1 span {
  background: linear-gradient(90deg, var(--accent), #67e8f9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  margin: 12px 0 0;
  max-width: 760px;
  color: #bfd0f2;
  font-size: 16px;
  line-height: 1.6;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 24px;
}
@media (max-width: 980px) {
  .agents-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
.ag {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 15px 14px;
  transition: border-color .2s ease, transform .2s ease;
}
.ag:hover {
  border-color: rgba(45, 212, 191, 0.45);
  transform: translateY(-2px);
}
.ag h4 { margin: 10px 0 4px; font-size: 14px; color: var(--text); }
.ag p { margin: 0; color: var(--muted); font-size: 12px; line-height: 1.46; }
.ag-icon {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}
.ag-icon.ic { background: #0ea5a0; }
.ag-icon.it { background: #3b82f6; }
.ag-icon.ib { background: #f59e0b; }
.ag-icon.ir { background: #a855f7; }
.ag-icon.id { background: #22c55e; }

.divider { display: flex; align-items: center; gap: 10px; margin: 18px 0 12px; }
.div-dot {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--accent);
  box-shadow: 0 0 12px rgba(45, 212, 191, 0.65);
}
.div-text {
  text-transform: uppercase;
  letter-spacing: 2px;
  font-size: 10px;
  font-weight: 700;
  color: var(--muted);
}
.div-line { height: 1px; flex: 1; background: var(--border); }

.input-card, .tech-card, .output-section, .test-summary, .done-card, .cached-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
}

.input-card { padding: 18px 20px; margin-bottom: 14px; }
.input-card h3 { margin: 0 0 4px; font-size: 18px; color: var(--text); }
.input-card p { margin: 0; color: var(--muted); font-size: 13px; }

.flow {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 10px;
}
.flow-node {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 7px 12px;
  font-size: 12px;
  color: #bfd0f2;
  background: var(--surface-2);
}
.flow-node.fn-active {
  border-color: rgba(45, 212, 191, 0.55);
  color: #b7fff5;
  background: rgba(45, 212, 191, 0.1);
}
.flow-arrow { color: #7f91b6; font-size: 12px; }

.tech-card { padding: 16px 18px; margin-bottom: 16px; }
.tech-card h4 { margin: 0 0 6px; color: #aff4ea; font-size: 18px; }
.tech-card p { margin: 0; color: var(--muted); font-size: 14px; line-height: 1.56; }

.stTextArea textarea {
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  background: #0f1728 !important;
  color: var(--text) !important;
  font-size: 14px !important;
}
.stTextArea { margin-bottom: 8px !important; }
.stTextArea textarea::placeholder { color: #7284aa !important; }
.stTextArea textarea:focus {
  border-color: rgba(45, 212, 191, 0.55) !important;
  box-shadow: 0 0 0 3px rgba(45, 212, 191, 0.14) !important;
}
.stTextArea [data-testid="InputInstructions"] {
  position: absolute !important;
  bottom: 8px !important;
  right: 12px !important;
  color: var(--muted) !important;
  font-size: 11px !important;
  opacity: 0.7 !important;
}

.stFileUploader [data-testid="stFileUploaderDropzone"] {
  background: #0f1728 !important;
  border: 1px dashed #3a4868 !important;
  border-radius: 12px !important;
}
.stFileUploader { margin-top: 6px !important; }
.stFileUploader [data-testid="stFileUploaderDropzone"]:hover {
  border-color: rgba(45, 212, 191, 0.55) !important;
  background: #101b2f !important;
}

.stRadio label { color: var(--text) !important; }
.stCaption { color: var(--muted) !important; font-size: 12px !important; }

.stButton > button[kind="primary"] {
  border: none !important;
  background: linear-gradient(135deg, var(--accent), #22d3ee) !important;
  color: #06212a !important;
  font-weight: 800 !important;
  border-radius: 12px !important;
  transition: transform .15s ease !important;
}
.stButton > button[kind="primary"]:hover { transform: translateY(-1px); }

.stDownloadButton > button {
  border: 1px solid rgba(45, 212, 191, 0.4) !important;
  background: rgba(45, 212, 191, 0.08) !important;
  color: #b7fff5 !important;
  border-radius: 12px !important;
}

.stProgress > div > div > div > div {
  background: linear-gradient(90deg, var(--accent), #60a5fa) !important;
}
.stProgress > div > div > div { background: #1a2440 !important; }

.step {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  margin: 8px 0;
}
.step-run { background: rgba(45, 212, 191, 0.14); border: 1px solid rgba(45, 212, 191, 0.35); color: #9df5e8; }
.step-ok { background: rgba(52, 211, 153, 0.14); border: 1px solid rgba(52, 211, 153, 0.35); color: #98f4cd; }
.step-fail { background: rgba(248, 113, 113, 0.14); border: 1px solid rgba(248, 113, 113, 0.35); color: #ffb7b7; }
.step-warn { background: rgba(245, 158, 11, 0.14); border: 1px solid rgba(245, 158, 11, 0.35); color: #ffd18a; }

.output-section { margin: 10px 0 6px; padding: 12px 14px 6px; }
.output-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 10px;
}
.output-section-icon {
  width: 24px;
  height: 24px;
  border-radius: 7px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #fff;
  font-size: 11px;
}
.output-section-title { font-size: 13px; font-weight: 700; color: var(--text); }
.output-section-subtitle {
  margin-left: auto;
  color: var(--muted);
  font-family: var(--mono);
  font-size: 11px;
}
.output-section.os-coder .output-section-icon { background: #0ea5a0; }
.output-section.os-tester .output-section-icon { background: #3b82f6; }
.output-section.os-reviewer .output-section-icon { background: #a855f7; }
.output-section.os-docs .output-section-icon { background: #22c55e; }

.verdict-badge {
  margin-left: auto;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.3px;
}
.verdict-approved { background: rgba(52, 211, 153, 0.15); border: 1px solid rgba(52, 211, 153, 0.35); color: #98f4cd; }
.verdict-rejected { background: rgba(248, 113, 113, 0.15); border: 1px solid rgba(248, 113, 113, 0.35); color: #ffb7b7; }

.test-summary { padding: 14px; margin: 10px 0; }
.test-summary.ts-pass { border-color: rgba(52, 211, 153, 0.35); }
.test-summary.ts-fail { border-color: rgba(248, 113, 113, 0.35); }
.test-summary.ts-warn { border-color: rgba(245, 158, 11, 0.35); }

.ts-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.ts-status-icon {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}
.ts-pass .ts-status-icon { background: rgba(52, 211, 153, 0.15); color: #9df5d2; }
.ts-fail .ts-status-icon { background: rgba(248, 113, 113, 0.15); color: #ffb7b7; }
.ts-warn .ts-status-icon { background: rgba(245, 158, 11, 0.15); color: #ffd18a; }
.ts-title { font-weight: 700; }
.ts-pass .ts-title { color: #9df5d2; }
.ts-fail .ts-title { color: #ffb7b7; }
.ts-warn .ts-title { color: #ffd18a; }
.ts-attempt {
  margin-left: auto;
  font-size: 11px;
  color: var(--muted);
  font-family: var(--mono);
}
.ts-stats { display: flex; gap: 8px; margin-bottom: 10px; }
.ts-stat {
  flex: 1;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--surface-2);
  padding: 8px;
  text-align: center;
}
.ts-stat-value { font-family: var(--mono); font-size: 20px; font-weight: 700; }
.ts-stat-value.sv-pass { color: #9df5d2; }
.ts-stat-value.sv-fail { color: #ffb7b7; }
.ts-stat-value.sv-total { color: var(--text); }
.ts-stat-label { font-size: 10px; letter-spacing: 1px; color: var(--muted); text-transform: uppercase; }
.ts-bar-track { height: 6px; border-radius: 10px; background: #1c2742; overflow: hidden; }
.ts-bar-fill { height: 100%; }
.ts-bar-fill.bf-pass { background: #34d399; }
.ts-bar-fill.bf-partial { background: #60a5fa; }

.done-card {
  margin: 20px 0 10px;
  padding: 24px 18px;
  text-align: center;
  border-color: rgba(45, 212, 191, 0.42);
}
.done-icon {
  width: 46px;
  height: 46px;
  border-radius: 999px;
  margin: 0 auto 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(52, 211, 153, 0.16);
  color: #9df5d2;
  font-size: 20px;
}
.done-card h3 { margin: 0; color: var(--text); }
.done-card p { margin: 6px 0 0; color: var(--muted); }
.done-card strong { color: #c2fff6; }
.done-stats { display: flex; justify-content: center; gap: 30px; margin-top: 16px; }
.done-stat-value { font-family: var(--mono); font-size: 22px; font-weight: 700; color: var(--text); }
.done-stat-value.dsv-green { color: #9df5d2; }
.done-stat-value.dsv-acc { color: #9fd2ff; }
.done-stat-label { font-size: 10px; letter-spacing: 1px; color: var(--muted); text-transform: uppercase; }

.stCodeBlock {
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  max-width: calc(100vw - 440px) !important;
  overflow: hidden !important;
}
.stCodeBlock code {
  white-space: pre !important;
  overflow-x: auto !important;
  display: block !important;
}
.stMarkdown {
  max-width: calc(100vw - 440px) !important;
  overflow-wrap: break-word !important;
  word-break: break-word !important;
}
div[data-testid="stVerticalBlock"] > div {
  min-width: 0 !important;
  max-width: 100% !important;
}

.crew-log {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: #0f1728;
  padding: 12px;
  max-height: 320px;
  overflow-y: auto;
  font-family: var(--mono);
  font-size: 12px;
  color: #bfd0f2;
  white-space: pre-wrap;
}

.cached-card { padding: 14px; }
.cached-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
}
.cached-card-title { font-size: 14px; font-weight: 700; color: var(--text); }
.cached-card-badge {
  margin-left: auto;
  padding: 2px 9px;
  border: 1px solid rgba(52, 211, 153, 0.35);
  border-radius: 999px;
  font-size: 10px;
  color: #9df5d2;
  background: rgba(52, 211, 153, 0.14);
}

.pipe-spacer { height: 12px; }
.pipe-section {
  margin: 16px 0;
  border-top: 1px dashed var(--border);
  padding-top: 12px;
}
.workspace-shell {
  margin: 18px 0 10px;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--surface);
  padding: 16px;
  max-width: 100%;
  overflow: hidden;
}
.workspace-title {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  color: var(--text);
}
.workspace-sub {
  margin: 4px 0 12px;
  color: var(--muted);
  font-size: 12px;
}
.workspace-pane {
  margin-top: 12px;
  max-width: 100%;
  overflow-x: auto;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

div[role="radiogroup"] {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 8px;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 6px;
  background: rgba(15, 23, 40, 0.9);
}
div[role="radiogroup"] > label {
  margin: 0 !important;
  border: 1px solid transparent;
  border-radius: 10px;
  background: transparent;
  padding: 4px 10px 4px 6px;
  transition: background .15s ease, border-color .15s ease;
}
div[role="radiogroup"] > label:hover {
  background: rgba(96, 165, 250, 0.12);
  border-color: rgba(96, 165, 250, 0.35);
}
div[role="radiogroup"] > label:has(input:checked) {
  background: rgba(45, 212, 191, 0.14);
  border-color: rgba(45, 212, 191, 0.45);
}

.app-footer {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  text-align: center;
  color: var(--muted);
  font-size: 11px;
}
.app-footer a { color: #93fff1; text-decoration: none; }

/* Custom right-side pipeline board */
.pipeline-board {
  position: fixed;
  right: 18px;
  top: 18px;
  width: 352px;
  max-height: calc(100vh - 36px);
  overflow: auto;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: linear-gradient(180deg, rgba(16, 24, 43, 0.96), rgba(11, 17, 31, 0.96));
  padding: 14px;
  z-index: 999;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.45);
}
.pb-title {
  font-size: 13px;
  letter-spacing: 1.8px;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 8px;
  font-weight: 700;
}
.pb-project {
  font-size: 14px;
  color: var(--text);
  margin-bottom: 12px;
  font-weight: 700;
}
.pb-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 10px;
}
.pb-stat {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 8px;
  background: var(--surface-2);
}
.pb-stat-v {
  color: var(--text);
  font-family: var(--mono);
  font-size: 16px;
  font-weight: 700;
}
.pb-stat-k {
  color: var(--muted);
  font-size: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
}
.agent-stack {
  display: grid;
  gap: 12px;
}
.agent-card {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: rgba(23, 31, 52, 0.7);
  padding: 10px 11px;
}
.agent-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.agent-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  border: 1px solid transparent;
}
.agent-name {
  color: var(--text);
  font-size: 13px;
  font-weight: 700;
}
.agent-state {
  margin-left: auto;
  font-size: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--muted);
}
.agent-desc {
  font-size: 12px;
  color: var(--muted);
}
.agent-events {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.agent-ev {
  border-radius: 8px;
  padding: 6px 8px;
  font-size: 11px;
  line-height: 1.35;
  border: 1px solid var(--border);
  background: rgba(148, 163, 184, 0.08);
  color: #c7d2e8;
}
.ev-running {
  border-color: rgba(45, 212, 191, 0.38);
  background: rgba(45, 212, 191, 0.12);
  color: #b7fff5;
}
.ev-done {
  border-color: rgba(52, 211, 153, 0.38);
  background: rgba(52, 211, 153, 0.12);
  color: #b7ffd8;
}
.ev-fail {
  border-color: rgba(248, 113, 113, 0.38);
  background: rgba(248, 113, 113, 0.12);
  color: #ffd0d0;
}
.ev-warn {
  border-color: rgba(245, 158, 11, 0.38);
  background: rgba(245, 158, 11, 0.12);
  color: #ffe1ad;
}
.ac-idle .agent-dot { background: #334155; border-color: #475569; }
.ac-idle .agent-state { color: #94a3b8; }
.ac-running { border-color: rgba(45, 212, 191, 0.45); }
.ac-running .agent-dot {
  background: #2dd4bf;
  border-color: #99f6e4;
  box-shadow: 0 0 12px rgba(45, 212, 191, 0.65);
}
.ac-running .agent-state { color: #99f6e4; }
.ac-done { border-color: rgba(52, 211, 153, 0.45); }
.ac-done .agent-dot { background: #34d399; border-color: #a7f3d0; }
.ac-done .agent-state { color: #a7f3d0; }
.ac-fail { border-color: rgba(248, 113, 113, 0.45); }
.ac-fail .agent-dot { background: #f87171; border-color: #fecaca; }
.ac-fail .agent-state { color: #fecaca; }
.ac-warn { border-color: rgba(245, 158, 11, 0.45); }
.ac-warn .agent-dot { background: #f59e0b; border-color: #fde68a; }
.ac-warn .agent-state { color: #fde68a; }

@media (max-width: 1200px) {
  .block-container {
    width: 100% !important;
    max-width: 1120px !important;
    margin: 0 auto !important;
    padding: 20px 16px 48px !important;
  }
  .pipeline-board {
    position: relative;
    right: auto;
    top: auto;
    width: 100%;
    max-height: none;
    margin-bottom: 14px;
  }
}

@media (max-width: 1536px) {
  html { font-size: 14px; }
  .topbar-brand { font-size: 18px; }
  .hero { padding: 28px 24px; }
  .hero h1 { font-size: clamp(26px, 3.8vw, 44px); }
  .hero-sub { font-size: 14px; }
  .pb-stat-v { font-size: 14px; }
  .agent-name { font-size: 12px; }
  .agent-desc { font-size: 11px; }
}

@media (max-width: 780px) {
  .topbar { flex-direction: column; align-items: flex-start; }
  .topbar-pills { width: 100%; }
  .hero { padding: 24px 18px; }
  .ts-stats, .done-stats { flex-direction: column; gap: 10px; }
}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
#  UTILITIES  (100% unchanged from working version)
# ------------------------------------------------------------------------------
def sanitize_filename(n):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', n.strip())[:80]

def save_output(d, f, c):
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f), "w", encoding="utf-8") as fh:
        fh.write(c if isinstance(c, str) else str(c))

def create_zip(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for n, c in files.items():
            zf.writestr(n, c)
    buf.seek(0)
    return buf.getvalue()

def strip_fences(t):
    s = t.strip()
    if s.startswith("```"):
        nl = s.find("\n")
        if nl != -1: s = s[nl + 1:]
        if s.rstrip().endswith("```"): s = s.rstrip()[:-3].rstrip()
    return s

def _txt(x):
    if isinstance(x, str): return x
    for a in ("raw", "final_output", "output", "result", "content"):
        if hasattr(x, a):
            v = getattr(x, a)
            if isinstance(v, str) and v.strip(): return v
    return str(x)

def run_agent(factory, *args):
    agent = factory.create()
    task = factory.get_task(agent, *args)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        out = crew.kickoff()
    return _txt(out), log.getvalue()

def run_tests(d):
    tp = os.path.join(d, "tests.py")
    if not os.path.exists(tp): return False, "tests.py not found."
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pytest", "--maxfail=5", "--disable-warnings", "-q", tp],
            capture_output=True, text=True, cwd=d, timeout=120)
        return r.returncode == 0, (r.stdout or "") + "\n" + (r.stderr or "")
    except subprocess.TimeoutExpired: return False, "Tests timed out (120s)."
    except Exception as e: return False, str(e)

def parse_test_results(output):
    """Parse pytest -q output into structured result counts."""
    result = {"passed": 0, "failed": 0, "errors": 0, "total": 0,
              "summary_line": "", "status": "unknown"}
    if not output or not output.strip():
        return result
    if "timed out" in output.lower() or "Tests timed out" in output:
        result["status"] = "timeout"
        result["summary_line"] = "Tests timed out (120s)"
        return result
    if "tests.py not found" in output.lower():
        result["status"] = "error"
        result["summary_line"] = "tests.py not found"
        return result
    if "INTERNALERROR" in output:
        result["status"] = "error"
        result["errors"] = 1
        result["total"] = 1
        # Extract the actual error message
        for line in output.splitlines():
            if "Error" in line or "error" in line.lower():
                result["summary_line"] = line.replace("INTERNALERROR>", "").strip()
                break
        if not result["summary_line"]:
            result["summary_line"] = "pytest INTERNALERROR (possible module name conflict)"
        return result
    passed_m = re.search(r'(\d+)\s+passed', output)
    failed_m = re.search(r'(\d+)\s+failed', output)
    error_m = re.search(r'(\d+)\s+error', output)
    if passed_m: result["passed"] = int(passed_m.group(1))
    if failed_m: result["failed"] = int(failed_m.group(1))
    if error_m: result["errors"] = int(error_m.group(1))
    result["total"] = result["passed"] + result["failed"] + result["errors"]
    for line in reversed(output.strip().splitlines()):
        line = line.strip()
        if line and ("passed" in line or "failed" in line or "error" in line):
            result["summary_line"] = line
            break
    if result["total"] == 0:
        result["status"] = "unknown"
    elif result["failed"] > 0 or result["errors"] > 0:
        result["status"] = "failed"
    else:
        result["status"] = "passed"
    return result

def _render_test_summary(tr, attempt, max_attempts, mode):
    """Render a styled test results summary card."""
    css_cls = {"pass": "ts-pass", "fail": "ts-fail", "warn": "ts-warn"}[mode]
    icon = {"pass": "&#10003;", "fail": "&#10007;", "warn": "!"}[mode]
    title = {"pass": "All Tests Passed", "fail": "Tests Failed",
             "warn": "Tests Incomplete \u2014 Proceeding"}[mode]
    passed = tr["passed"]
    failed = tr["failed"] + tr["errors"]
    total = tr["total"]
    pct = int((passed / total * 100) if total > 0 else 0)
    bar_cls = "bf-pass" if mode == "pass" else "bf-partial"
    st.markdown(f"""
    <div class="test-summary {css_cls}">
      <div class="ts-header">
        <div class="ts-status-icon">{icon}</div>
        <span class="ts-title">{title}</span>
        <span class="ts-attempt">Attempt {attempt}/{max_attempts}</span>
      </div>
      <div class="ts-stats">
        <div class="ts-stat">
          <div class="ts-stat-value sv-pass">{passed}</div>
          <div class="ts-stat-label">Passed</div>
        </div>
        <div class="ts-stat">
          <div class="ts-stat-value sv-fail">{failed}</div>
          <div class="ts-stat-label">Failed</div>
        </div>
        <div class="ts-stat">
          <div class="ts-stat-value sv-total">{total}</div>
          <div class="ts-stat-label">Total</div>
        </div>
      </div>
      <div class="ts-bar-track">
        <div class="ts-bar-fill {bar_cls}" style="width: {pct}%;"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

PIPELINE_AGENTS = [
    ("coder", "Coder Agent", "Generates the implementation."),
    ("tester", "Tester Agent", "Builds and refreshes pytest cases."),
    ("testloop", "Test Runner", "Executes tests across retry attempts."),
    ("bugfix", "BugFix Agent", "Proposes targeted fixes from failures."),
    ("reviewer", "Reviewer Agent", "Approves or rejects proposed fixes."),
    ("docs", "Docs Agent", "Generates final documentation."),
]


def _new_pipeline_state():
    return {k: "idle" for k, _, _ in PIPELINE_AGENTS}


def _new_pipeline_events():
    return {k: [] for k, _, _ in PIPELINE_AGENTS}


def _new_run_artifacts():
    return {
        "project": "",
        "code": "",
        "tests_by_attempt": [],
        "reviews_by_attempt": [],
        "docs": "",
    }


def _push_agent_event(agent_key, text, kind="idle"):
    events = st.session_state.setdefault("pipeline_events", _new_pipeline_events())
    bucket = events.setdefault(agent_key, [])
    bucket.append({"text": text, "kind": kind})
    if len(bucket) > 8:
        del bucket[:-8]


def _pipeline_html(state, project_name="", attempt=0, tr=None, events=None):
    done_count = sum(1 for _, v in state.items() if v == "done")
    total = len(PIPELINE_AGENTS)
    test_stats = f'{tr.get("passed", 0)}/{tr.get("total", 0)}' if tr else "-"
    events = events or _new_pipeline_events()
    cards = []
    for key, name, desc in PIPELINE_AGENTS:
        stt = state.get(key, "idle")
        event_rows = events.get(key, [])
        event_html = "".join(
            f'<div class="agent-ev ev-{e.get("kind", "idle")}">{html.escape(e.get("text", ""))}</div>'
            for e in event_rows
        )
        cards.append(
            f'<div class="agent-card ac-{stt}"><div class="agent-head"><span class="agent-dot"></span><span class="agent-name">{name}</span><span class="agent-state">{stt}</span></div><div class="agent-desc">{desc}</div><div class="agent-events">{event_html}</div></div>'
        )
    project_line = project_name if project_name else "No active run"
    return (
        f'<aside class="pipeline-board">'
        f'<div class="pb-title">Live Pipeline</div>'
        f'<div class="pb-project">{project_line}</div>'
        f'<div class="pb-stats">'
        f'<div class="pb-stat"><div class="pb-stat-v">{done_count}/{total}</div><div class="pb-stat-k">Stages Complete</div></div>'
        f'<div class="pb-stat"><div class="pb-stat-v">{attempt if attempt else "-"}</div><div class="pb-stat-k">Attempt</div></div>'
        f'<div class="pb-stat"><div class="pb-stat-v">{test_stats}</div><div class="pb-stat-k">Tests Passed</div></div>'
        f'<div class="pb-stat"><div class="pb-stat-v">{state.get("testloop", "idle").upper()}</div><div class="pb-stat-k">Test State</div></div>'
        f'</div>'
        f'<div class="agent-stack">{"".join(cards)}</div>'
        f'</aside>'
    )


if "crew_log" not in st.session_state:
    st.session_state["crew_log"] = ""
if "pipeline_state" not in st.session_state:
    st.session_state["pipeline_state"] = _new_pipeline_state()
if "pipeline_attempt" not in st.session_state:
    st.session_state["pipeline_attempt"] = 0
if "pipeline_events" not in st.session_state:
    st.session_state["pipeline_events"] = _new_pipeline_events()
if "run_artifacts" not in st.session_state:
    st.session_state["run_artifacts"] = _new_run_artifacts()
if "active_view" not in st.session_state:
    st.session_state["active_view"] = "Code"

pipeline_holder = st.empty()


def _push_pipeline(project_name="", tr=None):
    pipeline_holder.markdown(
        _pipeline_html(
            st.session_state["pipeline_state"],
            project_name=project_name,
            attempt=st.session_state.get("pipeline_attempt", 0),
            tr=tr,
            events=st.session_state.get("pipeline_events"),
        ),
        unsafe_allow_html=True,
    )


_push_pipeline(
    project_name=st.session_state.get("project_files", {}).get("name", ""),
    tr=st.session_state.get("test_results"),
)


def _render_workspace():
    art = st.session_state.get("run_artifacts") or {}
    if not art.get("project"):
        return

    st.markdown(f"""
    <div class="divider">
      <div class="div-dot"></div>
      <span class="div-text">{art["project"]}</span>
      <div class="div-line"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="workspace-shell">
      <h3 class="workspace-title">Run Outputs</h3>
      <p class="workspace-sub">Use the navbar to switch between code, tests, reviews, and docs.</p>
    </div>
    """, unsafe_allow_html=True)

    views = ["Code", "Tests", "Reviews", "Docs"]
    if st.session_state.get("active_view") not in views:
        st.session_state["active_view"] = "Code"
    active = st.radio(
        "Output View",
        views,
        horizontal=True,
        label_visibility="collapsed",
        key="active_view",
    )
    st.markdown('<div class="workspace-pane"></div>', unsafe_allow_html=True)

    if active == "Code":
        st.markdown("""
        <div class="output-section os-coder">
          <div class="output-section-header">
            <div class="output-section-icon">C</div>
            <span class="output-section-title">Generated Code</span>
            <span class="output-section-subtitle">main.py</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.code(art.get("code", ""), language="python")

    elif active == "Tests":
        test_rows = art.get("tests_by_attempt", [])
        if not test_rows:
            st.info("No test attempts recorded yet.")
        else:
            opts = [f"Attempt {r['attempt']}" for r in test_rows]
            choice = st.selectbox("Attempt", opts, label_visibility="collapsed")
            row = test_rows[opts.index(choice)]
            tr = row.get("result", {})
            mode = "pass" if tr.get("status") == "passed" else ("warn" if tr.get("status") == "unknown" else "fail")
            _render_test_summary(tr, row.get("attempt", 1), max(1, len(test_rows)), mode)
            st.markdown("""
            <div class="output-section os-tester">
              <div class="output-section-header">
                <div class="output-section-icon">T</div>
                <span class="output-section-title">Tests Used In This Attempt</span>
                <span class="output-section-subtitle">tests.py</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
            st.code(row.get("tests", ""), language="python")
            with st.expander("Raw pytest output"):
                st.text(row.get("output", ""))

    elif active == "Reviews":
        review_rows = art.get("reviews_by_attempt", [])
        if not review_rows:
            st.info("No review attempts were needed.")
        else:
            opts = [f"Attempt {r['attempt']} - {r['verdict']}" for r in review_rows]
            choice = st.selectbox("Review Attempt", opts, label_visibility="collapsed")
            row = review_rows[opts.index(choice)]
            verdict_cls = "verdict-approved" if row.get("verdict") == "APPROVED" else "verdict-rejected"
            st.markdown(f"""
            <div class="output-section os-reviewer">
              <div class="output-section-header">
                <div class="output-section-icon">R</div>
                <span class="output-section-title">Code Review - Attempt {row.get("attempt", "-")}</span>
                <span class="verdict-badge {verdict_cls}">{row.get("verdict", "UNKNOWN")}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(row.get("review", ""))
            if row.get("fix"):
                with st.expander("Proposed fix for this attempt"):
                    st.code(row.get("fix", ""), language="python")

    else:
        st.markdown("""
        <div class="output-section os-docs">
          <div class="output-section-header">
            <div class="output-section-icon">D</div>
            <span class="output-section-title">Generated Documentation</span>
            <span class="output-section-subtitle">docs.md</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            st.markdown(art.get("docs", ""))


# ------------------------------------------------------------------------------
#  TOP BAR
# ------------------------------------------------------------------------------
st.markdown("""
<div class="topbar">
  <div class="topbar-left">
    <div class="topbar-logo">DF</div>
    <span class="topbar-brand">DevFlow<span>AI</span></span>
  </div>
  <div class="topbar-pills">
    <span class="pill pill-acc">Python Only</span>
    <span class="pill pill-acc">Local UI refresh</span>
    <span class="pill pill-green">5 Agents</span>
    <span class="pill">CrewAI</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
#  HERO
# ------------------------------------------------------------------------------
st.markdown("""
<div class="hero">
  <h1>Build Features. <span>Verify Fast.</span></h1>
  <p class="hero-sub">Describe what you want, then let a coordinated agent pipeline generate code, tests, fixes, reviews, and docs. The backend flow stays the same; this redesign is focused on clarity while the run is in progress.</p>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
#  AGENTS GRID
# ------------------------------------------------------------------------------
st.markdown("""
<div class="agents-grid">
  <div class="ag">
    <div class="ag-icon ic">C</div>
    <h4>Coder</h4>
    <p>Implements the requested feature in Python.</p>
  </div>
  <div class="ag">
    <div class="ag-icon it">T</div>
    <h4>Tester</h4>
    <p>Generates pytest coverage for the behavior.</p>
  </div>
  <div class="ag">
    <div class="ag-icon ib">B</div>
    <h4>BugFix</h4>
    <p>Analyzes failures and proposes targeted fixes.</p>
  </div>
  <div class="ag">
    <div class="ag-icon ir">R</div>
    <h4>Reviewer</h4>
    <p>Approves or rejects each proposed patch.</p>
  </div>
  <div class="ag">
    <div class="ag-icon id">D</div>
    <h4>Docs</h4>
    <p>Produces final docs after code stabilizes.</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
#  INPUT SECTION
# ------------------------------------------------------------------------------
st.markdown("""
<div class="divider">
  <div class="div-dot"></div>
  <span class="div-text">Build Input</span>
  <div class="div-line"></div>
</div>
<div class="input-card">
  <h3>Describe your feature or upload code</h3>
  <p>Keep prompts concrete. You can also upload a ZIP or multiple Python files for incremental improvements. This is a simple demo, so keep your uploads to simple python projects.</p>
</div>
""", unsafe_allow_html=True)

feature_prompt = st.text_area(
    "prompt", height=90,
    placeholder="e.g. Create a bank account system with deposit, withdraw, transfer, and transaction history...",
    label_visibility="collapsed",
)

left_col, mid_col, right_col = st.columns([5, 1, 3])
with left_col:
    umode = st.radio("fmt", ["ZIP archive", "Python files (.py)"],
                     horizontal=True, label_visibility="collapsed")
    if umode == "ZIP archive":
        uploaded_zip = st.file_uploader("zip", type=["zip"], label_visibility="collapsed")
        uploaded_py = None
    else:
        uploaded_py = st.file_uploader("py", type=["py"],
                                       accept_multiple_files=True, label_visibility="collapsed")
        uploaded_zip = None
with right_col:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    run_btn = st.button("Run Pipeline", type="primary", use_container_width=True)

st.caption("Generates a single Python file with tests and documentation.")


# ------------------------------------------------------------------------------
#  PIPELINE VISUALIZATION
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
#  RESULTS (from session)
# ------------------------------------------------------------------------------
if "project_files" in st.session_state and not run_btn:
    if not st.session_state.get("run_artifacts", {}).get("project"):
        proj = st.session_state["project_files"]
        st.session_state["run_artifacts"] = {
            "project": proj.get("name", ""),
            "code": proj.get("files", {}).get("main.py", ""),
            "tests_by_attempt": [],
            "reviews_by_attempt": [],
            "docs": proj.get("files", {}).get("docs.md", ""),
        }
    _render_workspace()
    st.download_button(
        "Download Project (.zip)",
        data=create_zip(st.session_state["project_files"]["files"]),
        file_name=f"{st.session_state['project_files']['name']}.zip",
        mime="application/zip",
        use_container_width=True,
    )

    if st.session_state.get("crew_log"):
        with st.expander("CrewAI Agent Log"):
            st.markdown(
                f'<div class="crew-log">{html.escape(st.session_state["crew_log"])}</div>',
                unsafe_allow_html=True)


#  PIPELINE EXECUTION  (100% unchanged logic)
# ------------------------------------------------------------------------------
if run_btn:
    st.session_state.pop("project_files", None)
    st.session_state["crew_log"] = ""
    st.session_state["pipeline_state"] = _new_pipeline_state()
    st.session_state["pipeline_events"] = _new_pipeline_events()
    st.session_state["pipeline_attempt"] = 0
    st.session_state["run_artifacts"] = _new_run_artifacts()
    st.session_state["active_view"] = "Code"
    _push_pipeline()
    logs = []

    has_up = (uploaded_zip is not None) or (uploaded_py and len(uploaded_py) > 0)
    if has_up:
        pname = sanitize_filename(
            (uploaded_zip.name.replace(".zip", "") if uploaded_zip
             else uploaded_py[0].name.replace(".py", "")) or "project")
    else:
        if not feature_prompt.strip():
            st.error("Enter a feature request or upload code.")
            st.stop()
        pname = sanitize_filename(feature_prompt)

    tmp = tempfile.mkdtemp(prefix="devflow_")
    pdir = os.path.join(tmp, pname)
    os.makedirs(pdir, exist_ok=True)

    try:
        # Resolve prompt
        if uploaded_zip:
            with zipfile.ZipFile(uploaded_zip, "r") as zr:
                zr.extractall(pdir)
            ctx = []
            for root, _, files in os.walk(pdir):
                for f in files:
                    if f.endswith(".py") and f != "tests.py" and not f.startswith("test_") and not f.endswith("_test.py"):
                        fp = os.path.join(root, f)
                        with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                            ctx.append(f"\n# File: {os.path.relpath(fp, pdir)}\n{fh.read()}")
            # Clean out ALL original zip files to prevent name collisions
            # (e.g. code.py shadows Python stdlib 'code' module, crashing pytest)
            for item in os.listdir(pdir):
                item_path = os.path.join(pdir, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path) and item == "__pycache__":
                    shutil.rmtree(item_path, ignore_errors=True)
            full_prompt = f"{feature_prompt.strip() or 'Improve the project'}\n\nExisting code:\n{''.join(ctx)}"
        elif uploaded_py and len(uploaded_py) > 0:
            ctx = []
            for uf in uploaded_py:
                ctx.append(f"\n# File: {uf.name}\n{uf.read().decode('utf-8', errors='ignore')}")
            full_prompt = f"{feature_prompt.strip() or 'Improve the code'}\n\nExisting code:\n{''.join(ctx)}"
        else:
            full_prompt = feature_prompt.strip()

        st.markdown(f"""
        <div class="divider">
          <div class="div-dot"></div>
          <span class="div-text">Running &mdash; {pname}</span>
        <div class="div-line"></div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state["run_artifacts"]["project"] = pname
        _push_pipeline(project_name=pname)
        prog = st.progress(0, text="Starting...")

# ------------------------------------------------------------------------------
        prog.progress(10, text="Coder Agent...")
        st.session_state["pipeline_state"]["coder"] = "running"
        _push_agent_event("coder", "Generating implementation", "running")
        _push_pipeline(project_name=pname)
        with st.spinner("Working..."):
            code, log = run_agent(CoderAgentFactory(), full_prompt)
            code = strip_fences(code)
            save_output(pdir, "main.py", code)
            logs.append(f"=== CODER ===\n{log}\n")
        st.session_state["run_artifacts"]["code"] = code
        st.session_state["pipeline_state"]["coder"] = "done"
        _push_agent_event("coder", "Code generated", "done")
        _push_pipeline(project_name=pname)

# ------------------------------------------------------------------------------
        prog.progress(30, text="Tester Agent...")
        st.session_state["pipeline_state"]["tester"] = "running"
        _push_agent_event("tester", "Generating tests from code", "running")
        _push_pipeline(project_name=pname)
        with st.spinner("Working..."):
            tests, log = run_agent(TesterAgentFactory(), code)
            tests = strip_fences(tests)
            save_output(pdir, "tests.py", tests)
            logs.append(f"=== TESTER ===\n{log}\n")
        st.session_state["pipeline_state"]["tester"] = "done"
        _push_agent_event("tester", "tests.py generated", "done")
        _push_pipeline(project_name=pname)

# ------------------------------------------------------------------------------
        st.session_state["run_artifacts"]["code"] = code

# ------------------------------------------------------------------------------
        st.markdown('<div class="pipe-section"></div>', unsafe_allow_html=True)
        prog.progress(50, text="Running tests...")
        mx = 3
        final_test_results = None
        final_test_attempt = 0
        agents_ran = 2  # Coder + Tester already ran
        for att in range(1, mx + 1):
            st.session_state["pipeline_attempt"] = att
            st.session_state["pipeline_state"]["testloop"] = "running"
            _push_agent_event("testloop", f"Attempt {att}: running pytest", "running")
            _push_pipeline(project_name=pname, tr=final_test_results)
            ok, tout = run_tests(pdir)
            logs.append(f"=== TEST {att} ===\n{tout}\n")

            tr = parse_test_results(tout)
            # Use parsed results for success: if we found tests and none failed, it's a pass
            # (returncode can be non-zero due to warnings/deprecation even when all tests pass)
            if tr.get("total", 0) > 0 and tr.get("failed", 0) == 0 and tr.get("errors", 0) == 0:
                ok = True
            final_test_results = tr
            final_test_attempt = att
            st.session_state["run_artifacts"]["tests_by_attempt"].append(
                {"attempt": att, "tests": tests, "result": tr, "output": tout}
            )

            if ok:
                st.session_state["pipeline_state"]["testloop"] = "done"
                _push_agent_event(
                    "testloop",
                    f"Attempt {att}: passed {tr.get('passed', 0)}/{tr.get('total', 0)}",
                    "done",
                )
                _push_pipeline(project_name=pname, tr=tr)
                break
            if att == mx:
                st.session_state["pipeline_state"]["testloop"] = "warn"
                _push_agent_event(
                    "testloop",
                    f"Attempt {att}: max retries reached ({tr.get('failed', 0) + tr.get('errors', 0)} failing)",
                    "warn",
                )
                _push_pipeline(project_name=pname, tr=tr)
                break

            _push_agent_event(
                "testloop",
                f"Attempt {att}: {tr.get('failed', 0) + tr.get('errors', 0)} failed",
                "fail",
            )

# ------------------------------------------------------------------------------
            prog.progress(min(50 + att * 10, 80), text=f"BugFix (attempt {att})...")
            st.session_state["pipeline_state"]["bugfix"] = "running"
            _push_agent_event(
                "bugfix",
                f"Attempt {att}: received {tr.get('failed', 0) + tr.get('errors', 0)} failing tests",
                "warn",
            )
            _push_agent_event("bugfix", f"Attempt {att}: analyzing failures", "running")
            _push_pipeline(project_name=pname, tr=tr)
            with st.spinner("Working..."):
                fix, log = run_agent(BugFixAgentFactory(), code, tout)
                fix = strip_fences(fix)
                logs.append(f"=== BUGFIX {att} ===\n{log}\n")
            st.session_state["pipeline_state"]["bugfix"] = "done"
            _push_agent_event("bugfix", f"Attempt {att}: proposed patch", "done")
            _push_pipeline(project_name=pname, tr=tr)
            agents_ran += 1

            st.session_state["pipeline_state"]["reviewer"] = "running"
            _push_agent_event("reviewer", f"Attempt {att}: reviewing patch", "running")
            _push_pipeline(project_name=pname, tr=tr)
            rprompt = (
                f"Old Code:\n{code}\n\nProposed Fix:\n{fix}\n\n"
                "Approve if it fixes failures without breaking behavior.\n"
                "End with: VERDICT: APPROVED or VERDICT: REJECTED"
            )
            with st.spinner("Working..."):
                review, log = run_agent(ReviewerAgentFactory(), rprompt)
                logs.append(f"=== REVIEWER {att} ===\n{log}\n")
            agents_ran += 1

            m = re.search(r"VERDICT:\s*(APPROVED|REJECTED)", review, re.IGNORECASE)
            approved = bool(m and m.group(1).upper() == "APPROVED")
            verdict_text = "APPROVED" if approved else "REJECTED"
            review_display = re.sub(r'VERDICT:\s*(APPROVED|REJECTED)', '', review, flags=re.IGNORECASE).strip()
            st.session_state["run_artifacts"]["reviews_by_attempt"].append(
                {"attempt": att, "verdict": verdict_text, "review": review_display, "fix": fix}
            )

            if approved:
                st.session_state["pipeline_state"]["reviewer"] = "done"
                _push_agent_event("reviewer", f"Attempt {att}: approved", "done")
                code = fix
                save_output(pdir, "main.py", code)
                st.session_state["run_artifacts"]["code"] = code
                with st.spinner("Working..."):
                    tests, log = run_agent(TesterAgentFactory(), code)
                    tests = strip_fences(tests)
                    save_output(pdir, "tests.py", tests)
                    logs.append(f"=== TESTER REGEN ===\n{log}\n")
                st.session_state["pipeline_state"]["tester"] = "done"
                _push_agent_event("tester", f"Attempt {att}: tests regenerated", "done")
                _push_pipeline(project_name=pname, tr=tr)
            else:
                st.session_state["pipeline_state"]["reviewer"] = "warn"
                _push_agent_event("reviewer", f"Attempt {att}: rejected", "fail")
                _push_pipeline(project_name=pname, tr=tr)

# ------------------------------------------------------------------------------
        prog.progress(90, text="Docs Agent...")
        st.session_state["pipeline_state"]["docs"] = "running"
        _push_agent_event("docs", "Generating documentation", "running")
        _push_pipeline(project_name=pname, tr=final_test_results)
        with st.spinner("Working..."):
            docs, log = run_agent(DocsAgentFactory(), code)
            logs.append(f"=== DOCS ===\n{log}\n")
        st.session_state["pipeline_state"]["docs"] = "done"
        _push_agent_event("docs", "docs.md generated", "done")
        _push_pipeline(project_name=pname, tr=final_test_results)
        agents_ran += 1
        st.session_state["run_artifacts"]["docs"] = docs

# ------------------------------------------------------------------------------
        prog.progress(100, text="Complete")
        st.session_state["project_files"] = {
            "name": pname,
            "files": {"main.py": code, "tests.py": tests, "docs.md": docs},
        }
        st.session_state["run_artifacts"]["project"] = pname
        st.session_state["run_artifacts"]["code"] = code
        st.session_state["run_artifacts"]["docs"] = docs
        st.session_state["crew_log"] = "\n".join(logs)
        st.session_state["test_results"] = final_test_results
        st.session_state["test_attempt"] = final_test_attempt
        _push_pipeline(project_name=pname, tr=final_test_results)

        test_passed = final_test_results["passed"] if final_test_results else 0
        test_total = final_test_results["total"] if final_test_results else 0

        st.markdown(f"""
        <div class="done-card">
          <div class="done-icon">&#10003;</div>
          <h3>Pipeline Complete</h3>
          <p>All outputs generated for <strong>{pname}</strong></p>
          <div class="done-stats">
            <div class="done-stat">
              <div class="done-stat-value dsv-green">{test_passed}/{test_total}</div>
              <div class="done-stat-label">Tests Passed</div>
            </div>
            <div class="done-stat">
              <div class="done-stat-value dsv-acc">{final_test_attempt}</div>
              <div class="done-stat-label">Attempts</div>
            </div>
            <div class="done-stat">
              <div class="done-stat-value">{agents_ran}</div>
              <div class="done-stat-label">Agents Run</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        _render_workspace()
        st.download_button(
            "Download Project (.zip)",
            data=create_zip(st.session_state["project_files"]["files"]),
            file_name=f"{pname}.zip",
            mime="application/zip",
        )
        with st.expander("CrewAI Agent Log"):
            st.markdown(
                f'<div class="crew-log">{html.escape(st.session_state["crew_log"])}</div>',
                unsafe_allow_html=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------------------
#  FOOTER
# ------------------------------------------------------------------------------
st.markdown("""
<div class="app-footer">
  Built with <a href="https://github.com/crewAIInc/crewAI" target="_blank">CrewAI</a> &middot;
  <a href="https://groq.com" target="_blank">Groq</a> &middot;
  <a href="https://streamlit.io" target="_blank">Streamlit</a>
  <br>DevFlow.AI
</div>
""", unsafe_allow_html=True)
