FROM nginx:1.21.6-alpine
COPY default.conf /etc/nginx/conf.d/
COPY frontend /usr/share/nginx/html

RUN apk add --upgrade apk-tools && \
 apk update && \
 apk upgrade --available && \
 rm -rf /var/cache/apk/*
RUN chgrp -R 0 \
 /var/cache/nginx \
 /var/run \
 /usr/lib/nginx/ \
 /etc/nginx \
 /var/log/nginx && \
 chmod -R g=u \
 /var/cache/nginx \
 /var/run \
 /usr/lib/nginx/ \
 /etc/nginx \
 /var/log/nginx \
 /etc/passwd
USER 1001
CMD ["nginx", "-g", "daemon off;"]