from langchain.prompts import PromptTemplate

REFACTOR_TEMPLATE = """You are a world-renowned expert in all programming languages and practices. You have been tasked with identifying security vulnerabilities, performance bottlenecks, memory management concerns, best practices, and code correctness problems with the following code.

The code below is a part of a larger code base.

----- BEGIN CODE -----
{code}
----- END CODE -----

Please refactor this code keeping in mind your goal to fix any of the issues found above, such as security vulnerabilities, performance bottlenecks, memory management concerns, best practices, and code correctness problems.  

In addition, please try to make the code more readable and maintainable (such as by reorganizing, removing unused code, adding comments, correcting grammar, etc.).

Return ONLY the newly refactored code, and nothing else.  Your refactored code will overwrite the existing code.

Refactored Code:
"""

REFACTOR_PROMPT = PromptTemplate(
    input_variables=["code"],
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
