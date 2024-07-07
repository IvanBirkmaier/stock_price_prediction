# Twitter Data Scraping and Analysis Web Application

## Project Description

This project was developed as part of a module within my Bachelor's program at HTW Berlin. It is my first foray into the field of AI. The primary goal of this project was to create a web application that scrapes Twitter data using SNscraper, processes the data through a feature engineering pipeline, and enables analysis or training of a neural network with the data, which is then saved.

### Key Components

- **Data Scraping**: Utilizing SNscraper to collect Twitter data.
- **Feature Engineering Pipeline**: Processing the scraped data for analysis and model training.
- **Analysis and Model Training**: Allowing users to analyze the data or train a neural network.
- **Storage**: Trained models are saved for future use.

### Origin and Limitations

This project was developed as part of my studies at HTW Berlin and represents my initial steps into AI. Therefore, the model results are not significant. Additionally, as of 2024, it is no longer possible to scrape Twitter data, affecting the reproducibility of the project.

### Demonstration Videos

Two private YouTube videos are available to demonstrate and explain the setup and functionality of the application:

1. **[Episode 1](https://youtu.be/8xBfSqPxwR4)**: Shows the functionality and features of the application.
2. **[Episode 2](https://youtu.be/xcwguBuW3Gw)**: Provides a detailed guide on setting up and running the application.

### Setup Instructions

#### Frontend

1. **Start Frontend**: 
    ```bash
    cd frontend_docker
    make dockerstart
    ```
2. **Access Frontend**: Open [http://localhost:8081](http://localhost:8081). If this port is occupied, modify the `default.conf` file:
    ```nginx
    server {
        listen 8081; # Change this port if necessary
        # Other configurations...
    }
    ```
3. **Docker Installation Guide**: Follow the instructions [here](https://docs.docker.com/engine/install/ubuntu/).

#### Backend

1. **Access Backend**: Open [http://localhost:8000](http://localhost:8000).
2. **Start Backend**: 
    ```bash
    uvicorn backend.controller.apiController:app --reload
    ```
3. **Custom Port Configuration**: If port 8000 is occupied, specify a different host and port:
    ```bash
    uvicorn backend.controller.apiController:app --reload --host ${HOST} --port ${PORT}
    ```
4. **Update Origin URLs**: If ports are redefined, update the origin URLs in the `apiController` file.

#### Docker Commands

- Stop all running containers:
    ```bash
    docker kill $(docker ps -q)
    ```
- Remove all created containers:
    ```bash
    docker rm -vf $(docker ps -aq)
    ```
- Remove all created images:
    ```bash
    docker rmi -f $(docker images -aq)
    ```
- List all built images:
    ```bash
    docker images
    ```
- List all containers (including running ones):
    ```bash
    docker ps
    ```

### Required Installations

1. Docker
2. MySQL
3. (Optional) Makefile

## Tech Stack

### Backend

- **Framework**: FastAPI
- **Database**: MySQL
- **Languages and Libraries**: 
    - Python
    - Pandas
    - SQLAlchemy
    - NumPy
    - TextBlob
    - Torch (PyTorch)
    - SNscraper
    - Uvicorn
    - Matplotlib

### Frontend

- **Technologies**:
    - JavaScript
    - HTML
    - CSS
    - Nginx

### DevOps

- **Tools**:
    - Docker