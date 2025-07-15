import ollama

class LanguageModel:
    def __init__(
        self,
        model_name="llama3.2:latest",
        system_prompt=(
            "You are a helpful, concise, and natural-sounding voice assistant named Ava. "
            "Speak in a friendly, professional tone. Avoid verbose explanations unless asked. "
            "If the user asks a question, answer it clearly and directly. "
            "If the user gives a command, respond with the result or a clarifying follow-up. "
            "Use simple language when possible and keep responses under 3 sentences unless more detail is requested. "
            "Always maintain a conversational flow suitable for audio playback. "
            "Do not mention you are an AI or language model unless explicitly asked."
        )
    ):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.history = []  # Store conversation history as a list of messages

    def generate(self, prompt):
        # Add the new user message to history
        self.history.append({"role": "user", "content": prompt})
        # Build the full message list: system prompt, then history
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history
        ]
        response = ollama.chat(
            model=self.model_name,
            messages=messages
        )
        # Add the assistant's reply to history
        self.history.append({"role": "assistant", "content": response['message']['content']})
        return response['message']['content']

    def reset(self):
        self.history = []
