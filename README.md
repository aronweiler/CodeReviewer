# CodeReviewer
A LLM powered code reviewing and refactoring tool.

- ✅ Basic Code Review 
  - Currently reviews a single file at a time (e.g. no other files in context), producing line-numbered Markdown output  
- ✅ Basic Refactor
  - Currently refactors single file at a time, creating a new branch where those files are checked in  
- ☑️ Basic Documentation
  - Review and summarize code within a repository (or just file list).  Create markdown documentation / architecture diagrams.
- ☑️ Advanced Code Review
  - Adds better context-aware code-splitting, cross-referencing other source files, entity memory, source control integration
- ☑️ Advanced Refactor
  - Adds cross-referencing other source files, entity memory
- ☑️ Advanced Documentation
  - Ingest existing documentation and edit it.

This tool is consumable through a number of means-
- Through the python code directly
- As a docker container
- As a GitHub Action

## Running the Python Code
You can run the app.py directly with the following command-line arguments.

- Make sure you `pip install -r requirements.txt` first.

- Replace the placeholders in the `.env.template` file with your own values, and rename the file to `.env`.

- All of the following modes are used by calling `python run.py` and setting the `--type` command line argument.

### For Code Reviews

`--type=review <file paths>`

#### Example:

`--type=review src/my_file.py 'src/space in/path.py`

This will review the provided files, and then output to the specified output file (source control integration not available yet)

### For Refactoring

`--type=refactor --source_branch=<source branch> --target_branch=<target branch> <file paths>`

Refactoring your code using the `File` provider in the `.env` file will create a `.refactored` code file next to the original file.


## Running in a Docker Container
TBD

## Running as a GitHub Action
TBD

### A detailed description of what the action does

### Required input and output arguments

### Optional input and output arguments

### Secrets the action uses

### Environment variables the action uses

### An example of how the action is used in a workflow