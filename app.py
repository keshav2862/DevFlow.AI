# app.py
import os
import re
import sys
import zipfile
import subprocess
import streamlit as st
from dotenv import load_dotenv
from crewai import Crew, Process

from agents.coder_agent import CoderAgentFactory
from agents.tester_agent import TesterAgentFactory
from agents.reviewer_agent import ReviewerAgentFactory
from agents.docs_agent import DocsAgentFactory
from agents.bugfix_agent import BugFixAgentFactory  # ensure this file exists

load_dotenv()

# ----------------- Utilities -----------------
def sanitize_filename(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name.strip())

def save_output(project_dir: str, filename: str, content: str) -> str:
    os.makedirs(project_dir, exist_ok=True)
    path = os.path.join(project_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content if isinstance(content, str) else str(content))
    return path

def extract_zip(uploaded_file, target_dir: str):
    os.makedirs(target_dir, exist_ok=True)
    with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
        zip_ref.extractall(target_dir)

def _to_text(x):
    if isinstance(x, str):
        return x
    # Try common attrs CrewAI returns
    for attr in ("raw", "final_output", "output", "result", "content"):
        if hasattr(x, attr):
            v = getattr(x, attr)
            if isinstance(v, str) and v.strip():
                return v
    # Fallback
    return str(x)

def run_agent(factory, *task_args) -> str:
    agent = factory.create()
    task = factory.get_task(agent, *task_args)
    crew = Crew(
        agents=[agent],
        tasks=[task],
        model="groq/llama-3.1-8b-instant",
        process=Process.sequential,
        cache=True,
        verbose=True,
        planning=True,
        planning_llm=factory.llm
    )
    out = crew.kickoff()
    return _to_text(out)

def run_tests(project_dir: str):
    """Run pytest for the generated tests.py inside project_dir."""
    tests_path = os.path.join(project_dir, "tests.py")
    if not os.path.exists(tests_path):
        return False, "tests.py not found. TesterAgent may have failed to generate tests."

    try:
        # Use current interpreter to be sure we’re in the right venv
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--maxfail=5", "--disable-warnings", "-q", tests_path],
            capture_output=True,
            text=True,
            cwd=project_dir  # ensure tests import local code correctly
        )
        out = (result.stdout or "") + "\n" + (result.stderr or "")
        return result.returncode == 0, out
    except FileNotFoundError as e:
        return False, f"Pytest not found. Install it in your venv: pip install pytest\n\n{e}"
    except Exception as e:
        return False, str(e)

def gather_code_context(project_dir: str) -> str:
    """Collect .py contents from an uploaded project for Real-World mode."""
    context = []
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".py"):
                full = os.path.join(root, file)
                try:
                    rel = os.path.relpath(full, project_dir)
                except Exception:
                    rel = file
                with open(full, "r", encoding="utf-8", errors="ignore") as f:
                    context.append(f"\n\n# File: {rel}\n{f.read()}")
    return "".join(context)

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="DevFlow.AI", layout="wide")
st.title("🤖 DevFlow.AI - Multi-Agent AI Developer")

st.sidebar.header("Project Setup")
feature_prompt = st.sidebar.text_area("📝 Feature request", height=120, placeholder="Describe the feature you want…")
uploaded_project = st.sidebar.file_uploader("📂 Upload Existing Project (.zip)", type=["zip"])
run_pipeline = st.sidebar.button("🚀 Run Pipeline")

# Optional: pick an existing project to view
st.sidebar.header("Previous Projects")
if os.path.exists("projects"):
    previous = [""] + sorted(os.listdir("projects"))
else:
    previous = [""]
selected_project = st.sidebar.selectbox("📁 View Project", previous)

if selected_project:
    st.subheader(f"📂 Viewing: {selected_project}")
    proj_dir = os.path.join("projects", selected_project)
    if os.path.isdir(proj_dir):
        for fname in sorted(os.listdir(proj_dir)):
            fpath = os.path.join(proj_dir, fname)
            st.write(f"#### {fname}")
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
            if fname.endswith(".py"):
                st.code(content, language="python")
            elif fname.endswith((".md", ".txt")):
                st.markdown(content)
            else:
                st.text(content)
    else:
        st.info("No such project directory")

# ----------------- Run Pipeline -----------------
if run_pipeline:
    # Determine mode and project directory
    if uploaded_project is not None:
        # Real-World Project Mode
        project_name = sanitize_filename(uploaded_project.name.replace(".zip", "") or "uploaded_project")
        project_dir = os.path.join("projects", project_name)
        # Extract (only once per session run; harmless to re-extract)
        extract_zip(uploaded_project, project_dir)
        st.sidebar.success(f"✅ Project extracted to {project_dir}")

        code_context = gather_code_context(project_dir)
        user_goal = feature_prompt.strip() or "Improve the project"
        full_prompt = f"{user_goal}\n\nHere is the current project code context:\n{code_context}"
    else:
        # New Feature Mode
        if not feature_prompt.strip():
            st.error("Please enter a feature request or upload a project zip.")
            st.stop()
        project_name = sanitize_filename(feature_prompt)
        project_dir = os.path.join("projects", project_name)
        code_context = ""  # not used in new mode
        full_prompt = feature_prompt.strip()

    st.subheader(f"🚀 Running pipeline for: `{project_name}`")

    # Placeholders for progressive updates
    ph_code = st.empty()
    ph_tests = st.empty()
    ph_loop = st.empty()
    ph_review = st.empty()
    ph_docs = st.empty()

    # 1) Code generation
    ph_code.write("### 🛠 Generating code…")
    code = run_agent(CoderAgentFactory(), full_prompt)
    save_output(project_dir, "code.py", code)
    ph_code.code(code, language="python")

    # 2) Test generation
    ph_tests.write("### 🧪 Generating tests…")
    tests = run_agent(TesterAgentFactory(), code)
    save_output(project_dir, "tests.py", tests)
    ph_tests.code(tests, language="python")

    # 3) Test loop: BugFixAgent + ReviewerAgent (debate) before applying fixes
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        ph_loop.write(f"### 🔄 Running tests (Attempt {attempt}/{max_attempts})…")
        success, test_output = run_tests(project_dir)
        ph_loop.text(test_output)

        if success:
            ph_loop.success("✅ All tests passed!")
            break

        ph_loop.error("❌ Tests failed. BugFixAgent will propose a fix…")
        fixed_code = run_agent(BugFixAgentFactory(), code, test_output)

        ph_review.write("### 🔍 ReviewerAgent evaluating fix…")
        review_prompt = (
            f"Old Code:\n{code}\n\nProposed Fix:\n{fixed_code}\n\n"
            "Assess the proposed fix. If it resolves the failing tests without breaking other behavior, approve it; "
            "otherwise reject it and briefly say why.\n\n"
            "Respond with your comments, and end with EXACTLY one of the following on its own final line:\n"
            "VERDICT: APPROVED\n"
            "VERDICT: REJECTED"
        )
        review = run_agent(ReviewerAgentFactory(), review_prompt)
        ph_review.markdown(review)

        m = re.search(r"VERDICT:\s*(APPROVED|REJECTED)", review, re.IGNORECASE)
        approved = bool(m and m.group(1).upper() == "APPROVED")

        if approved:
            code = fixed_code
            save_output(project_dir, "code.py", code)
            ph_review.success("✅ Fix approved and applied.")
        else:
            ph_review.warning("⚠️ Fix rejected. BugFixAgent will try again…")

    # 4) Docs
    ph_docs.write("### 📄 Generating documentation…")
    docs = run_agent(DocsAgentFactory(), code)
    save_output(project_dir, "docs.md", docs)
    ph_docs.markdown(docs)

    st.success(f"🎉 Pipeline completed for project: {project_name}")
    st.info(f"Outputs saved in: `projects/{project_name}`")

    st.markdown("---")
    st.caption("Tip: If you see a pytest error about missing command, install it in your venv: `pip install pytest`")
