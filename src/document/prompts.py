from langchain.prompts import PromptTemplate

SUMMARIZE_TEMPLATE = """Summarize the functionality of the following code: 

{code}

### Response in Markdown:
# Here is the summary of the code in Markdown:
"""


SUMMARIZE_PROMPT = PromptTemplate(
    input_variables=["code"],
    template=SUMMARIZE_TEMPLATE,
)

COMBINE_TEMPLATE = """The following is a number of summaries describing code functionality. Combine them into a single summary. 

{text}

### Response in Markdown:
# Here is the combined summary in Markdown:
"""


COMBINE_PROMPT = PromptTemplate(
    input_variables=["text"],
    template=COMBINE_TEMPLATE,
)

MAP_REDUCE_COMBINE_TEMPLATE = """The following is a number of summaries describing code functionality. Disregard any summaries that are not relevant to the question. Combine the remaining summaries into a single summary.

Summaries:
====================
{summaries}
====================

Original Question:
====================
{question}
====================

Response in Markdown:
"""


MAP_REDUCE_COMBINE_PROMPT = PromptTemplate(
    input_variables=["summaries", "question"],
    template=MAP_REDUCE_COMBINE_TEMPLATE,
)
