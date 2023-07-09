import os
import configparser
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

# Get the path to the config.ini file
config_path = os.path.join(os.path.dirname(__file__), 'settings', 'config.ini')

# Read the config.ini file
config = configparser.ConfigParser()
config.read(config_path)

# Get values from the config file
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = config.get('openai', 'openai_api_version')
os.environ["OPENAI_API_BASE"] = config.get('openai', 'openai_api_base')
os.environ["OPENAI_API_KEY"] = config.get('openai', 'openai_api_key')

SYSTEM_MSG_TEMPLATE = SystemMessagePromptTemplate.from_template(
    """
    You are a legal assistant. Your primary goal is to identify special commitments in legal documents.
    A special commitment is a clause that obliges one or more parties to do something specific or refrain from doing something in the future.
    Given a legal document, identify if it contains any special commitments related to \"{commitment}\" and list them.
    A special commitment related to \"{commitment}\" has the following policy: {policy}.
    The user will always provide you a snippet from the legal document to review.
    Review the snippet, evaluate against the commitment policy, your response is in JSON format.
    The JSON schema is as below: {{
        \"is_special_commitment\": \"TRUE OR FALSE\",
        \"confidence\": \"CONFIDENCE IN PREDICTION - HIGH, MEDIUM, OR LOW\",
        \"reason\": \"DESCRIPTION OF THE REASON FOR THE PREDICTION\"
    }}
    """)
HUMAN_MSG_TEMPLATE = HumanMessagePromptTemplate.from_template("Snippet: {snippet}")
AI_MSG_TEMPLATE = AIMessagePromptTemplate.from_template("""
{{
    \"is_special_commitment\": \"{is_special_commitment}\",
    \"confidence\": \"{confidence}\",
    \"reason\": \"{reason}\"
}}
""")

# Create an instance of Azure OpenAI chat model
chat = AzureChatOpenAI(
    deployment_name="gpt-35-turbo",
    openai_api_version="2023-05-15"
)

def get_system_message(commitment, policy):
    chat_prompt = ChatPromptTemplate.from_messages([SYSTEM_MSG_TEMPLATE])
    chat_prompt_value = chat_prompt.format_prompt(commitment=commitment, policy=policy)
    messages = chat_prompt_value.to_messages()
    return messages

def get_example_messages(examples, messages):
    human_ai_prompt = ChatPromptTemplate.from_messages([HUMAN_MSG_TEMPLATE, AI_MSG_TEMPLATE])
    for example in examples:
        human_ai_prompt_value = human_ai_prompt.format_prompt(
            snippet=example["snippet"],
            is_special_commitment=example["is_special_commitment"],
            confidence=example["confidence"],
            reason=example["reason"],
        )
        messages.extend(human_ai_prompt_value.to_messages())
    return messages

def get_human_message(snippet, messages):
    human_prompt = ChatPromptTemplate.from_messages([HUMAN_MSG_TEMPLATE])
    human_prompt_value = human_prompt.format_prompt(snippet=snippet)
    messages.extend(human_prompt_value.to_messages())
    return messages

def evaluate_snippet(commitment, policy, examples, snippet):
    messages = get_system_message(commitment, policy)
    messages = get_example_messages(examples, messages)
    messages = get_human_message(snippet, messages)
    response = chat(messages)
    return response.content


