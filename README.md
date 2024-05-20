# Smart-Note-Assistant

## Installation

To run locally, install Docker and Docker-compose

```
docker-compose network create same_network
docker-compose up --build -d
```

Caddyfile is used with Caddy to expose ports 5000, 8080 and 8081 during deploymet

```
caddy start
```