import os
import logging

logging.basicConfig(level=logging.DEBUG)

github_output = os.environ.get("GITHUB_OUTPUT", "not available")
changes = os.environ.get("CHANGES", "None found")

output = "Hello World!  Fake summary ;)"

logging.debug(output)
logging.debug("GH Output: " + github_output)
logging.debug("Changes: " + changes)


# Write the output to the $GITHUB_OUTPUT environment file
# See: https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action?learn=create_actions&learnProduct=actions#writing-the-action-code
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"summary={output}")

