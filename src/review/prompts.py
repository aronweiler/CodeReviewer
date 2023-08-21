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

DIFF_REVIEW_TEMPLATE = """You are a world-renowned expert in the practice of software engineering.  You are thourough, precise, and detail oriented. You have been tasked with reviewing another software engineers code changes, and identifying security vulnerabilities, performance bottlenecks, memory management concerns, and code correctness problems in the given diff.

Here is some context related to this diff:
----- BEGIN CONTEXT -----
{context}
----- END CONTEXT -----

Here is the diff to review:
----- BEGIN DIFF -----
{diff}
----- END DIFF -----

Your code review output should be only JSON formatted text.
When commenting on one or more lines of code, use the following format:
{{"start": <starting line number>, "end": <ending line number>, "comment": <comment in markdown>}}
When commenting on the entire code, use the following format:
{{"comment": <comment in markdown>}}


Only provide comments on code that you find specific issues with.  If the context to judge a piece of code does not exist, such as when an unknown (not visibly incorrect) method on an object is called, do not comment on it.

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

DIFF_REVIEW_PROMPT = PromptTemplate(
    input_variables=["diff", "context"],
    template=DIFF_REVIEW_TEMPLATE,
)

CONTEXT_EXTRACTION_TEMPLATE = """You are part of a code reviewing team, and I need you to find and return a list of missing context items that I should pull into a review of the following diff.  This could include things like classes or functions that are not represented in this diff, or other relevant data.  You should ignore missing imports, usings, or other library-inclusions (i.e. Ignore the missing imports or usings of language specific libraries, such as System, os, typing, System.Collections, etc.) when they are not in the context of the diff.

Your response should be a JSON formatted list of context to look up.  For example:

@@ -0,0 +1,95 @@
+   myvar:List[str] = os.getenv("my_var").split(",")
+   my_items = get_data(myvar)
+   for item in my_items:
+      inputs = MyClass.DoWork(item)
+      someunion:Union[str,str] = item, VALID_RESPONSE['inputs'].go()


{{"missing_context": "MyClass", "reference_type": "class", "reason": "`MyClass` is used, but not defined in the diff."}}
{{"missing_context": "get_data()", "reference_type": "function", "reason": "The `get_data()` function is used to create `my_items` list, but I can't verify the usage of `my_items` without knowing how `get_data()` works."}}
{{"missing_context": "VALID_RESPONSE", "reference_type": "variable", "reason": "`inputs` is used to select from `VALID_RESPONSE`, but `VALID_RESPONSE` is not defined in the diff."}}

----- BEGIN DIFF -----
{diff}
----- END DIFF -----

Missing context items in JSON format:
"""

CONTEXT_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["diff"],
    template=CONTEXT_EXTRACTION_TEMPLATE,
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
