from crewai import Agent, Task, LLM
import os

class BugFixAgentFactory:
    """Agent that focuses on fixing code based on test failure logs."""

    def __init__(self):
        self.llm = LLM(
            model="groq/llama-3.1-8b-instant",     
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.2,
            stream=True
        )

    def create(self) -> Agent:
        return Agent(
            role="BugFixAgent",
            goal="Fix Python code based on failing test logs.",
            backstory=(
                "An expert software engineer who specializes in debugging Python "
                "applications and resolving failing unit tests with minimal changes."
            ),
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def get_task(self, agent: Agent, code: str, test_log: str) -> Task:
        return Task(
            description=(
                "You are given the current Python code and the test failure logs.\n"
                "Your job is to fix the code so that all tests pass while keeping "
                "existing functionality intact.\n"
                "Do not introduce unnecessary changes or alter unrelated logic.\n\n"
                f"--- Test Failure Log ---\n{test_log}\n\n"
                f"--- Current Code ---\n{code}"
            ),
            expected_output="Return the updated, fully functional Python code.",
            agent=agent
        )
