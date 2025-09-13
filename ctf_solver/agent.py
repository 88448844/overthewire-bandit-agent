import os
import google.generativeai as genai
from policies import is_safe

class Reasoner:
    def __init__(self, model="gemini-1.5-pro"):
        self.model = model
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set. Please set it to your API key.")
        
        genai.configure(api_key=self.api_key)
        self.llm = genai.GenerativeModel(self.model)

    def decide(self, system_prompt: str, tool_context: str):
        print("--REASONER INPUT (showing last 300 chars)--")
        print(tool_context[-300:])
        print("--END REASONER INPUT--")
        
        prompt = f"{system_prompt}\n{tool_context}"
        
        try:
            # Real call to the Gemini API
            response = self.llm.generate_content(prompt)
            cmd = response.text.strip()
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            cmd = "ls -la" # Fallback command on API error

        if not is_safe(cmd):
            print(f"Warning: Unsafe command '{cmd}' generated. Falling back to 'ls -la'.")
            return "ls -la"
        return cmd
