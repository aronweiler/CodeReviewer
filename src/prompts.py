from langchain.prompts import PromptTemplate

REVIEW_TEMPLATE = """Perform a comprehensive code review of the following {language} code, considering security, performance, memory management, and code correctness. 

{code}

### Response in Markdown:
# Here is the comprehensive code review of the {language} code in Markdown. I've addressed the following aspects:
- Security: Looked for potential security vulnerabilities such as SQL injection, cross-site scripting (XSS), or improper handling of sensitive data, and suggested security measures.
- Performance: Identified areas for code optimizations, algorithm improvements, and better data structures to enhance performance.
- Memory Management: Checked for memory leaks and buffer overflow possibilities, and recommended strategies for efficient memory management.
- Code Correctness: Ensured code clarity, checked for uninitialized variables, undefined behavior, and logic errors that could lead to incorrect outcomes, and provided suggestions for improving code readability and correctness.

Please find the detailed review and recommendations below:
"""

REVIEW_PROMPT = PromptTemplate(
    input_variables=["language", "code"],
    template=REVIEW_TEMPLATE,
)