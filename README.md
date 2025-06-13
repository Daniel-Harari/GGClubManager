# GGClubManager

A FastAPI-based club management system.

## Prerequisites

- Docker installed on your system
  - [Docker Installation Guide](https://docs.docker.com/get-docker/)
- Git (optional, for cloning the repository)


### Environment Setup Instructions

1. **Local Development**
   - Copy the `.env.example` file to `.env`
   ```bash
   cp .env.example .env
   ```
   - Edit the `.env` file with your specific values


## Quick Start with Docker

1. **Clone the repository** (if using Git)
   ```bash
   git clone <repository-url>
   cd GGClubManager
   ```

2. **Build the Docker image**
   ```bash
   docker build -t ggclubmanager:latest .
   ```

3. **Run the container**
   ```bash
   docker run -p 8080:8080 ggclubmanager:latest
   ```

4. **Access the application**
   - Main application: [http://localhost:8080](http://localhost:8080)
   - API documentation: [http://localhost:8080/docs](http://localhost:8080/docs)
