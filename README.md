# Smart-Note-Assistant

## Introduction

Smart-Note-Assistant is a web application designed to assist users with note-taking, task management, and calendar integration. It leverages various APIs to provide a seamless user experience.

[Documentation](https://docs.google.com/document/d/1s-PCBP9Gy_LqdBJMIXq9yLylK9HWw8iIbncAuSw35Eo/edit?usp=sharing)

## Prerequisites

To run this application locally, you need to have the following installed on your machine:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Caddy](https://caddyserver.com/docs/install) (for HTTPS support)

## Installation

### 1. Clone the Repository

First, clone the repository to your local machine:

```sh
git clone https://github.com/htamlive/MnemeAI---Smart-Note-Assistant.git
cd Smart-Note-Assistant
```

### 2. Create a Docker Network

Create a Docker network to allow containers to communicate with each other:

```sh
docker network create same_network
```

### 3. Build and Run the Containers

Use Docker Compose to build and run the containers:

```sh
docker-compose up --build -d
```

### 4. Expose Ports with Caddy

Create a `Caddyfile` in the root directory of the project to expose ports 5000, 8080, and 8081:

```Caddyfile
:5002 {
    reverse_proxy localhost:5000
}

:8082 {
    reverse_proxy localhost:8080
}

:8083 {
    reverse_proxy localhost:8081
}
```

Start Caddy with the following commands:

```sh
sudo apt-get install -y caddy
caddy start
```

### 5. Verify the Setup

Verify that your services are running by navigating to the following URLs in your web browser:

- http://your-domain-or-ip:5002
- http://your-domain-or-ip:8082
- http://your-domain-or-ip:8083

## Configuration

### Environment Variables

Make sure to set the necessary environment variables in a `.env` file or directly in your Docker Compose file for proper configuration. An example of the `.env` file can be found in `example.env`.


### OAuth2 Setup

Ensure you have set up your OAuth2 credentials correctly. The callback URLs should be added to your OAuth2 provider settings, such as Google, with the correct redirect URIs.

## Usage

Once the containers are up and running, you can access the application through your web browser and start using the features provided by Smart-Note-Assistant.

## Troubleshooting

If you encounter any issues, here are some common solutions:

- **Ports Already in Use**: Ensure that the ports 5000, 8080, and 8081 are not being used by other applications.
- **Caddy Errors**: Check the Caddy logs for any issues related to configuration or proxying.
- **Environment Variables**: Double-check that all required environment variables are set correctly.

## Contributing

The project is open to contribution, do reach out for suggestions!

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
