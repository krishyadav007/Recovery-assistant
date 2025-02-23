import os
# import logging
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langsmith import traceable
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env", verbose=True, override=True)

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@traceable(run_type="llm", metadata={"ls_provider": "ollama", "model": "mistral"})
def create_qa_agent(pdf_path, model_name="mistral"):
    print("Agent running", pdf_path)
    """
    Create a question-answering agent for a specific PDF document.

    Args:
        pdf_path (str): Path to the PDF file
        model_name (str): Name of the Ollama model to use

    Returns:
        qa_chain: A QA chain that can answer questions about the PDF
    """
    persist_directory = "./data/chroma_db"

    # Check if the Chroma store already exists
    if os.path.exists(persist_directory):
        # logging.info("Loading existing Chroma store...")
        vectorstore = Chroma(persist_directory=persist_directory, embedding_function=OllamaEmbeddings(model=model_name))
    else:
        # logging.info("Creating new Chroma store...")
        # 1. Load the PDF
        loader = PyPDFLoader("./"+pdf_path)
        pages = loader.load()
        # logging.info(f"Loaded {len(pages)} pages from the PDF.")

        # 2. Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        splits = text_splitter.split_documents(pages)
        # logging.info(f"Split the document into {len(splits)} chunks.")
        print("This should be splits:", splits)

        # 3. Create embeddings and store them
        embeddings = OllamaEmbeddings(model=model_name)
        vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

        for i, chunk in enumerate(tqdm(splits, desc="Processing chunks"), 1):
            vectorstore.add_documents([chunk], embedding=embeddings)
        # logging.info(f"Stored {len(splits)} chunks in the vectorstore.")

    # 4. Create the LLM
    llm = Ollama(model=model_name)

    # 5. Create a custom prompt template
    prompt_template = """
    You are a helpful health AI assistant that answers questions based on the provided PDF document.
    Try your reasoning and context provided to answer the question. The user wants to know what they can do, which will be good for their health or bad for thier health. If you don't know the answer say so. Also restate the question in your answer. 

    For example if user asks I want to eat mango is it fine. You can reply yes since your disease doesn't affect by eating mango.
    However if they ask can I drink alcohol. Then reply no drinking alcohol can make your problem worse.
    
    Context: {context}

    Question: {question}

    Answer: Let me help you with that based on the PDF content."""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    # print("This the prompt template: ", prompt_template)

    # 6. Create and return the QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 10}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )

    return qa_chain

@traceable(run_type="chain")
def ask_question(qa_chain, question):
    """
    Ask a question to the QA chain and get the response.

    Args:
        qa_chain: The QA chain created by create_qa_agent
        question (str): The question to ask

    Returns:
        dict: Response containing the answer and source documents
    """
    try:
        response = qa_chain({"query": question})
        return {
            "answer": response["result"],
            "sources": [doc.page_content for doc in response["source_documents"]]
        }
    except Exception as e:
        # logging.error(f"An error occurred: {str(e)}")
        return {
            "error": f"An error occurred: {str(e)}",
            "answer": None,
            "sources": None
        }
