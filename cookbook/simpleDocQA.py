import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 1. Load PDF
loader = PyPDFLoader("example.pdf")
documents = loader.load()

# 2. Split text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)

# 3. Embed and store in FAISS vectorstore
embeddings = OpenAIEmbeddings(openai_api_key=api_key)
vectorstore = FAISS.from_documents(chunks, embeddings)

# 4. Create retriever and QA chain
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
llm = ChatOpenAI(temperature=0, openai_api_key=api_key)
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)

# 5. Ask questions
query = "What is the main argument of the author?"
result = qa_chain({"query": query})

# Print the result
print("\nQ:", query)
print("A:", result["result"])
print("\nSources:")
for doc in result["source_documents"]:
    print(f" - Page: {doc.metadata.get('page')} | Content snippet: {doc.page_content[:100]}...")
