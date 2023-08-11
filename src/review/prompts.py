from langchain.prompts import PromptTemplate

REVIEW_TEMPLATE = """You are a world-renowned expert in {language} code. You have been tasked with identifying security vulnerabilities, performance bottlenecks, memory management concerns, and code correctness problems with the following code.

The code below is a part of a larger code base.

----- BEGIN CODE -----
{code}
----- END CODE -----

Your code review output should be only JSON formatted text.
When commenting on one or more lines of code, use the following format:
{{"start": <starting line number>, "end": <ending line number>, "comment": <comment in markdown>}}
When commenting on the entire code, use the following format:
{{"comment": <comment in markdown>}}


Only provide comments on code that you find issue with.  Do not provide any comments on code that you do not find issue with.  
If the context to judge a piece of code does not exist, such as when an unknown (not incorrect) method on an object is called, do not comment on it.

EXAMPLE OUTPUT:
{{
    "comments": [
        {{"start": 10, "end": 15, "comment": "Avoid using unsanitized inputs directly in SQL queries to prevent SQL injection vulnerabilities. Use parameterized queries instead."}},
        {{"start": 20, "end": 25, "comment": "Ensure proper input validation to prevent cross-site scripting (XSS) attacks by escaping user-generated content."}},
        {{"start": 35, "end": 40, "comment": "Consider using a more efficient data structure (e.g., a set) to improve the lookup time in this loop."}},
        {{"start": 50, "end": 55, "comment": "It seems that the 'result' object is not properly released, leading to a potential memory leak. Consider using context managers to ensure proper cleanup."}},
        {{"start": 65, "end": 70, "comment": "The loop condition is incorrect. It should be 'while i < len(data)' to avoid an index out of range error."}},
        {{"comment": "Overall, the code appears to be trying to take in user input, format it, and then call the underlying send function. However, it seems that the blocking send call will prevent any more user input from being received. A review of the threading model for this code should be considered."}}
    ]
}}
Code review in JSON format:
"""


REVIEW_PROMPT = PromptTemplate(
    input_variables=["language", "code"],
    template=REVIEW_TEMPLATE,
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
