#%% md
# # BabyAGI User Guide
# 
# This notebook demonstrates how to implement [BabyAGI](https://github.com/yoheinakajima/babyagi/tree/main) by [Yohei Nakajima](https://twitter.com/yoheinakajima). BabyAGI is an AI agent that can generate and pretend to execute tasks based on a given objective.
# 
# This guide will help you understand the components to create your own recursive agents.
# 
# Although BabyAGI uses specific vectorstores/model providers (Pinecone, OpenAI), one of the benefits of implementing it with LangChain is that you can easily swap those out for different options. In this implementation we use a FAISS vectorstore (because it runs locally and is free).
#%% md
# ## Install and Import Required Modules
#%%
from typing import Optional

from langchain_experimental.autonomous_agents import BabyAGI
from langchain_openai import OpenAI, OpenAIEmbeddings
#%% md
# ## Connect to the Vector Store
# 
# Depending on what vectorstore you use, this step may look different.
#%%
from langchain.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
#%%
# Define your embedding model
embeddings_model = OpenAIEmbeddings()
# Initialize the vectorstore as empty
import faiss

embedding_size = 1536
index = faiss.IndexFlatL2(embedding_size)
vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})
#%% md
# ### Run the BabyAGI
# 
# Now it's time to create the BabyAGI controller and watch it try to accomplish your objective.
#%%
OBJECTIVE = "Write a weather report for SF today"
#%%
llm = OpenAI(temperature=0)
#%%
# Logging of LLMChains
verbose = False
# If None, will keep on going forever
max_iterations: Optional[int] = 3
baby_agi = BabyAGI.from_llm(
    llm=llm, vectorstore=vectorstore, verbose=verbose, max_iterations=max_iterations
)
#%%
baby_agi({"objective": OBJECTIVE})
#%%
