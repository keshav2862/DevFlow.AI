import os
from crewai import Agent, Task, LLM

class ReviewerAgentFactory:
    """Reviews Python code for correctness, style, and performance."""

    def __init__(self):
        self.llm = LLM(
            model="groq/llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.2,
            stream=True
        )

    def create(self) -> Agent:
        return Agent(
            role="ReviewerAgent",
            goal="Review Python code and provide concise, actionable feedback.",
            backstory="An experienced code reviewer who identifies bugs, style issues, and optimizations.",
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def get_task(self, agent: Agent, code: str) -> Task:
        return Task(
            description=(
                "Review the following Python code and provide feedback:\n\n"
                f"{code}\n\n"
                "Provide feedback in these sections:\n"
                "1. **Bugs & Issues** – list any functional errors.\n"
                "2. **Code Quality** – style, readability, maintainability.\n"
                "3. **Performance** – suggest optimizations.\n"
                "4. **Security** – note any vulnerabilities.\n"
                "Respond in bullet points."
            ),
            expected_output="A structured markdown-formatted review report.",
            agent=agent
        )
