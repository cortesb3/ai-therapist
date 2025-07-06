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

    def generate(self, prompt):
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content']
