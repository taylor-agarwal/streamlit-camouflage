sudo yum update -y
sudu yum install -y git python3.8
# curl -sSL https://install.python-poetry.org | python3 -
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl start docker
sudo docker build --file=backend.dockerfile -t streamlit-camouflage-backend .
sudo docker build --file=frontend.dockerfile -t streamlit-camouflage-frontend .
sudo docker compose -f compose.yml up