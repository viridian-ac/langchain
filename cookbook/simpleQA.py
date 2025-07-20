# Import necessary libraries
import os  # For accessing environment variables
from dotenv import load_dotenv  # For loading .env file
from langchain_community.llms import OpenAI  # OpenAI LLM from LangChain
from langchain.prompts import PromptTemplate  # For creating prompt templates
from langchain.chains import LLMChain  # For chaining prompts with LLM
from openai import RateLimitError, OpenAIError, AuthenticationError  # OpenAI-specific errors

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Define the prompt template
# The {question} placeholder will be replaced with the user's input
prompt = PromptTemplate(
    input_variables=["question"],
    template="You are a knowledgeable assistant. Provide a concise answer to: {question}"
)

# Initialize the OpenAI LLM
# Temperature of 0.5 ensures a balance between creativity and accuracy
llm = OpenAI(temperature=0.5, openai_api_key=api_key)

# Create an LLMChain to combine the prompt and LLM for streamlined execution
chain = LLMChain(llm=llm, prompt=prompt)

# Define a list of questions to ask the LLM
questions = [
    "What is the largest planet in our solar system?",
    "Who wrote the novel 'Pride and Prejudice'?",
    "What is the capital city of Brazil?",
    "How many continents are there on Earth?",
    "What is the chemical symbol for gold?"
]

# Process each question with error handling
for question in questions:
    try:
        # Execute the chain for the current question and get the response
        response = chain.run(question)
        # Print the question and response, stripping extra whitespace
        print(f"Question: {question}")
        print(f"Answer: {response.strip()}")
        print("-" * 50)  # Separator for readability
    except RateLimitError:
        # Handle API rate limit errors
        print(f"⚠️ Rate limit exceeded for question: '{question}'. Please check your OpenAI API quota or try again later.")
        break  # Stop processing further questions to avoid repeated errors
    except AuthenticationError:
        # Handle invalid API key errors
        print("❌ Invalid API key. Please verify your OPENAI_API_KEY in the .env file.")
        break  # Stop processing if authentication fails
    except OpenAIError as e:
        # Handle other OpenAI API errors
        print(f"❌ OpenAI API error for question '{question}': {e}")
        continue  # Continue with the next question on error