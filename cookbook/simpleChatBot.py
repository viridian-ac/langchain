from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import start
# Step 1: Define the prompt template
prompt = PromptTemplate(
    input_variables=["question"],
    template="You are a helpful assistant. Answer the question: {question}"
)

# Step 2: Choose an LLM (GPT via OpenAI)
llm = OpenAI(temperature=0.7, OPENAI_API_KEY=start.OPENAI_API_KEY)

# Step 3: Create the chain
chain = LLMChain(llm=llm, prompt=prompt)

# Step 4: Run the chain
question = "What is the capital of Switzerland?"
response = chain.run(question)

print("Q:", question)
print("A:", response)
