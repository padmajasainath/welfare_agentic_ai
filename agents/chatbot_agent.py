from agents.base_agent import BaseAgent
 
class ChatbotAgent(BaseAgent):
    def __init__(self):
        super().__init__("EtihadAssistant")
        self.conversation_history = []
 
    def run(self, user_query):
        """
        Answers general questions about Etihad Airways.
        """
        prompt = f"""
        You are the Etihad Airways Virtual Assistant.
        Answer the following question from a staff member or customer helpful and professionally.
        Verify your answer is related to Etihad Airways policies, destinations, or fleet if applicable.
        If the question is unrelated to aviation or Etihad, politely steer it back.
       
        Question: {user_query}
        """
 
        try:
            # Maintain simple history in the prompt if needed,
            # but for minimal implementation, single-turn is safer to start.
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"I apologize, I am currently unable to access my knowledge base. Error: {str(e)}"
 
