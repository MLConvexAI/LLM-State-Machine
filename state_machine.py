import streamlit as st
from openai import OpenAI


class Agent_Two_State:
    def __init__(self, model="gpt-4o-mini", temperature=0.6, max_tokens=4086, top_p=0.9):

        self.client = OpenAI()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p

    def evaluate(self, context, question, answers):

        instructions = f"""You are a helpful AI assistant. Use {context} to answer to the question which is given in {question}. If the answer is {answers[0]} return "1". If the asnwer is {answers[1]} return "0". Return only "1" or "0". """
        initial_messages = [{"role": "user", "content": instructions}]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=initial_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
        )
        response_text = response.choices[0].message.content
        return response_text
    
class Agent_Three_State:
    def __init__(self, model="gpt-4o", temperature=0.6, max_tokens=4086, top_p=0.9):

        self.client = OpenAI()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p

    def evaluate(self, context, question, answers):

        instructions = f"""You are a helpful AI assistant. Use {context} to answer to the question which is given in {question}. If the answer is {answers[0]} return "2". If the asnwer is {answers[1]} return "1". If the asnwer is {answers[2]} return "0". Return only "2", "1" or "0". """
        initial_messages = [{"role": "user", "content": instructions}]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=initial_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
        )
        response_text = response.choices[0].message.content
        return response_text
    

class ResponseValidator:
    def __init__(self, default_valid_responses=["0", "1"]):
        self.default_valid_responses = default_valid_responses

    def validate(self, response, valid_responses=None):
        if valid_responses is None:
            valid_responses = self.default_valid_responses

        if response in valid_responses:
            return True
        else:
            return f"Invalid response. Valid values are {valid_responses}."
      

class Agent_Chat:
    def __init__(self, model="gpt-4o", temperature=0.6, max_tokens=4086, top_p=0.9):

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p

    def answer_to_user(self, context, asnwer):

        instructions = f"""You are a helpful AI assistant. Create a polite answer based on answer {asnwer} and using context {context}. Give the answer in the format as if you were replying directly to the end customer in the chat channel."""
        initial_messages = [{"role": "user", "content": instructions}]

        response = st.session_state.client.chat.completions.create(
            model=self.model,
            messages=initial_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
        )
        response_text = response.choices[0].message.content
        return response_text   


def initialization():
    st.session_state.client = OpenAI()
    st.session_state.Agent_Chat = Agent_Chat()
    st.session_state.messages = []
    set_system_instructions()
    st.session_state.context = "init"

        
def set_system_instructions():
    sys_instructions = f"""You are a helpful AI assistant. """
    st.session_state.messages.append(
        {
            "role": "system", 
            "content": sys_instructions
        }
    )


def streamlit_ui():
    st.header("LLM state model example", divider="rainbow") 

    if "context" not in st.session_state:
        initialization()

    negative_sentiment = False
    reclamation_answer = False
    phone_number = False
    tone = False

    Agent_Chat = st.session_state.Agent_Chat
    Agent_Two_State_Machine = Agent_Two_State()
    Agent_Two_State_Machine_4o = Agent_Two_State(model="gpt-4o")
    Agent_Three_State_Machine = Agent_Three_State()
    Agent_Qualify_Answer = ResponseValidator()

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Please provide input"):
    
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )
        st.chat_message("user").markdown(prompt)

        response = ""
        for _ in range(3):  # Maximum 3 attempts
            response_text = Agent_Three_State_Machine.evaluate(prompt, "What is the sentiment in the text?", ["positive", "neutral", "negative"])                                   
            if Agent_Qualify_Answer.validate(response_text, ["0", "1", "2"]) == True:
                response += f"Sentiment = {response_text}. "
                if response_text == "0":
                    negative_sentiment = True
                break  # Exit the loop if the answer is valid
        else:
            response += f"Sentiment = -1. "
            print("Failed to get a valid response after 3 attempts.")
        
        for _ in range(3): 
            response_text = Agent_Two_State_Machine.evaluate(prompt, "Is there a reclamation in the text?", ["yes", "no"])
            if Agent_Qualify_Answer.validate(response_text) == True:
                response += f"Reclamation = {response_text}. "
                if response_text == "1":
                    reclamation_answer = True
                break
        else:
            response += f"Reclamation = -1. "
            print("Failed to get a valid response after 3 attempts.")

        for _ in range(3): 
            response_text = Agent_Two_State_Machine_4o.evaluate(prompt, "Is there a phone number in the text?", ["yes", "no"])
            if Agent_Qualify_Answer.validate(response_text) == True:
                response += f"Phone number = {response_text}. "
                if response_text == "1":
                    phone_number = True
                break
        else:
            response += f"Phone number = -1. "
            print("Failed to get a valid response after 3 attempts.")

        for _ in range(3): 
            response_text = Agent_Two_State_Machine.evaluate(prompt, "Is the tone furious?", ["yes", "no"])
            if Agent_Qualify_Answer.validate(response_text) == True:
                response += f"Tone furious = {response_text}. "
                if response_text == "1":
                    tone = True
                break
        else:
            response += f"Tone furious = -1. "
            print("Failed to get a valid response after 3 attempts.")

        st.session_state.messages.append(
        {
             "role": "machine",
             "content": response
        }
        )
        st.chat_message("machine").markdown(response)   

        if reclamation_answer and phone_number:
            response = Agent_Chat.answer_to_user(prompt, "I will call you immediately!")
            st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
            )
            st.chat_message("assistant").markdown(response) 
        elif negative_sentiment and reclamation_answer and tone:
            response = Agent_Chat.answer_to_user(prompt, "Propose an alternative product.")
            st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
            )
            st.chat_message("assistant").markdown(response) 

if __name__ == "__main__":

    streamlit_ui()
 