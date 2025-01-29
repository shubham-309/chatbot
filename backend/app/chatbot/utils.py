import json
from typing import List, Dict, Optional
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
load_dotenv()

# Define the desired data structure with the 'all_parameters_collected' flag
from typing import Optional
from pydantic import BaseModel, Field

# Define the parameters as a nested model
class FreezoneParameters(BaseModel):
    no_of_shareholders: Optional[int] = Field(
        None, 
        description="The number of shareholders. (Optional)"
    )
    no_of_visas: Optional[int] = Field(
        None, 
        description="The number of visas. (Optional)"
    )
    activities: Optional[str] = Field(
        None, 
        description="The activities required. (Optional)"
    )
    cost: Optional[float] = Field(
        None, 
        description="The cost associated with the freezone. (Optional)"
    )
    office_space: Optional[bool] = Field(
        None, 
        description="Indicates if office space is required. (Optional)"
    )
    preferred_location: Optional[str] = Field(
        None, 
        description="The preferred location for the freezone. (Optional)"
    )

# Define the main response model with the 'parameters' field
class UserInputResponse(BaseModel):
    parameters: FreezoneParameters = Field(
        default_factory=FreezoneParameters, 
        description="Parameters related to the user's freezone requirements."
    )
    response: str = Field(..., description="The chatbot's response to the user.")
    all_parameters_collected: bool = Field(default=False, description="Flag indicating if all parameters have been collected from the user.")



def vector_search(
    no_of_visa: int,
    no_of_shareholder: int,
    cost: int,
    office: bool,
) -> List[dict]:
    # Initialize the embedding model and vector store
    embeddings = OpenAIEmbeddings()
    vector_store = PineconeVectorStore(
        index_name="test",  # Replace with your Pinecone index name
        embedding=embeddings,
        text_key="text",
    )

    # Construct metadata filter based on the inputs
    metadata_filter = f"""The company has {no_of_shareholder} shareholders, employs {no_of_visa} visa holders, incurs a total cost of {cost}, and operates out of the {office} office."""

    # Perform similarity search with metadata filtering
    similarity_search_results = vector_store.similarity_search_with_score(
        metadata_filter,
        k=5,
    )

    return similarity_search_results

def give_suggestion(
    parameters: FreezoneParameters, user_query: str, chat_history: List[Dict[str, str]]
) -> str:
    """
    Gives a suggestion based on the collected parameters.

    Args:
        parameters (FreezoneParameters): Collected parameters from the user.
        user_query (str): The user's original query.
        chat_history (list): The chat history.

    Returns:
        str: A suggestion based on the collected parameters.
    """
    # Call vector_search to get data based on the parameters
    data = vector_search(
        parameters['no_of_visas'], 
        parameters['no_of_shareholders'], 
        parameters['cost'], 
        parameters['office_space']
    )

    # Define the prompt template
    prompt = f"""Based on the following data for free zone license packages, recommend the most suitable free zone for the user:

                Input Data: {{data}}

                Output Requirements:
                - Recommended Free Zone Name.
                - A brief explanation of why this free zone is suitable based on the user's input (e.g., matches the budget, visa requirements, and business activity).
                - Any additional recommendations, such as alternative free zones or flexibility for future business needs.

                Example Output:
                IFZA Dubai is a great option for those seeking a commercial license with a budget-friendly price of 14,900 AED for one visa, offering flexibility for future scalability with the possibility of up to four visas. This makes it an ideal choice for users looking for a cost-effective solution with room to grow. Alternatively, Shams is recommended for users with a lower budget and fewer visa requirements.
    """

    # Create a PromptTemplate and configure the chain
    template = PromptTemplate(template=prompt, input_variables=["data"])

    model = ChatOpenAI(temperature=0.3, model='gpt-4o-mini')

    # Create a chain
    chain = template | model

    # Invoke the chain
    results = chain.invoke(input={"data": data})

    return results.content

# Function to process user input
def process_user_input(user_query: str, chat_history: List[Dict[str, str]]) -> Dict:
    """
    Process user input and return a structured JSON response using LangChain.
    """
    # Initialize the model
    model = ChatOpenAI(temperature=0, model="gpt-4o-mini")

    # Define the output parser
    parser = JsonOutputParser(pydantic_object=UserInputResponse)

    # Build the prompt template
    prompt = PromptTemplate(
        template=(
            "You are a helpful assistant. Process the user's query and respond in JSON format "
            "using the following structure:\n"
            "{format_instructions}\n\n"
            
            "You are a helpful assistant. Your task is to guide the user through a series of "
            "questions to collect details about their freezone requirements and eventually suggest the best freezones. "
            "You will process the user's query and respond with a JSON structure containing the response and status of "
            "collected parameters.\n\n"

            "Instructions:\n"
            "1. If the query is general, respond directly and move on to the next step.\n"
            "2. If the query relates to freezones, check the user's provided information in the chat history. "
            "The parameters you need to collect are: 'No of shareholders', 'No of visas', 'Activities', 'Cost', "
            "'Office space', and 'Preferred location'. These parameters are optional initially.\n"
            "3. If any of the parameters are missing, ask the user for one missing parameter at a time in a conversational "
            "manner.\n"
            "4. Only when **all** parameters ('No of shareholders', 'No of visas', 'Activities', 'Cost', 'Office space', and 'Preferred location') "
            "are provided should you set the flag `all_parameters_collected` to `True`.\n"
            "5. If all parameters are collected, suggest appropriate freezones based on the user's input. The assistant should "
            "suggest the best freezones by referencing the parameters the user provided.\n"
            "6. After suggesting the freezones, reset the parameter collection status to `False` so that the assistant can be ready "
            "to collect new parameters from the next user request.\n"
            "7. If any parameters are missing, the assistant should respond with which specific parameter is still needed. "
            "Repeat this until all parameters are collected.\n"
            "8. Your tone should be user friendly and appealing, try to be best while interacting."
            
            "\nChat history:\n{chat_history}\n\n"
            "User query:\n{query}\n\n"
            "Your task is to:\n"
            "1. If all required parameters are collected, set `all_parameters_collected` to `True` and if the suggestion is already provided in the chat then set it to null and manage it accordingly"
            "2. If parameters are missing, prompt the user for the missing ones one at a time."
            "3. Return the structured response in JSON format with the appropriate information."
            "note : always make sure all the fields are filled before setting the flag to true"
            "see i want you to understand that what you give all_parameters_collected as true along with the parameters then i will use these parameters to call another tool to give suggestions bsed on these parameters so when you give it as true you do not need to give response (but always remember do this only when the flag is false otherwise give back a response under no circumstances are you allowed to do but the is you can never set the flag to false and not returning the response i repeat never) got it also understand this workflow so that you can work better next time"
            "you can never ever do this 'response': None, 'all_parameters_collected': False, got it,    if all the parameters are received and the user is asking for suggestion then set the flag to true otherwise under reply properly and accordingly"
            "also see in the chat history if the suggestion is already given in the current context then set the flag to falso and reply accordingly"
            ""
        ),
        input_variables=["query", "chat_history"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Create a chain by combining the prompt, model, and parser
    chain = prompt | model | parser

    # Invoke the chain with the user query and chat history
    result = chain.invoke({"query": user_query, "chat_history": str(chat_history)})
    print(f"\nAssistant result  : {result}")
    if result["all_parameters_collected"]:
        print(f"\n  {type(result['parameters'])}  Assistant Suggestion: {result['parameters']}")

        # Call the suggestion giver function if the flag is True
        suggestion = give_suggestion(
            parameters=result["parameters"], 
            user_query=user_query, 
            chat_history=chat_history
        )
        print(f"\nAssistant Suggestionnnnnn    : {suggestion}")
        return suggestion
    return result['response'] or "some error occured unable to fetch"
