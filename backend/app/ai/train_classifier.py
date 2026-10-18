import csv
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BACKEND_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BACKEND_DIR / "data" / "ticket_categories.csv"
MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODEL_DIR / "ticket_category_model.joblib"


def load_dataset():
    texts = []
    labels = []

    with DATASET_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        required_columns = {"title", "description", "category"}
        if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
            raise ValueError(
                "Dataset must contain title, description, and category columns."
            )

        for row in reader:
            title = (row["title"] or "").strip()
            description = (row["description"] or "").strip()
            category = (row["category"] or "").strip()

            if not title or not description or not category:
                continue

            texts.append(f"{title}. {description}")
            labels.append(category)

    if len(texts) < 8:
        raise ValueError("Not enough valid training examples.")

    if len(set(labels)) < 2:
        raise ValueError("The dataset must contain at least two categories.")

    return texts, labels


def main():
    texts, labels = load_dataset()

    print(f"Total examples: {len(texts)}")
    print(f"Categories: {sorted(set(labels))}")

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels,
    )

    model = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    print(f"\nTraining examples: {len(X_train)}")
    print(f"Test examples: {len(X_test)}")
    print(f"Test accuracy: {accuracy_score(y_test, predictions):.3f}")
    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Model saved to: {MODEL_PATH}")

    print("\nSample predictions:")
    samples = [
        "I was charged twice for my monthly plan",
        "The application crashes when I open the dashboard",
        "I cannot reset my password",
        "What plans do you offer to new customers?",
    ]

    for sample in samples:
        probabilities = model.predict_proba([sample])[0]
        best_index = probabilities.argmax()
        category = model.classes_[best_index]
        confidence = probabilities[best_index]

        print(f"- {sample}")
        print(f"  Predicted category: {category}")
        print(f"  Model confidence: {confidence:.3f}")


if __name__ == "__main__":
    main()
