# Инструкция по развёртыванию QuizRumble

## Требования к серверу

- **ОС**: Ubuntu 22.04 LTS или новее
- **Python**: 3.11+
- **PostgreSQL**: 15+
- **Redis**: 7+
- **Docker** и **Docker Compose** (рекомендуемый способ)
- **Git**
- **Nginx** (для production)

## Подготовка сервера

### 1. Обновление системы

```bash
sudo apt update && sudo apt upgrade -y


# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo apt install docker-compose-plugin -y

# Перезагрузка для применения групп
newgrp docker


sudo apt install git -y


sudo mkdir -p /opt/quizrumble
sudo chown $USER:$USER /opt/quizrumble
cd /opt/quizrumble


git clone https://gitlab.informatics.ru/2025-2026/vk/s105d/practice/quizrumble.git .


cd /opt/quizrumble
docker compose build
docker compose up -d


docker compose exec web python manage.py migrate


docker compose exec web python manage.py collectstatic --noinput


docker compose exec web python manage.py createsuperuser


docker compose ps
# Все контейнеры должны быть в статусе Up

curl http://localhost:8000


sudo apt install nginx -y


sudo nano /etc/nginx/sites-available/quizrumble


nginx
server {
    listen 80;
    server_name ваш-домен.com;

    client_max_body_size 10M;

    location /static/ {
        alias /opt/quizrumble/staticfiles/;
    }

    location /media/ {
        alias /opt/quizrumble/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}


sudo ln -s /etc/nginx/sites-available/quizrumble /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx


sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d ваш-домен.com


