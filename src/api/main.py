from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from inference import predict_price, batch_predict, load_artifacts, artifacts
from schemas import HousePredictionRequest, PredictionResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_artifacts()
    yield
    artifacts.clear()


app = FastAPI(
    title="House Price Prediction API",
    description="An API for predicting house prices based on various features.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=dict)
def health_check():
    return {"status": "healthy", "model_loaded": "model" in artifacts}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: HousePredictionRequest):
    return predict_price(request)


@app.post("/batch-predict", response_model=list[float])
def batch_predict_endpoint(requests: list[HousePredictionRequest]):
    return batch_predict(requests)