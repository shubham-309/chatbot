from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict, Optional
import json
from dotenv import load_dotenv
import os
from langchain.memory import ConversationBufferMemory
import os
from flask_caching import Cache
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()

openai_api_key = os.getenv("OPEN_API_KEY")

search = DuckDuckGoSearchRun()
pinecone_apikey = os.getenv("PINECONE_API_KEY")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "travel")

pinecone = Pinecone(api_key=pinecone_apikey, index=pinecone_index_name)
embeddings = OpenAIEmbeddings()


class ResponseStructure(BaseModel):
    next_reply: str
    metadata:str
    reason:str

# Define your model for parsing the output
class InternetSearchRequired(BaseModel):
    internet_search_required: bool = Field(default=False, description="Flag indicating if internet search is required")
    online_search_query: Optional[str] = Field(default=None, description="Query to search online for better GPT-4 responses")

app = Flask(__name__)
CORS(app)

# Configure cache
app.config['CACHE_TYPE'] = 'SimpleCache'  # Change to 'redis' if using Redis
app.config['CACHE_DEFAULT_TIMEOUT'] = 1800  # Timeout in seconds (1800 seconds = 30 minutes)

cache = Cache(app)



app.secret_key = 'your_secret_key'  # Replace with a secure key
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})  # Use SimpleCache for in-memory




def call_openai_api(chat_history, current_json, user_input):

    model = ChatOpenAI(api_key=openai_api_key, temperature=1, model="gpt-4o")
    # model = ChatOpenAI(api_key=openai_api_key, temperature=0)

    # Define the parser
    parser = JsonOutputParser(pydantic_object=ResponseStructure)

    query = f"""

            You are a Freezone assistant chatbot. Your name is FZcompare.AI, and you are designed to help users plan their Freezone and provide Freezones-related information.

            You have to interact with the user as a customer service agent and get them to answer questions. Ensure your responses are polite, engaging, and context-aware, using natural language to guide the user through the necessary details. Here are some key points to remember:

         
            1. Engage politely, analyze chat history, and provide informative responses.
            2. Analyze chat history carefully before responding, providing inferences only when appropriate.
            3. Each response should be informative and contain at least 20 words.
            4. If the user seems confused or requests suggestions then respond accordingly and guide them. base your suggestion on the questions already answered.
            7. Only give inferences when you have the answer; do not guess. If needed ask user for clarification in your next reply. also if you cannot match the answer to the value options then ask the user to clarify
            17. if the user is normally greeting like saying hi hello then greet them normally and introduce yourself (intro is important) say You are a travel assistant chatbot named Travel.AI, designed to help users plan their Freezone and provide Freezone-related information and how you need some info to do that.
            19. finally the most important thing is that your order and time of asking each question should not be ambigious. it should make sense, if the user is asking about a place or any other thing then resolve that first and ask the user if he have any more query. and only after the user's query has been answered then from there keeping the context in mind ask the next question in a relevant wany. dont just answer and ask the next question that is irrelevant. interact just like an professional customer support helping and guiding the user along

            always ask the questions in a logically sensible way

            Please ensure responses are informative, accurate, and tailored to the user's queries and preferences. Use natural language to engage users and provide a seamless experience throughout their Freezone planning journey.

            Below are a few examples for you to learn how to do it:

            Chat history:
            {chat_history}

            you have to answer every user query unless it is entirely on a different domain than the or Freezone use case. for example you have to answer if user asks you to find the visa, etc or if he asks about what is the current time or any visa related news. under any circumstances you have to answer that
            """
    
    internet = gpt_call_with_internet_search(user_input, current_json)

    if internet['internet_search_required']:
        print("yes")
        vector_store = PineconeVectorStore(index_name=pinecone_index_name, embedding=embeddings, text_key="text")
        information = vector_store.similarity_search_with_relevance_scores(query=query, k=5)
        totalScore = 0
        for doc in information:
            score = doc[1] * 100
            totalScore += score
        avgScore = totalScore / len(information)
        print("Average Scoree ",avgScore)
        if avgScore > 80:
            prompt_template = PromptTemplate(
                template="""
                You are a travel assistant. Your task is to answer the general travel query using the provided information.

                Query:
                {query}

                Information:
                {information}

                Steps to follow:
                1. Carefully read and understand the user's query.
                2. Use only the provided context to find the most relevant and accurate information.
                3. Ensure your response is concise, informative, and engaging, tailored to the user's query.
                4. Maintain relevance and enhance the user's understanding or provide actionable advice.
                5. Use a professional and helpful tone.
                """,
                input_variables=["query", "information"], partial_variables={"format_instructions": parser.get_format_instructions()},
            )
            model = ChatOpenAI(temperature=0.6, model_name="gpt-4o")
            chain = prompt_template | model | parser
            print(information)
            response = chain.invoke({"query": query, "information": information})        
        else:
            print("internet query")
        # Define the prompt template
            online_search_query = internet['online_search_query']
            search_results = search.run(online_search_query)
            prompt = PromptTemplate(
                template="""Answer the user query.\n{query}\n\n\n\n    below is the internet search results for the query {online_search_query} so kindly use it as a knowledge context only , Remember this is not the user's reply so do not include any inference from the below text at any cost (most important \n\n\n\n  {search_results}) \n\n Remember you have to give a detailed answer to the user's query using the above data. if you cannot answer or if the data is for internet search is not sufficient just say "i data from internet is not sufficient to answer that query" answer the query no matter what  """,
                input_variables=["query"],
                partial_variables={"format_instructions": parser.get_format_instructions()},
            )
            chain = prompt | model | parser
            response = chain.invoke({"query":query, "search_results":search_results, "online_search_query":online_search_query })

    else:
        prompt = PromptTemplate(
            template="""Answer the user query.\n{query}\n""",
            input_variables=["query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )


        # Create the LLMChain
        chain = prompt | model | parser


        # Invoke the chain
        response = chain.invoke({"query":query})
        
    
    updated_json = response
    print(updated_json)
    return response

# Function to handle GPT calls with internet search capability
def gpt_call_with_internet_search(chat_history: str) -> Dict:
    # Set up the parser
    parser = JsonOutputParser(pydantic_object=InternetSearchRequired)

    # Set up the prompt template
    prompt = PromptTemplate(
        template="see if the user query can me answered by using gpt, if not then we can perform an internet search and provide gpt with that internet search result realtime data , for example this can be used to answer any query if the llm needs internet data to answer it better. \n{format_instructions}\nquery: {query}.\n\n\n\n    if the search is required then give detailed online_search_query that will fetch desired response\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Set up the model
    model = ChatOpenAI(api_key=openai_api_key, temperature=0, model_name="gpt-4o-mini")

    # Create the chain
    chain = prompt | model | parser

    # Create the query including chat history
    query_with_history = f"""
        You are a Freezone assistant chatbot named FZcompare.AI. Your task is to determine if an internet search is needed to better answer the latest question asked by the user based on the provided chat history 

        Chat history:
        {chat_history}

        Your output JSON should follow this structure:

        {{
            "internet_search_required": "true if needed for better answers, otherwise false",
            "online_search_query": "specific query for an internet search if needed"
        }}
        see if the user query can me answered by using gpt, if not then we can perform an internet search and provide gpt with that internet search result realtime data , for example this can be used to answer the date.
        if the search is required then give efficient and detailed online_search_query that will fetch desired response

        if the user is not saying time zone then by default take it as indian standard time
        

        if the user is asking something that is not related to travel then you dont need to preform internet search as it is not in our domain
    """

    # query_with_history = 

    # Perform the GPT call
    response = chain.invoke({"query": chat_history})

    return response


