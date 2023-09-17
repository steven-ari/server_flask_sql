# Perga
Digital Assistant for Document Management
## Installation

Steps mentioned here are for a new ubuntu server, for other OS (CentOS or macOS), you might need to check for variations of these steps

0. Install using this command on the root, and just follow the steps below if this step is not working
```bash
bash setup.sh
````

1. Install dependencies
```bash
sudo apt upgrade
````

2. Install docker (using apt recommended; make sure `sudo docker run hello-world` works) Link: https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository

3. Start both server and database from the `root`
```bash
docker compose up --build
```
About the command: https://docs.docker.com/engine/reference/commandline/compose_up/

DNS Configuration
Log in to your domain registrar's website.

Access your DNS management settings.

Create a new DNS record with the following configuration:

Type: A (Address)
Host: your-api-domain.com (or subdomain)
Value: Your server's IP address
Save the DNS record.

Source: https://www.programonaut.com/setup-ssl-with-docker-nginx-and-lets-encrypt/?utm_source=pocket_saves 
