from langchain_core.pydantic_v1 import BaseModel, Field, validator
# from model.chat import azure_openai
from backend.utils import azure_openai
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate



class VerifyTagging(BaseModel):
    """
    An assistant, support to check a specific tagged name is appear in a context or not.
    """

    tagging: bool = Field(
        enum=[True, False],
        description="Checking the input sentence is True or False"
    )

parser_verify_tagging = PydanticOutputParser(pydantic_object=VerifyTagging)

prompt_verify_tagging = ChatPromptTemplate.from_messages([
    ("system",
     """
     Check if the {tagged_name} appears as the {tag} in the given sentence: \n
     {context}.

If it's not mentioned in the context, then it was not tagged in the context. \n
Even if it's mentioned in context, but if it's not mentioned as the {tag} in the context, then it was not tagged in the context. \n
     
     Wrap the output in `json` tags\n{format_instructions}
     """
     ,

    # (),
    # ("human", "{query}"
    ),
]).partial(format_instructions=parser_verify_tagging.get_format_instructions())

chain_verify_tagging = prompt_verify_tagging | azure_openai


