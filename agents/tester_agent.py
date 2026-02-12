import os
from crewai import Agent, Task, LLM

class TesterAgentFactory:
    """Generates pytest-compatible unit tests for given Python code."""

    def __init__(self):
        self.llm = LLM(
            model="groq/llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3,
            stream=True
        )

    def create(self) -> Agent:
        return Agent(
            role="TesterAgent",
            goal="Generate pytest-compatible unit tests covering normal and edge cases.",
            backstory="A QA engineer skilled in writing thorough and maintainable Python test cases.",
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def get_task(self, agent: Agent, code: str) -> Task:
        return Task(
            description=(
                "Write a comprehensive pytest test suite for the following Python code.\n"
                "IMPORTANT: The code is saved in a file called `main.py`. "
                "All imports MUST use `from main import <name>` or `import main`.\n\n"
                f"{code}\n\n"
                "Requirements:\n"
                "- Use `pytest` framework.\n"
                "- Use `@pytest.mark.parametrize` for data-driven tests where possible.\n"
                "- Explicitly cover:\n"
                "   1. Happy paths (standard inputs).\n"
                "   2. Edge cases (boundary values, empty inputs).\n"
                "   3. Negative cases (invalid inputs causing exceptions).\n"
                "- If the code uses external APIs or files, use `unittest.mock` to mock them.\n"
                "- Do NOT modify the original code.\n"
                "- Output ONLY the Python test code, no explanations."
            ),
            expected_output="A complete pytest module that imports from `main` and contains multiple test functions.",
            agent=agent
        )
