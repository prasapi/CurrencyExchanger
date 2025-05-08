from typing import Tuple, Dict
import dotenv
import os
import requests
from dotenv import load_dotenv
import json
import streamlit as st
from openai import OpenAI

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4o-mini"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

load_dotenv()
excr_key =os.getenv('EXCHANGERATE_API_KEY')





def get_exchange_rate(base: str, target: str, amount: str) -> Tuple:
    url = f"https://v6.exchangerate-api.com/v6/{excr_key}/pair/{base}/{target}/{amount}"
    res = requests.get(url)
    resjson = None
    if res.status_code ==200:
        resjson = json.loads(res.text)
        #"""Return a tuple of (base, target, amount, conversion_result (2 decimal places))"""
    else:
        print(res.content)
    return (base,target,amount,excr_key,f'{resjson["conversion_result"]:.2f}')
    pass

def call_llm(textbox_input) -> Dict:
    """Make a call to the LLM with the textbox_input as the prompt.
       The output from the LLM should be a JSON (dict) with the base, amount and target"""
    try:
        response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": textbox_input,
        }
    ],
    temperature=1.0,
    top_p=1.0,
    max_tokens=1000,
    model=model_name
    )
    except Exception as e:
        print(f"Exception {e} for {text}")
    else:
        print(response.choices[0].message.content)
        return response.choices[0].message.content

def run_pipeline():
    """Based on textbox_input, determine if you need to use the tools (function calling) for the LLM.
    Call get_exchange_rate(...) if necessary"""

    if True: #tool_calls
        # Update this
        st.write(f'{base} {amount} is {target} {exchange_response["conversion_result"]:.2f}')

    elif True: #tools not used
        # Update this
        st.write(f"(Function calling not used) and response from the model")
    else:
        st.write("NotImplemented")

print(get_exchange_rate('EUR','INR','252.4'))
# Setting the title of the web application
st.title("Multi-Lingual Currency  Exchanger")

# Creating a text input box
user_input = st.text_area("Enter the currency and amount")

# A submit button
if st.button("Submit"):
    # Display the user's input below the text box
    st.subheader("calling LLM:")
    st.write(call_llm(user_input))