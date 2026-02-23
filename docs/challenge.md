**Software Engineer (ML & LLMs) Challenge**

***Author: Ariel Aaron Argomedo Madrid***

**Executive Summary**

The provided Jupyter notebook file (exploration.ipynb) was refactored into a production-ready Python module and deployed 
as a scalable API using FastAPI and Google Cloud Run.

***Part I - Model Refactoring***
The exploration.ipynb notebook proposed two different models. The selected model was chosen based on:
    * Predictive performance (F1-score)
    * Stability
    * Simplicity

Given this is a binary classification problem (delay vs no delay), the selected model offers a good trade-off between interpretability and performance.

The notebook was converted into a modular file model.py following good engineering practices:
    * Removed exploratory and notebook-only code
    * Encapsulated logic into a reusable class
    * Encapsulated logic into a reusable class
    * Eliminated hardcoded paths
    * Fixed potential data inconsistencies
    * Ensured model loads once per execution context

The model passes "make model-test"

***Part II - API Implementation (FastAPI)***
The model was deployed through a REST API using FastAPI

    * Pydantic models used for input validation
    * Clear separation between request handling and inference logic
    * Proper HTTP error handling
    * Model instantiated once at application startup (singleton pattern)
This avoids reloading the model per request and significantly reduces latency impact.
The API passes "make api-test"

***Part III - Cloud Deployment (GCP Cloud Run)***
The API was containerized using Docker and deployed to Google Cloud Run.

The decision to use Cloud Run is based on the following points:
    * Automatic scaling
    * Simple container deployment model

A stress test was executed using concurrent users.
The service remained stable under concurrent load, validating correctness and scalability.
Finally, the API passes "make stress-test"

***Part IV - CI/CD Implementation***
A full CI/CD pipeline was implemented using GitHub Actions.

CI: on every push install dependencies and run unit test 
CD: on push to "main" the docker image is built and pushed to the Artifact Registry to finally deploy to Cloud Run.
This guarantees reproducibility and automated releases.

