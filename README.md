# CodeReviewer
A LLM powered code reviewing refactoring, and documentation tool.

I kicked this project off a while back because I wanted to have an LLM act as a code reviewer for me in absence of having a regular coding partner.  

As the capabilities of large language models like [OpenAI's ChatGPT](chat.openai.com), or open-source models like [Wizard Coder](https://huggingface.co/WizardLM/WizardCoder-15B-V1.0), have progressed, having an AI review my code has become something of a requirement for me.

To that end, I've taken what used to be a local-run-only application and ported it to a Docker container, and now a [GitHub Action](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions).

**Note:** Currently, this repository only makes use of the OpenAI models, which you can find here: [OpenAI Models](https://platform.openai.com/docs/models/overview)

- ✅ Basic Code Review
  - Run types: Local only
  - Currently reviews a single file at a time (e.g. no other files in context), producing line-numbered Markdown output
- ✅ Basic Refactor
  - Run types: Local, GitHub Action
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
You can run the app.py directly with the proper environment variables set.

- Make sure you `pip install -r requirements.txt` first.

- Replace the placeholders in the `.env.template` file with your own values, and rename the file to `.env`.

- Run the `python run.py` after setting the following environment variables.

### Environment variables:
- **CR_TYPE**: The type of the action to perform.  This can be either `review`, `refactor`, or `document`.  Currently, only `refactor` is supported.
- **OPENAI_API_KEY**: Your OpenAI API key, which you can get here: [platform.openai.com](platform.openai.com)
- **GITHUB_TOKEN**: This is the token that the action will use to make changes / commits to your repository.  This can be extracted from `${{ secrets.GITHUB_TOKEN }}` in your action workflow.
- **CR_PROVIDER**: Supported types right now are `github` and `file`.  This is required to be set to `github` if you are using the Action.  When running locally, you can set this to `file`.
- **CR_MODEL**: Which OpenAI model to use.
- **CR_TEMPERATURE**: Model temperature.
- **CR_MAX_SUPPORTED_TOKENS**: The maximum number of tokens that the model supports, or lower if you want to restrict usage.
- **CR_MAX_COMPLETION_TOKENS**: The number of tokens to use for the completion.  **Note:** This reduces the number of tokens available for the prompt (i.e. the code file to review).  This number might require some tuning from you in order to get the desired performance.
- **CR_SOURCE_BRANCH**: The source branch name the use for the review/refactor/document run.
- **CR_TARGET_BRANCH**: The target branch where you want the output files committed.  **Note**: Commits to this branch will use `-force`.
- **CR_TARGET_FILES**: Specifies any target files or directories that you might want to limit the refactor to.  This is not required, and when not specified the action will use the root directory.  
  - **⚠️WARNING⚠️** this can get expensive if you have a lot of files, and you send them all to OpenAI.
- **CR_LOG_LEVEL**: Logging level supported by the action. Default is `INFO`.

## Running in a Docker Container
TBD

## Running as a GitHub Action
Create a workflow in your repository under the `.github\workflows\` folder.  

See [.github\workflows\main.yml](.github\workflows\main.yml)

Currently I have tested the using the manual trigger (`workflow_dispatch`) within this action, so that is what I'd recommend.  However, if you set the proper environment variables, then it shouldn't matter how you run it.

### A detailed description of what the action does
This action will perform a code review, a code refactor, or documentation tasks for you. 

See: [Description at the top of this page](#CodeReviewer)


### Required input and output arguments
The following are environment variables that must be set for ANY of the modes supported here.

- **CR_TYPE**: The type of the action to perform.  This can be either `review`, `refactor`, or `document`.  Currently, only `refactor` is supported.

#### Required input arguments for Code Refactoring:
The following environment variables must be set for code refactoring.  Examples of these environment variables are shown in the [.github\workflows\main.yml](.github\workflows\main.yml) in this repo.

- **OPENAI_API_KEY**: Your OpenAI API key, which you can get here: [platform.openai.com](platform.openai.com)
- **GITHUB_TOKEN**: This is the token that the action will use to make changes / commits to your repository.  This can be extracted from `${{ secrets.GITHUB_TOKEN }}` in your action workflow.
- **CR_PROVIDER**: This is required to be set to `github` for this action.  When running locally, you can set this to `file`.
- **CR_MODEL**: Which OpenAI model to use for this run.
- **CR_TEMPERATURE**: Model temperature.
- **CR_MAX_SUPPORTED_TOKENS**: The maximum number of tokens that the model supports, or lower if you want to restrict usage.
- **CR_MAX_COMPLETION_TOKENS**: The number of tokens to use for the completion.  **Note:** This reduces the number of tokens available for the prompt (i.e. the code file to review).  This number might require some tuning from you in order to get the desired performance.
- **CR_SOURCE_BRANCH**: The source branch name the use for the review/refactor.
- **CR_TARGET_BRANCH**: The target branch where you want the output files committed.  Note: Commits to this branch will use `-force`.

### Optional input and output arguments

#### Optional input arguments for Code Refactor
- **CR_TARGET_FILES**: Specifies any target files or directories that you might want to limit the refactor to.  This is not required, and when not specified the action will use the root directory.  
  - **⚠️WARNING⚠️** this can get expensive if you have a lot of files, and you send them all to OpenAI.
- **CR_LOG_LEVEL**: Logging level supported by the action. Default is `INFO`.

### Secrets the action uses
While you can pass your `OPENAI_API_KEY` as an environment variable, obviously you shouldn't do that in the clear.  So set up a secret for that, and use it within your workflow.

### Environment variables the action uses

See: [Required input and output arguments](###Required-input-and-output-arguments)

### An example of how the action is used in a workflow

See the example in this repository: [.github\workflows\main.yml](.github\workflows\main.yml)
