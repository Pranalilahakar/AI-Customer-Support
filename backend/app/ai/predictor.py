from functools import lru_cache
from pathlib import Path

import joblib


MODEL_PATH = Path(__file__).resolve().parent / "models" / "ticket_category_model.joblib"


@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            "Ticket category model is missing. Train the model first."
        )

    return joblib.load(MODEL_PATH)


def predict_category(title: str, description: str) -> dict:
    model = load_model()
    text = f"{title.strip()}. {description.strip()}"

    probabilities = model.predict_proba([text])[0]
    best_index = int(probabilities.argmax())

    return {
        "category": str(model.classes_[best_index]),
        "confidence": round(float(probabilities[best_index]), 4),
    }
