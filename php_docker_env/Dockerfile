FROM php:8.2-fpm

RUN apt-get update \
    && apt-get install -y nginx \
    && docker-php-ext-install pdo_mysql \
    && rm -rf /var/lib/apt/lists/*

COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY index.php /var/www/html/index.php

EXPOSE 80
CMD ["/entrypoint.sh"]
