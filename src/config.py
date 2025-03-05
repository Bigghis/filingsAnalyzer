import os

ROOT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DATA_DIRECTORY = f"{ROOT_DIRECTORY}/../data"

# Define the folder for downloading the data
SOURCE_SEC_DIRECTORY = f"{DATA_DIRECTORY}/sec-edgar-filings"

# Define the folder for storing the temporary files (ex.: text files created from the 10-k filings)
# TMP_DIRECTORY = f"{DATA_DIRECTORY}/tmp"
TMP_DIRECTORY = "/tmp"

# DB 
#  Define the folders for storing database 
DB_PERSIST_DIRECTORY = f"{DATA_DIRECTORY}/embeddings"
DB_10K_DIR_NAME = "10K_items_1_1a_7_7a_8_9"

#  SEC
COMPANY_NAME = "Personal Use2"
EMAIL = "pa.casciano@gmail.com"

# MODEL 

MODEL_OPENAI = "gpt-4o-mini"
