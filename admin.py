import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain.schema import Document
from pinecone import Pinecone
import os

load_dotenv()

# Ingest documents into Pinecone
def ingest_docs(text):
    INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

    # Ensure text is wrapped in a Document object
    documents = [Document(page_content=text)]
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=2000)
    split_documents = text_splitter.split_documents(documents=documents)
    print(f"Split into {len(split_documents)} chunks")

    print(f"Going to add {len(split_documents)} to Pinecone")
    embeddings = OpenAIEmbeddings()
    PineconeVectorStore.from_documents(documents=split_documents, embedding=embeddings, index_name=INDEX_NAME)

    print("**** Loading to vector store done ****")

# Preprocess data using OpenAI
def preProcessData(data):
    prompt = f"""Extract and organize the data from the uploaded document (Excel or PDF) into a well-structured format. The output should include the following:
                
                Structure:
                    - Output the information in paragraph format.
                    - There should be a paragraph for each type of package listing all details about that package.
                    - List all the names of the packages or categories mentioned in the document.
                    - Extract all price-related information, including standard pricing, discounted pricing, and renewal costs if available.
                    - Highlight any introductory offers or special terms for pricing.
                    - List all included features for each package (e.g., WiFi, meeting room access, parking spaces, discounts).
                    - Specify feature usage limits (e.g., "5 hours/month of meeting room usage").
                    - Extract details of any optional or add-on services, along with their associated costs.
                    - Summarize any additional notes, terms, or conditions mentioned in the document.
                    - Ensure the data is aligned correctly with the associated categories. Retain any numerical values, units, or other specifications (e.g., hours, AED, percentages). If any information appears incomplete or ambiguous, note this explicitly."
            
                Data :- {data}
                """
    template = PromptTemplate(template=prompt, input_variables=["data"])

    model = ChatOpenAI(temperature=0.3, model='gpt-4o-mini')

    chain = template | model

    results = chain.invoke(input={"data": data})

    print(results.content)

    return results.content


# Process Excel files
def process_excel(file):
    try:
        df = pd.read_excel(file)
        st.write("Excel File Content:")
        # Pre-process the extracted text with OpenAI
        extracted_data = preProcessData(df)
        st.text_area("Extracted and Processed Data", value=extracted_data, height=300)
        return extracted_data
    except Exception as e:
        st.error(f"An error occurred while processing the Excel file: {e}")
        return None


# Process PDF files
def process_pdf(file):
    try:
        pdf_reader = PdfReader(file)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text()
        st.write("PDF File Content:")
        
        # Pre-process the extracted text with OpenAI
        extracted_data = preProcessData(text_content)
        
        # Display the result in the Streamlit app
        st.text_area("Extracted and Processed Data", value=extracted_data, height=300)
        return extracted_data
    except Exception as e:
        st.error(f"An error occurred while processing the PDF file: {e}")
        return None


# Streamlit UI
st.title("Admin Panel for Uploading PDF and Excel Files")
st.sidebar.header("Upload Section")
uploaded_file = st.sidebar.file_uploader("Upload a file (PDF or Excel)", type=["pdf", "xlsx"])

processed_data = None  # To store processed data

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    st.sidebar.success(f"Uploaded {uploaded_file.name}")

    if file_type == "xlsx":
        processed_data = process_excel(uploaded_file)
    elif file_type == "pdf":
        processed_data = process_pdf(uploaded_file)
    else:
        st.error("Unsupported file type. Please upload a PDF or Excel file.")
else:
    st.sidebar.info("No file uploaded yet.")

# Button to ingest data into Pinecone
if processed_data:
    if st.button("Ingest Data to Pinecone"):
        ingest_docs(processed_data)
        st.success("Data ingested to Pinecone successfully!")