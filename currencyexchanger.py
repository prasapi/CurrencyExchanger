from typing import Tuple, Dict
import dotenv
import os
import requests
from dotenv import load_dotenv
import json
import streamlit as st
from openai import OpenAI
from langsmith import traceable
from langsmith.wrappers import wrap_openai

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4o-mini"

os.environ["LANGCHAIN_TRACING_V2"]= "true"
os.getenv('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_PROJECT"] = "currencyexchanger"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
load_dotenv()
excr_key =os.getenv('EXCHANGERATE_API_KEY')
# Define a function tool that the model can ask to invoke in order to retrieve flight information
tool={
    "type": "function",
    "function": {
        "name": "get_exchange_rate",
        "description": """Returns information about the currency value in target currency.
            This includes the amount in the target currency""",
        "parameters": {
            "type": "object",
            "properties": {
                "base": {
                    "type": "string",
                    "description": "The name of base currency",
                },
                "target": {
                    "type": "string", 
                    "description": "The name of the target currency",
                },
                "amount": {
                    "type": "string", 
                    "description": "The amount to convert from base currency to target currency",
                },
            },
            "required": [
                "base","target","amount"
            ],
        },
    },
}

client = OpenAI(
    base_url=endpoint,
    api_key=token
)
@traceable
def get_exchange_rate(base: str, target: str, amount: str) -> Tuple:
    url = f"https://v6.exchangerate-api.com/v6/{excr_key}/pair/{base}/{target}/{amount}"
    res = requests.get(url)
    resjson = None
    if res.status_code ==200:
        resjson = json.loads(res.text)
        #"""Return a tuple of (base, target, amount, conversion_result (2 decimal places))"""
    else:
        print(res.content)
    return (base,target,amount,f'{resjson["conversion_result"]:.2f}')
    pass
@traceable
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
    tools=[tool],
    model=model_name
    )
    except Exception as e:
        print(f"Exception {e} for {text}")
    else:
        print(response.choices[0].message.content)
        return response#.choices[0].message.content
@traceable
def run_pipeline(user_input):
    """Based on textbox_input, determine if you need to use the tools (function calling) for the LLM.
    Call get_exchange_rate(...) if necessary"""
    response = call_llm(user_input)
    if response.choices[0].finish_reason == "tool_calls":
        response_arguments = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
        base = response_arguments["base"]
        target = response_arguments["target"]
        amount = response_arguments["amount"]
        _, _, _, conversion_result = get_exchange_rate(base, target, amount)
        st.write(f'{base} {amount} is {target} {conversion_result}')

    elif response.choices[0].finish_reason == "stop": #tools not used
        # Update this
        st.write(f"(Function calling not used) and {response.choices[0].message.content}")
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
    response = run_pipeline(user_input)
    #res_args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    #base = res_args["base"]
    #target = res_args["target"]
    #amount = res_args["amount"]
    #st.write(get_exchange_rate(base,target,amount))