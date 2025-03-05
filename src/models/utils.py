from langchain_openai import ChatOpenAI, OpenAIEmbeddings

def get_embeddings():
    return OpenAIEmbeddings()

def get_llm():
    return ChatOpenAI(temperature=0)