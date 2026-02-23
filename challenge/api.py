from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd

from challenge.model import DelayModel

app = FastAPI()

model = DelayModel()

# Valid Values
VALID_TIPOVUELO = {"I", "N"}
VALID_MES = set(range(1, 13))
VALID_OPERA = {
    "Aerolineas Argentinas",
    "Grupo LATAM",
    "Sky Airline",
    "Copa Air",
    "Latin American Wings",
}

class Flight(BaseModel):
    OPERA: str
    TIPOVUELO: str
    MES: int

class PredictionRequest(BaseModel):
    flights: List[Flight]

@app.post("/predict")
def predict(request: PredictionRequest):
    
    for flight in request.flights:
        if flight.MES not in VALID_MES:
            raise HTTPException(status_code=400, detail="Invalid MES")
        
        if flight.TIPOVUELO not in VALID_TIPOVUELO:
            raise HTTPException(status_code=400, detail="Invalid TIPOVUELO")
        
        if flight.OPERA not in VALID_OPERA:
            raise HTTPException(status_code=400, detail="Invalid OPERA")

    data = pd.DataFrame([f.dict() for f in request.flights])
    features = model.preprocess(data)
    predictions = model.predict(features)

    return {"predict": predictions}