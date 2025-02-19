from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from openpyxl import load_workbook
import PyPDF2
from langchain.schema import Document
import streamlit as st
import os
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
import uuid
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")


# Define the structured output model
class CompanyInfo(BaseModel):
    name: str = Field(..., description="Name of the Provider")
    package: str = Field(description="Name of the Package")
    number_of_visas: Optional[int] = Field(None, description="Number of visas")
    number_of_shareholders: Optional[int] = Field(None, description="Number of shareholders")
    office_required: Optional[bool] = Field(None, description="Is an office required?")
    cost: Optional[float] = Field(None, description="Associated cost")
    activity: Optional[str] = Field(description="Activities Allowed in the freezone, e.g. consultancy, media, trading, freelance, and industrial activities etc")

# Define a wrapper model for multiple CompanyInfo instances
class CompanyInfoList(BaseModel):
    companies: List[CompanyInfo]

# Initialize OpenAI model
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.0)

# Initialize OpenAIEmbeddings for generating vectors
embeddings = OpenAIEmbeddings()

# Create a Pinecone client instance with your API key.
pc = Pinecone()
print(pc.list_indexes())
index = os.getenv('PINECONE_INDEX_NAME')

# Initialize the parser for CompanyInfoList (not a list of CompanyInfoList)
parser = PydanticOutputParser(pydantic_object=CompanyInfoList)

# Define the prompt template
prompt = PromptTemplate(
    template="Extract structured information from the following text:\n\n"
             "- Name of the Provider\n"
             "- Name of the Package\n"
             "- Number of visas\n"
             "- Number of shareholders\n"
             "- Is an office required? (True/False)\n"
             "- Associated cost\n\n"
             "- Activities Allowed in the freezone, e.g. consultancy, media, trading, freelance, and industrial activities etc\n\n"
             "Provide the output in JSON format.\n\n"
             "Text: {text}\n\n"
             "{format_instructions}",
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


enhancement_prompt = PromptTemplate(
    template="create meaningful sentences from this text each sentence should mention:\n\n"
             "- Name of the Provider\n"
             "- Name of the Package\n"
             "- Number of visas\n"
             "- Number of shareholders\n"
             "- Is an office required? (True/False)\n"
             "- Associated cost\n\n"
             "- Activities Allowed in the freezone, e.g. consultancy, media, trading, freelance, and industrial activities etc\n\n"
             "Text: {text}\n\n",
    input_variables=["text"]
)

def extract_company_info(text: str) -> List[CompanyInfo]:
    """Extracts structured company information from unstructured text."""

    # Generate structured response using OpenAI LLM
    response = (prompt | llm | parser).invoke({"text": text})

    # Return the list of CompanyInfo instances from the wrapped response
    return response.companies if isinstance(response, CompanyInfoList) else []


def extract_data(text: str):
    """Extracts structured company information from unstructured text."""

    # Generate structured response using OpenAI LLM
    response = (enhancement_prompt | llm ).invoke({"text": text})

    return response.content

def extract_text_from_excel(uploaded_file) -> str:
    """Extracts text from all sheets of an Excel file."""
    wb = load_workbook(filename=uploaded_file, data_only=True)
    extracted_text = ""
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        extracted_text += f"Sheet: {sheet}\n"
        for row in ws.iter_rows(values_only=True):
            row_values = [str(cell) if cell is not None else "" for cell in row]
            extracted_text += "\t".join(row_values) + "\n"
        extracted_text += "\n"
    return extracted_text


def extract_text_from_pdf(uploaded_file) -> str:
    """Extracts text from a PDF file."""
    reader = PyPDF2.PdfReader(uploaded_file)
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text() + "\n"
    return extracted_text

def ingest_to_pinecone_docs(companies: List[CompanyInfo], embeddings):
    """
    Ingest approved companies into Pinecone by converting each company info into a Document,
    including all metadata, and using PineconeVectorStore.from_documents.
    """
    print("Starting ingestion process for companies...")
    
    for comp in companies:
        comp_text = (
            f"Name: {comp.name}; Package: {comp.package}; Number of Visas: {comp.number_of_visas}; "
            f"Number of Shareholders: {comp.number_of_shareholders}; Office Required: {comp.office_required}; "
            f"Cost: {comp.cost}; Activity: {comp.activity}"
        )

        metadata= {
                "name": comp.name,
                "package": comp.package,
                "number_of_visas": comp.number_of_visas,
                "number_of_shareholders": comp.number_of_shareholders,
                "office_required": comp.office_required,
                "cost": comp.cost,
                "activity": comp.activity
            }

        # Create a Document with metadata
        document = Document(
            page_content=comp_text,
            metadata= metadata
        )

        if document:
            try:
                PineconeVectorStore.from_documents(
                    documents=[document],
                    embedding=embeddings,
                    index_name=index
                )
                print("Successfully ingested approved companies into Pinecone.")
            except Exception as e:
                print(f"Error while ingesting to Pinecone: {e}")
        else:
            print("No documents to ingest.")

    return "Approved companies have been ingested into Pinecone."
# ------------------------------
# Streamlit App Layout
# ------------------------------

st.title("Company Info Extraction, Approval & Ingestion App")
st.write("Upload Excel and/or PDF files to extract, edit, approve, and then ingest company information into Pinecone.")

# Use a file uploader and store the uploaded files in session state to prevent re-running extraction on each widget interaction.
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = None

uploaded_files = st.file_uploader(
    "Upload Excel or PDF files", type=["xlsx", "pdf"], accept_multiple_files=True
)
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files

# Extraction button: run only once and store results in session state.
if st.button("Extract Company Info"):
    if not st.session_state.uploaded_files:
        st.error("Please upload at least one file.")
    else:
        combined_text = ""
        for uploaded_file in st.session_state.uploaded_files:
            ext = uploaded_file.name.split('.')[-1].lower()
            if ext == "xlsx":
                combined_text += extract_text_from_excel(uploaded_file) + "\n"
            elif ext == "pdf":
                combined_text += extract_text_from_pdf(uploaded_file) + "\n"
            else:
                st.warning(f"Unsupported file type: {uploaded_file.name}")
        

        st.info("Enhancing text...")
        enhanced_text = extract_data(combined_text)
        st.session_state.enhanced_text = enhanced_text


        st.info("Extracting Company Information...")
        company_infos = extract_company_info(enhanced_text)
        st.session_state.company_infos = company_infos

# If extraction is done, render the editable company details.
if "company_infos" in st.session_state:
    st.subheader("Extracted Company Information (Editable & Approve Each)")
    approved_companies = []
    for idx, info in enumerate(st.session_state.company_infos):
        with st.expander(f"Company {idx+1} Details", expanded=True):
            name = st.text_input("Name", value=info.name, key=f"name_{idx}")
            package = st.text_input("Package", value=info.package, key=f"package_{idx}")
            number_of_visas = st.number_input("Number of Visas", value=info.number_of_visas or 0, step=1, key=f"visas_{idx}")
            number_of_shareholders = st.number_input("Number of Shareholders", value=info.number_of_shareholders or 0, step=1, key=f"shareholders_{idx}")
            office_required = st.checkbox("Office Required", value=info.office_required if info.office_required is not None else False, key=f"office_{idx}")
            cost = st.number_input("Cost", value=info.cost or 0.0, step=100.0, format="%.2f", key=f"cost_{idx}")
            activity = st.text_input("Activity", value=info.activity if info.activity is not None else "", key=f"activity_{idx}")
            
            # Use checkbox without forcing a default value from info so that session state preserves user changes.
            approved = st.checkbox("Approve this company", key=f"approve_{idx}")
            
            if approved:
                updated_company = CompanyInfo(
                    name=name,
                    package=package,
                    number_of_visas=number_of_visas,
                    number_of_shareholders=number_of_shareholders,
                    office_required=office_required,
                    cost=cost,
                    activity=activity,
                )
                approved_companies.append(updated_company)
    
    if st.button("Ingest Approved Data into Pinecone"):
        if not approved_companies:
            st.error("No companies approved for ingestion.")
        else:
            ingest_to_pinecone_docs(approved_companies, embeddings)
