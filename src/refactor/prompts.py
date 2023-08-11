from langchain.prompts import PromptTemplate

REFACTOR_TEMPLATE = """You are a world-renowned expert in the {language} programming language and best practices. You have been tasked with identifying security vulnerabilities, performance bottlenecks, memory management concerns, best practices, and code correctness problems with the following code.

The code below is a part of a larger code base.

----- BEGIN CODE -----
{code}
----- END CODE -----

Please refactor this {language} code keeping in mind your goal to fix any of the issues found above, such as security vulnerabilities, performance bottlenecks, memory management concerns, best practices, and code correctness problems. In addition, please add explanatory comments where code might be hard to understand.

Also, please try to make the code more readable and maintainable (such as by reorganizing code, removing unused code, adding or rephrasing comments, correcting grammar, etc.).  Existing code comments should not be removed, only rephrased for accuracy.

Return only the newly refactored and commented code, and nothing else.  Do not return markdown, or ```{language} (code)```.  Do not summarize your changes, only refactor the code.  

Refactored {language} CODE ONLY:
"""

REFACTOR_PROMPT = PromptTemplate(
    input_variables=["code", "language"],
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
