# Rapid Serial Visual Presentation

## Features

RSVP for reading enables users to quickly and effectively move through text material. It includes the following features:

- Implementation of the RSVP reading technique
- Adaptability to different reading speeds
- Use of AI for post-reading test generation via LLM (Large Language Model) to evaluate comprehension

## Prerequisites

To run this web app, you will need:

- Docker
- Accounts on Large Language Model (LLM) services

## Environment Setup

Before starting up the application, you will need to set an environment variable `GROQ_API_KEY` with your LLM service API key. This is necessary for the test generation feature to function properly.

This application leverages litellm to access and interact with various LLM (Large Language Model) services. The model used can be specified using the `LLM_MODEL` environment variable in the docker-compose.yaml file. This allows for easy customization and switching between different models as per your requirements.

For a comprehensive list of supported models and their respective names, please refer to the [litellm documentation](https://docs.litellm.ai/docs/). The documentation also provides detailed instructions on how to configure API authentication using the appropriate environment variables for each model.


## Setup and Installation

Begin by running Docker Compose to start the application:

```
docker compose up
```

Following the initial launch, access the app container and execute the migration command for the first run:

```
docker compose exec app alembic upgrade head
```

## Usage

Navigate to `http://localhost:8000` in your browser.

## License

This project is governed by the MIT License - see the [LICENSE.md](LICENSE.md) file for detailed information.
