import os
# from queries import get_query
from queries.K10 import K10Query
from sec.sec import get_recent_folders, download_filings
from config import DB_PERSIST_DIRECTORY, SOURCE_SEC_DIRECTORY
from db.K10 import K10_DB
# from agents.openai.agent import load_agents, create_tools, get_embeddings
# from agents.openai.k10_templates import get_prompt
from models.utils import get_embeddings

os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'

symbol = "STLA"

download_filings(symbol, "10-K")

embeddings = get_embeddings()

persist_directory = f"{DB_PERSIST_DIRECTORY}/{symbol}/10K_items_1_1a_7_7a_8"

k10_db = K10_DB(persist_directory, symbol, embeddings, save_to_txt_files=True, num_years=3)

available_docs = k10_db.get_available_documents()
print("available_docs = ", available_docs)


available_years = k10_db.get_available_years()
print("available_years = ", available_years)

# query= get_query(symbol, key="Risk Factors Years", available_years=available_years)
# print("query = ", query)

# exit()

retriever = k10_db.get_retriever_chain(available_years)






# # Indexing
# db = create_DB(persist_directory, symbol, embeddings)

# retriever = get_retriever(db, persist_directory, embeddings)

k10_query = K10Query(symbol, available_years)

query = k10_query.get_query("Overview")
print("query = ", query)

res = retriever.invoke(query)

#res = agent.invoke(get_query(symbol, "Risk Factors Years"))
# print(response) # all data 

# Save retriever response to temporary file
with open('/tmp/res.txt', 'w') as f:
    # Split response into chunks of 1000 chars
    res_str = str(res)
    chunks = [res_str[i:i+170] for i in range(0, len(res_str), 170)]
    # Write each chunk on a new line
    f.write('\n'.join(chunks))


# Save response output to file

# print("response output:::", res)

