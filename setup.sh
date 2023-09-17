sudo apt-get update
sudo apt install docker.io docker-compose
sudo groupadd docker
sudo usermod -aG docker $USER
chmod +x ./services/web/entrypoint.sh
cp env.dev .env.dev
docker-compose up --build --force-recreate
