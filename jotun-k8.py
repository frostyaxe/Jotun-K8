# JotunAI - Predictive Kubernetes Resource Management Solution
# 
# Author: Abhishek Prajapati
# Contact: prajapatiabhishek1996@gmail.com
#
# Description:
# JotunAI is a machine learning-based application that works with large datasets
# to predict the values required for managing Kubernetes resources in a predictive manner.
#
# Usage:
# Users are allowed to use the application, but modification or copying of the code 
# is strictly prohibited without prior permission from the author (Abhishek Prajapati).
#
# License:
# Unauthorized modification or redistribution is not allowed. Please contact the author for
# any permissions or questions regarding usage and licensing.
# Email: prajapatiabhishek1996@gmail.com

from loaders.models import get_models
from fastapi import FastAPI
from routers.routers import router 
from contextlib import asynccontextmanager
from updater.updater import JotunUpdater
from apscheduler.schedulers.background import BackgroundScheduler
from utils.db import JotunDBUtils
import sys
from sqlite3 import Error
from exceptions.exceptions import GracefulShutdown


def prerequiste() -> Error:
    """
    Perform the necessary prerequisites for the application to function correctly.

    This method ensures that all required configurations, resources, or dependencies
    are in place before the main operations of the application begin.

    Usage:
        Call this method at the start of the application to ensure the environment
        is ready before proceeding with further operations.

    Example:
        prerequiste()

    Notes:
        - This method may raise exceptions if the prerequisites are not met.
        - Ensure that you have appropriate access and configurations set before
          running this method.

    """
  
    db = JotunDBUtils("hash_tracker.db")
    if db.error:
        return db.error
    table_create_err = db.create_table()
    if table_create_err:
        return table_create_err

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager that handles the startup and graceful shutdown of the FastAPI application.
    This context manager is used to load models into memory, perform prerequisite checks, start a model 
    update process, and gracefully shut down the application if needed.

    Parameters:
    - app (FastAPI): The FastAPI application instance.

    """
    app.state.models = get_models("./models")       # Loads the model in the memory
    try:
        prerequisteErr = prerequiste()                  # performs pre-activities like hash tracker table creation
        if prerequisteErr:
            raise GracefulShutdown(prerequisteErr)
        
        def update():
            updater = JotunUpdater(app.state.models)
            isUpdated = updater.update()
            if isUpdated:
                print("One or more models have been updated. Reloading the models...")
                app.state.models.clear()
                app.state.models = get_models("./models") 
        update()       
        scheduler = BackgroundScheduler()
        scheduler.add_job(update, 'interval', minutes=15, id='update_models')
        scheduler.start()
        yield
    except GracefulShutdown as e:
        print(f"{e}")
    finally:
        app.state.models.clear()
        sys.exit(1)
        

app = FastAPI(lifespan=lifespan)


@app.get("/models",tags=["models"])
async def display_models():
    """
    Endpoint to display the list of available models in the application.

    Returns:
        dict: A dictionary containing a key "models" with a list of model names 
              (keys from `app.state.models`).
    
    Example response:
    {
        "models": ["model1", "model2", "model3"]
    }

    This endpoint can be used to check which models are currently loaded in memory
    in the FastAPI application.
    """
    return {"models": list(app.state.models.keys())}

# Include the router for model-related endpoints
app.include_router(router, prefix="/models", tags=["models"])
