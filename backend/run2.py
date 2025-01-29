import json
from typing import List, Dict, Optional
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

# Define the desired data structure with the 'all_parameters_collected' flag
class UserInputResponse(BaseModel):
    parameters: Dict[str, Optional[str]] = Field(
        default_factory=lambda: {
            "No of shareholders": None,
            "No of visas": None,
            "Activities": None,
            "Cost": None,
            "Office space": None,
        },
        description=(
            "Parameters collected from the user for freezone suggestions. "
            "All fields are optional until the user provides them."
        )
    )
    response: str = Field(
        ..., 
        description="The chatbot's response to the user."
    )
    all_parameters_collected: bool = Field(
        default=False, 
        description="Flag indicating if all parameters have been collected from the user."
    )


# Function to give suggestions based on the collected parameters
def give_suggestion(
    parameters: Dict[str, str], user_query: str, chat_history: List[Dict[str, str]]
) -> str:
    """
    Gives a suggestion based on the collected parameters. For now, returns a hardcoded response.

    Args:
        parameters (dict): Collected parameters from the user.
        user_query (str): The user's original query.
        chat_history (list): The chat history.

    Returns:
        str: A hardcoded suggestion for demonstration.
    """
    # Hardcoded response for demonstration
    return (
        f"Thank you for providing all the details. Based on your input:\n"
        f"- Number of shareholders: {parameters.get('No of shareholders')}\n"
        f"- Number of visas: {parameters.get('No of visas')}\n"
        f"- Activities: {parameters.get('Activities')}\n"
        f"- Cost: {parameters.get('Cost')}\n"
        f"- Office space: {parameters.get('Office space')}\n\n"
        "I suggest the following freezones: Freezone A, Freezone B, Freezone C."
    )


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
            "Here is the chat history:\n{chat_history}\n\n"
            "User query:\n{query}\n\n"
            "Tasks:\n"
            "1. If the query is general, respond directly.\n"
            "2. If the query is about freezones, check the chat history for details like "
            "'No of shareholders', 'No of visas', 'Activities', 'Cost', and 'Office space'.\n"
            "3. If any details are missing, ask the user for one missing parameter at a time.\n"
            "4. Once all details are collected, suggest the best freezones.\n"
            "5. After suggesting, reset the collection status and wait for new input."
        ),
        input_variables=["query", "chat_history"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Create a chain by combining the prompt, model, and parser
    chain = prompt | model | parser

    # Invoke the chain with the user query and chat history
    result = chain.invoke({"query": user_query, "chat_history": str(chat_history)})
    # print(result)
    if result["all_parameters_collected"]:
        # Call the suggestion giver function if the flag is True
        suggestion = give_suggestion(
            parameters=result["parameters"], 
            user_query=user_query, 
            chat_history=chat_history
        )
    return result


# Terminal chatbot loop
def terminal_chatbot():
    print("Welcome to the Freezone Assistant! Type 'exit' to quit.")
    chat_history = []
    parameters = {
        "No of shareholders": None,
        "No of visas": None,
        "Activities": None,
        "Cost": None,
        "Office space": None,
    }

    while True:
        user_query = input("\nYou: ").strip()

        if user_query.lower() == "exit":
            print("Goodbye!")
            break

        try:
            # Process user input
            response = process_user_input(user_query, chat_history)

            # Add to chat history
            chat_history.append({"role": "user", "content": user_query})
            chat_history.append({"role": "assistant", "content": response["response"]})

            # Print the assistant's response
            print(f"\nAssistant: {response['response']}")

            # Check if all parameters are collected and if the flag is True
            if response["all_parameters_collected"]:
                # Call the suggestion giver function if the flag is True
                suggestion = give_suggestion(
                    parameters=response["parameters"], 
                    user_query=user_query, 
                    chat_history=chat_history
                )
                print(f"\nAssistant Suggestion: {suggestion}")

                # After giving the suggestion, reset the parameters collection
                parameters = {key: None for key in parameters}
                response["all_parameters_collected"] = False
            else:
                print("\nCollected Parameters (Incomplete):")
                print(json.dumps(response["parameters"], indent=2))

        except Exception as e:
            print(f"Error: {e}")


# Run the chatbot
if __name__ == "__main__":
    terminal_chatbot()
