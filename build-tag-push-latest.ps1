# Build the dockerfile, tag it with latest, and push it to the registry

docker build -t aronweiler/github-actions:latest .
docker push aronweiler/github-actions:latest
