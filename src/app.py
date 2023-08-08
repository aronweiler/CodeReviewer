import os

output = "Hello World!  Fake summary ;)"

# Write the output to the $GITHUB_OUTPUT environment file
# See: https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action?learn=create_actions&learnProduct=actions#writing-the-action-code
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"summary={output}")

