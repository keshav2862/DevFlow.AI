DevFlow.AI is a multi-agent AI system designed to automate the end-to-end software development workflow. It simulates a collaborative environment where agents specialize in different roles such as coding, testing, reviewing, documentation, and bug fixing.

🚀 Features

Coder Agent – Generates code based on user requirements

Tester Agent – Creates and runs test cases for generated code

Reviewer Agent – Reviews code for quality, style, and correctness

Docs Agent – Generates project documentation (usage, explanations)

Bugfix Agent – Identifies and fixes issues found during testing/review

Runner – Orchestrates the workflow and coordinates agents

Project Workspace – Stores generated projects with code, tests, docs, and reviews

Clone the repo

git clone https://github.com/keshav2862/DevFlow.AI
cd DevFlow.AI


Create a virtual environment & install dependencies

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt

▶️ Usage

Run the app to start the multi-agent system:

python app.py


Example: Generating a simple calculator project

python app.py "Build a calculator with 6 operations"


This will create a project folder in projects/ containing code.py, tests.py, docs.md, and review.md.

🧪 Testing

Each generated project contains test files (e.g., tests.py).
Run tests using:

pytest projects/YourProjectName/tests.py

🛠️ Technologies

Python 3.12

Multi-Agent Orchestration (custom runner)

LLM integration (Phi models via testphi.py)

📌 Future Plans

Add GitOps simulation (CI/CD pipelines)

Expand agent roles (design agent, infra agent)

Support external deployment (Docker + ECS)
