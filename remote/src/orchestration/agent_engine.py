import google.generativeai as genai
import subprocess
import os

class ClusterAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash", # Use 2.0 locally first
            tools=[self.execute_shell]
        )
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def execute_shell(self, command: str) -> str:
        """Executes a shell command on the cluster and returns the output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            output = result.stdout.strip()
            error = result.stderr.strip()
            return f"STDOUT:\n{output}\n\nSTDERR:\n{error}" if error else output
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def ask(self, prompt: str) -> str:
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                return "⚠️ Quota exceeded (Rate limited). Please wait a minute and try again."
            return f"💥 Agent Error: {error_msg}"

if __name__ == "__main__":
    # Test script
    import sys
    if len(sys.argv) > 1:
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            print("GEMINI_API_KEY env var required")
            sys.exit(1)
        agent = ClusterAgent(key)
        print(agent.ask(" ".join(sys.argv[1:])))
