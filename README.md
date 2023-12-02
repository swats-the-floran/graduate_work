# Проектная работа: диплом

1. Перейти в директорию **infra**
    ```shell
    cd infra
    ```
2. Запустить сборку образов
    ```shell
    docker-compose -f docker-compose.yml up  --build 
    ```
3. Сервисы доступны по адресам:
   - http://localhost/api/openapi-movies
   - http://localhost/api/openapi-auth
   - http://localhost/api/openapi-ugc

