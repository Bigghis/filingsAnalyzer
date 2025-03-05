import os
from langchain_openai import ChatOpenAI
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import StructuredQueryOutputParser
from langchain_chroma import Chroma
from dotenv import load_dotenv
from ..queries.K10 import get_query_constructor, allowed_comparators
from ..sec.sec import get_recent_folders
from ..sec.K10 import K10, RELEVANT_ITEMS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, RunnableParallel
from langchain_community.query_constructors.chroma import ChromaTranslator
from ..config import MODEL_OPENAI, SOURCE_SEC_DIRECTORY

load_dotenv()

class K10_DB:
    def __init__(self, persist_directory, symbol, embeddings, save_to_txt_files=True, num_years=3):
        self.persist_directory = persist_directory
        self.symbol = symbol
        self.embeddings = embeddings
        self.num_years = num_years        
        self.docs = []
        self.db = None
        self._initialize_items(save_to_txt_files)

    def _chunck_data(data):
        ''' Function to split documents in chunks'''
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=100)
        chunks = text_splitter.split_documents(data)
        return chunks

    def _initialize_items(self, save_to_txt_files):
        # Check if persist directory exists and create db if not
        if not os.path.exists(self.persist_directory):
            print(f"Creating db for {self.symbol}")
            print(f"Downloading 10-k filings files because {self.persist_directory} does not exist")

            dir_path = os.path.join(SOURCE_SEC_DIRECTORY, self.symbol, "10-K")
            recent_folders = get_recent_folders(self.symbol, num_years=self.num_years)

            for year_folder in recent_folders:
                year_folder_path = os.path.join(dir_path, year_folder)
                print("year_folder_path = ", year_folder_path)
                if not os.path.isdir(year_folder_path):
                    raise(f"Directory {year_folder_path} does not exist")
                doc_path = os.path.join(year_folder_path, "primary-document.html")                
                extractor = K10(self.symbol, doc_path)
                relevant_items = extractor.extract_item_contents(save_to_txt_files)

                for item_key, item in relevant_items.items():
                    self.docs.append(Document(
                        page_content= item["content"], 
                        metadata={
                            "year": item["year"], 
                            "type": item_key,
                            #"type_description": item["title_description"]
                        }
                    ))
            
            # text_splitter = RecursiveCharacterTextSplitter(chunk_size=16000, chunk_overlap=100)
            # documents = text_splitter.split_documents(self.docs)

            # print(f"The document list has been split into {len(documents)} Documents.")
            # for i, doc in enumerate(documents):
            #     # print(f"text: {doc.page_content}")
            #     print(f"{i} metadata: {doc.metadata}")
            #     print("====")
            print(f"Create db")
            self.db = Chroma.from_documents(self.docs, self.embeddings, persist_directory=self.persist_directory)
        else:
            print(f"Loading db for {self.symbol}")
            self.db = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)

    def _get_attributes_info(self):
        """
        Returns the metadata fields for the 10-K documents.
        """
        # types = []
        # for item in self.docs:
        #     types.append(item.metadata["type"])
        # types = sorted(list(set(types)))

        #, one of [{', '.join(types)}]
        return [
            AttributeInfo(name="year", description="The year of the 10-K item", type="integer"),
            AttributeInfo(name="type", description=f"The type of the 10-K item", type="string"),
            #AttributeInfo(name="type_description", description="The description of the 10-K item type", type="string"),
        ]


    def get_retriever(self):
        document_content_description = "Yearly financial reports of the company. The documents are the 10-K filings of the company."
        metadata_field_info = self._get_attributes_info()

        # Check if the persist_directory exists
        if not os.path.exists(self.persist_directory):
            raise ValueError(f"The specified persist_directory does not exist: {self.persist_directory}")

        llm = ChatOpenAI(
            temperature=0,
            model=MODEL_OPENAI,
        )

        retriever = SelfQueryRetriever.from_llm(
            llm,
            self.db,
            document_content_description,
            metadata_field_info,
        )

        return retriever


    def get_retriever_chain(self, available_years):
        max_k = len(available_years) * len(RELEVANT_ITEMS)
        
        attributes_info = self._get_attributes_info()
        constructor_prompt = get_query_constructor(attributes_info)
        output_parser = StructuredQueryOutputParser.from_components()
        llm = ChatOpenAI(
            temperature=0,
            model=MODEL_OPENAI,
        )
        query_constructor = constructor_prompt | llm | output_parser
        chroma_translator = ChromaTranslator()
        chroma_translator.allowed_comparators = allowed_comparators    

        # Initialize the Self-Query Retriever
        retriever = SelfQueryRetriever(
            structured_query_translator=chroma_translator,
            query_constructor=query_constructor,
            vectorstore=self.db,
            search_kwargs={'k': max_k}
        )

        template = '''You are a professional financial analyst, a very disciplined value investor.
        Use this context to answer the question:
        {context}
        Question: {question}'''

        prompt = ChatPromptTemplate.from_template(template)

        def format_docs(docs):
            return "\n\n".join(f"{doc.page_content}\n\nMetadata: {doc.metadata}" for doc in docs)

        # Create a chatbot Question & Answer chain from the retriever
        rag_chain_from_docs = (
            RunnablePassthrough.assign(
                context=(lambda x: format_docs(x["context"])))
            | prompt
            | llm
            | StrOutputParser()
        )

        rag_chain_with_source = RunnableParallel(
            {
                "context": retriever,
                "question": RunnablePassthrough()
            }
        ).assign(answer=rag_chain_from_docs)

        return rag_chain_with_source

    def get_available_documents(self):
        docs = []
        for x in range(len(self.db.get()["ids"])):
            # print(db.get()["metadatas"][x])
            doc = self.db.get()["metadatas"][x]
            docs.append(doc)
        return docs
            

    def get_available_years(self):
        """
        Returns the available years in the database.
        """
        docs = self.get_available_documents()
        years = [doc["year"] for doc in docs]
        return sorted(list(set(years)))
