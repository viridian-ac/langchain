# Import required libraries for building a Retrieval-Augmented Generation (RAG) system
import os  # Provides access to environment variables (e.g., for API keys)
from dotenv import load_dotenv  # Loads environment variables from a .env file
from langchain_community.document_loaders import PyPDFLoader  # Loads and extracts text from PDF files
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Splits text into manageable chunks
from langchain_openai import OpenAIEmbeddings  # Generates vector embeddings for text using OpenAI's model
from langchain_community.vectorstores import FAISS  # FAISS vector store for efficient similarity search
from langchain.chains import RetrievalQA  # Creates a question-answering chain with retrieval
from langchain_openai import ChatOpenAI  # OpenAI's chat model for generating answers
from openai import RateLimitError, OpenAIError, AuthenticationError  # OpenAI-specific error handling classes

# Load environment variables from a .env file in the project directory
# The .env file should contain key-value pairs, e.g., OPENAI_API_KEY=your-api-key-here
load_dotenv()

# Retrieve the OpenAI API key from environment variables
# os.getenv() safely accesses the key; returns None if not found
api_key = os.getenv("OPENAI_API_KEY")

# Validate the API key to provide early feedback and prevent runtime errors
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in .env file. Please set it and try again.")

# Step 1: Load the PDF document
# PyPDFLoader reads the specified PDF file and extracts its text content
# The file 'document.pdf' must exist in the working directory, or a FileNotFoundError will occur
try:
    loader = PyPDFLoader("document.pdf")  # Initialize the PDF loader with the target file
    documents = loader.load()  # Load the PDF content into a list of Document objects
except FileNotFoundError:
    raise FileNotFoundError("❌ The file 'document.pdf' was not found in the working directory.")

# Step 2: Split the document into smaller chunks
# RecursiveCharacterTextSplitter divides text into chunks for efficient embedding and retrieval
# chunk_size=1000 limits each chunk to ~1000 characters to balance context and performance
# chunk_overlap=200 ensures 200 characters of overlap between chunks to preserve context
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)  # Split the loaded documents into chunks

# Step 3: Generate embeddings and store them in a FAISS vector store
# OpenAIEmbeddings converts text chunks into vector representations using OpenAI's embedding model
# FAISS (Facebook AI Similarity Search) creates an index for fast similarity-based retrieval
try:
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)  # Initialize embeddings with the API key
    vectorstore = FAISS.from_documents(chunks, embeddings)  # Create a FAISS index from document chunks
except OpenAIError as e:
    raise OpenAIError(f"❌ Failed to generate embeddings: {e}")

# Step 4: Set up the retriever and QA chain
# Convert the FAISS vector store into a retriever for fetching relevant document chunks
# search_kwargs={"k": 3} limits retrieval to the top 3 most relevant chunks based on similarity
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Initialize the OpenAI chat model
# ChatOpenAI uses OpenAI's chat-based LLM (e.g., GPT models) for generating answers
# temperature=0 ensures deterministic, focused responses suitable for factual queries
llm = ChatOpenAI(temperature=0, openai_api_key=api_key)

# Create a RetrievalQA chain
# Combines the LLM and retriever to answer queries using relevant document chunks
# return_source_documents=True includes the retrieved chunks in the response for transparency
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)

# Step 5: Define and process a sample query
# The query is a question about the document's content, answered based on retrieved chunks
query = "What is the main argument of the author?"

# Execute the query with error handling
try:
    result = qa_chain.invoke({"query": query})  # Run the QA chain with the query using invoke
except RateLimitError:
    print("⚠️ Rate limit exceeded. Please check your OpenAI API quota or try again later.")
    exit(1)  # Exit the program on rate limit error to avoid further API calls
except AuthenticationError:
    print("❌ Invalid API key. Please verify your OPENAI_API_KEY in the .env file.")
    exit(1)  # Exit the program on authentication failure
except OpenAIError as e:
    print(f"❌ OpenAI API error: {e}")
    exit(1)  # Exit on other OpenAI errors
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)  # Exit on unexpected errors

# Print the query and the LLM's answer
# result["result"] contains the generated answer based on retrieved document chunks
print("\nQ:", query)
print("A:", result["result"])

# Print the source documents used to generate the answer
# result["source_documents"] contains the retrieved chunks with metadata (e.g., page numbers)
print("\nSources:")
for doc in result["source_documents"]:
    # Access page number from document metadata; use get() to handle missing metadata
    # Limit content snippet to 100 characters for brevity, appending "..." to indicate truncation
    print(f" - Page: {doc.metadata.get('page', 'Unknown')} | Content snippet: {doc.page_content[:100]}...")