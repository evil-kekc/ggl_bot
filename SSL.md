# Nginx as a server
To be able to use nginx as a server for any of our projects, we have to create a Docker Compose service for it. Docker will handle the download of the corresponding image and all the other tasks we used to do manually without Docker.
```bash
version: '3.9'
services:
  web:
    container_name: web
    image: nginx:alpine
    depends_on:
      - telegram-bot
    ports:
      - "80:80"
      - "443:443"
```
At anytime during the tutorial, you can run `docker-compose up` to start the environment and see if everything goes well.

We have now a working raw installation of nginx that listens to ports `80` for HTTP and `443` for HTTPS.
```bash
version: '3.9'

services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    restart: always
```
As I want the server to be always up and running, I tell Docker that it should take care of restarting the "webserver" service when it unexpectedly shuts down.
```bash
version: '3.9'

services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    restart: always
    volumes:
      - ${PWD}/nginx/conf/:/etc/nginx/conf.d/:ro
```
The ultimate goal of our installation isn't to serve the default welcome page of nginx. So, we need a way to update the nginx configuration and declare our website.

To accomplish that, we use the "volumes" feature of Docker. This means we map the folder located at `/etc/nginx/conf.d/` from the docker container to a folder located at `./nginx/conf/` on our local machine. Every file we add, remove or update into this folder locally will be updated into the container.

Note that I add a `:ro` at the end of the volume declaration. `ro` means "read-only". The container will never have the right to update a file into this folder. It is not a big deal, but consider it as a best practice. It can avoid wasting a few precious hours of debugging.

Now update the Docker Compose file as below:
```bash
version: '3.9'

services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    restart: always
    volumes:
      - ${PWD}/nginx/conf/:/etc/nginx/conf.d/:ro
      - ${PWD}/certbot/www:/var/www/certbot/:ro
```
And add the following configuration file into your `./nginx/conf/` local folder. Do not forget to update using your own data.
```bash
server {
    listen 80;
    listen [::]:80;

    server_name example.org www.example.org;
    server_tokens off;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://example.org$request_uri;
    }
}
```
The configuration is simple. We explain to nginx that it has to listen to port `80` (either on IPv4 or IPv6) for the specific domain name `example.org`.

By default, we want to redirect someone coming on port `80` to the same route but on port `443`. That's what we do with the `location /` block.

But the specificity here is the other `location` block. It serves the files Certbot need to authenticate our server and to create the HTTPS certificate for it.

Basically, we say "always redirect to HTTPS except for the `/.well-know/acme-challenge/` route".

We can now reload nginx by doing a rough `docker-compose restart` or if you want to avoid service interruptions (even for a couple of seconds) reload it inside the container using `docker-compose exec webserver nginx -s reload`.

# Create the certificate using Certbot
or now, nothing will be shown because nginx keeps redirecting you to a `443` port that's not handled by nginx yet. But everything is fine. We only want Certbot to be able to authenticate our server.

To do so, we need to use the docker image for certbot and add it as a service to our Docker Compose project.
```bash
version: '3.9'
services:
  web:
    container_name: web
    image: nginx:alpine
    depends_on:
      - telegram-bot
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ${PWD}/nginx/conf.d/:/etc/nginx/conf.d/:ro
      - ${PWD}/certbot/www:/var/www/certbot/:ro
    networks:
      - bot
    restart: always
    
  certbot:
    image: certbot/certbot:latest
    volumes:
      - ${PWD}/certbot/www/:/var/www/certbot/:rw
```
We now have two services, one for nginx and one for Certbot. You might have noticed they have declared the same volume. It is meant to make them communicate together.

Certbot will write its files into `./certbot/www/` and nginx will serve them on port 80 to every user asking for `/.well-know/acme-challenge/`. That's how Certbot can authenticate our server.

Note that for Certbot we used `:rw` which stands for "read and write" at the end of the volume declaration. If you don't, it won't be able to write into the folder and authentication will fail.

You can now test that everything is working by running` docker-compose run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ --dry-run -d example.org`. You should get a success message like "The dry run was successful".

Now that we can create certificates for the server, we want to use them in nginx to handle secure connections with end users' browsers.

Certbot create the certificates in the `/etc/letsencrypt/` folder. Same principle as for the webroot, we'll use volumes to share the files between containers.
```bash
version: '3.9'
services:
  web:
    container_name: web
    image: nginx:alpine
    depends_on:
      - telegram-bot
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ${PWD}/nginx/conf.d/:/etc/nginx/conf.d/:ro
      - ${PWD}/certbot/www:/var/www/certbot/:ro
      - ${PWD}/certbot/conf/:/etc/nginx/ssl/:ro
    networks:
      - bot
    restart: always
    
  certbot:
    image: certbot/certbot:latest
    volumes:
      - ${PWD}/certbot/www/:/var/www/certbot/:rw
      - ${PWD}/certbot/conf/:/etc/letsencrypt/:rw
```
Restart your container using `docker-compose restart`. Nginx should now have access to the folder where Certbot creates certificates.

However, this folder is empty right now. Re-run Certbot without the `--dry-run` flag to fill the folder with certificates:
```bash
docker-compose run --rm  certbot certonly --webroot --webroot-path /var/www/certbot/ -d example.org
```
Since we have those certificates, the piece left is the `443` configuration on nginx.
```bash
server {
    listen 80;
    listen [::]:80;
    server_name example.com;

    location / {
        return 301 https://$host$request_uri;
    }

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}

server {
    listen 443 ssl;
    server_name example.com www.example.com;
    server_tokens off;

    ssl_certificate /etc/nginx/ssl/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/live/example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH';

    location /webhook {
        proxy_pass http://telegram-bot:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /info {
        proxy_pass http://telegram-bot:5000/info;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /favicon.ico {
        access_log off;
        log_not_found off;
    }
}
```
Reloading the nginx server now will make it able to handle secure connection using HTTPS. Nginx is using the certificates and private keys from the Certbot volumes.

# Renewing the certificates
One small issue you can have with Certbot and Let's Encrypt is that the certificates last only 3 months. You will regularly need to renew the certificates you use if you don't want people to get blocked by an ugly and scary message on their browser.

But since we have this Docker environment in place, it is easier than ever to renew the Let's Encrypt certificates!

```bash
docker-compose run --rm certbot renew
```
This small "renew" command is enough to let your system work as expected. You just have to run it once every three months. You could even automate this process…