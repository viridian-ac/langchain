# Import necessary libraries
import logging  # For logging errors and information
import os  # For accessing environment variables
from langchain_community.llms import OpenAI  # Import OpenAI LLM from langchain_community
from langchain.prompts import PromptTemplate  # For creating prompt templates
from langchain.chains import LLMChain  # For chaining prompts with the LLM
from openai import RateLimitError, OpenAIError, AuthenticationError  # Import OpenAI-specific error classes
from dotenv import load_dotenv  # For loading environment variables from .env file

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Define the prompt template for the LLM
# input_variables specifies the variable to be replaced in the template
# template defines the structure of the prompt sent to the LLM
prompt = PromptTemplate(
    input_variables=["question"],
    template="You are a helpful assistant. Answer the question: {question}"
)

# Initialize the OpenAI LLM
# temperature controls creativity (0.7 balances creativity and coherence)
# openai_api_key passes the API key for authentication
llm = OpenAI(temperature=0.7, openai_api_key=api_key)

# Create an LLMChain to combine the prompt and the LLM
# This chains the prompt template with the LLM for streamlined processing
chain = LLMChain(llm=llm, prompt=prompt)

# Define the question to ask the LLM
question = "What is the capital of Switzerland?"

# Run the chain inside a try-except block to handle potential errors
try:
    # Execute the chain with the question and get the response
    response = chain.run(question)
    # Print the question and the LLM's response
    print("Q:", question)
    print("A:", response)
except RateLimitError:
    # Handle case where API rate limit is exceeded
    print("⚠️ Rate limit exceeded. Please check your usage or try again later.")
except AuthenticationError:
    # Handle case where the API key is invalid
    print("❌ Invalid API key. Please verify your OPENAI_API_KEY in .env.")
except OpenAIError as e:
    # Handle other OpenAI-specific errors
    print(f"❌ OpenAI API error: {e}")

