# Basically:

While setting up server got ssh keys (.gem) 

Used the IP address to ssh into the vm (ssh -i signin.pem linux1@148.100.108.101) 

Set up a dockerfile for frontend and backend setup a dockercompose file in the adam directory linking into the frontend and backend directories

built the docker compose file (docker compose build --no-cache)

ran the docker compose file to launch the other dockerfiles (docker compose up -d)


## Troubleshooting 

Can use "docker ps" to view all active ports and close ports using "docker stop <container_id>"

## commands

docker compose up -d  (Run docker compose)

docker compose build --no-cache (Docker compose build)

docker compose down (Stop docker compose)

docker compose logs -f (view docker compose logs)

docker ps (Display docker ids and ports)

docker stop <container_id> (Stop docker port)
