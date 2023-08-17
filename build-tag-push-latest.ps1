# Build the dockerfile, tag it with latest, and push it to the registry

# Docker hub
docker build -t aronweiler/github-actions:latest .
docker push aronweiler/github-actions:latest

# Medtronic
# docker build -t case.artifacts.medtronic.com/ventilation-docker-dev-local/prototypes/code-reviewer:latest .
# docker push case.artifacts.medtronic.com/ventilation-docker-dev-local/prototypes/code-reviewer:latest