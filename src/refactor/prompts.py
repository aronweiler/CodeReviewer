from langchain.prompts import PromptTemplate

REFACTOR_TEMPLATE = """You are a world-renowned expert in {language} code. You have been tasked with identifying security vulnerabilities, performance bottlenecks, memory management concerns, and code correctness problems with the following code.

The code below is a part of a larger code base.

----- BEGIN CODE -----
{code}
----- END CODE -----

Your task is to review the code for any issues mentioned above, and refactor the code to address any issues you find.  In addition, please try to make the code more readable and maintainable (such as by adding comments, renaming variables, etc.).

Only output the updated code, not anything else.

Updated code:
"""


REFACTOR_PROMPT = PromptTemplate(
    input_variables=["language", "code"],
    template=REFACTOR_TEMPLATE,
)

SUMMARIZE_TEMPLATE = """Summarize the functionality of the following {language} code. 

{code}

### Response in Markdown:
# Here is the summary of the {language} code in Markdown:
"""


SUMMARIZE_PROMPT = PromptTemplate(
    input_variables=["language", "code"],
    template=SUMMARIZE_TEMPLATE,
)
