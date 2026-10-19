
import csv
from collections import Counter
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


# --------------------------------------------------
# PATHS AND CONFIGURATION
# --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = BACKEND_DIR / "data" / "ticket_categories.csv"

MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODEL_DIR / "ticket_category_model.joblib"

EXPECTED_CATEGORIES = {
    "technical_issue",
    "billing",
    "account_access",
    "general_inquiry",
}

TEST_SIZE = 0.25
RANDOM_STATE = 42


# --------------------------------------------------
# LOAD AND VALIDATE DATASET
# --------------------------------------------------

def load_dataset():
    """Load and validate ticket-category training examples."""

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {DATASET_PATH}"
        )

    texts = []
    labels = []
    skipped_rows = 0

    with DATASET_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        required_columns = {
            "title",
            "description",
            "category",
        }

        if (
            not reader.fieldnames
            or not required_columns.issubset(reader.fieldnames)
        ):
            raise ValueError(
                "Dataset must contain title, description, "
                "and category columns."
            )

        for row in reader:
            title = (row.get("title") or "").strip()
            description = (row.get("description") or "").strip()
            category = (row.get("category") or "").strip().lower()

            if not title or not description or not category:
                skipped_rows += 1
                continue

            texts.append(f"{title}. {description}")
            labels.append(category)

    if len(texts) < 8:
        raise ValueError(
            f"Only {len(texts)} valid examples found. "
            "Add more training examples before training."
        )

    category_counts = Counter(labels)

    missing_categories = EXPECTED_CATEGORIES - set(category_counts)

    if missing_categories:
        raise ValueError(
            "The dataset is missing expected categories: "
            f"{sorted(missing_categories)}"
        )

    # Stratified splitting requires at least two examples
    # in each category to place examples in both sets.
    insufficient_categories = {
        category: count
        for category, count in category_counts.items()
        if count < 2
    }

    if insufficient_categories:
        raise ValueError(
            "At least two examples per category are required "
            "for stratified evaluation. Insufficient counts: "
            f"{insufficient_categories}"
        )

    print("\n===== DATASET SUMMARY =====")
    print(f"Dataset: {DATASET_PATH}")
    print(f"Valid examples: {len(texts)}")
    print(f"Skipped incomplete rows: {skipped_rows}")
    print(f"Categories: {sorted(category_counts)}")

    print("\nExamples per category:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")

    return texts, labels


# --------------------------------------------------
# BUILD CLASSIFICATION PIPELINE
# --------------------------------------------------

def build_model():
    """Create the TF-IDF and Logistic Regression pipeline."""

    return Pipeline(
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
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


# --------------------------------------------------
# EVALUATE MODEL
# --------------------------------------------------

def evaluate_model(model, X_test, y_test):
    """Print holdout evaluation metrics."""

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("\n===== MODEL EVALUATION =====")

    print(f"Test examples: {len(y_test)}")
    print(f"Test accuracy: {accuracy:.3f}")

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=sorted(EXPECTED_CATEGORIES),
            zero_division=0,
        )
    )

    labels = sorted(EXPECTED_CATEGORIES)

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=labels,
    )

    print("Confusion matrix (rows = actual, columns = predicted):")
    print("Category order:", labels)
    print(matrix)

    return accuracy


# --------------------------------------------------
# SAMPLE PREDICTIONS
# --------------------------------------------------

def show_sample_predictions(model):
    """Display predictions for representative ticket examples."""

    samples = [
        (
            "Duplicate subscription charge",
            "I was charged twice for my monthly subscription "
            "and need a refund.",
        ),
        (
            "Application crashes",
            "The dashboard crashes and displays a server error.",
        ),
        (
            "Cannot reset password",
            "I cannot reset my password or access my account.",
        ),
        (
            "Product information",
            "What features are included in the standard plan?",
        ),
    ]

    print("\n===== SAMPLE PREDICTIONS =====")

    for title, description in samples:
        text = f"{title}. {description}"

        probabilities = model.predict_proba([text])[0]
        best_index = probabilities.argmax()

        category = model.classes_[best_index]
        confidence = probabilities[best_index]

        print(f"\nTitle: {title}")
        print(f"Predicted category: {category}")
        print(f"Confidence: {confidence:.3f}")


# --------------------------------------------------
# TRAIN AND SAVE MODEL
# --------------------------------------------------

def main():
    texts, labels = load_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    print("\n===== TRAINING SUMMARY =====")
    print(f"Training examples: {len(X_train)}")
    print(f"Test examples: {len(X_test)}")

    model = build_model()
    model.fit(X_train, y_train)

    accuracy = evaluate_model(model, X_test, y_test)

    # Fit a final model on all available data after evaluation.
    # The holdout score above still reflects the separate test set.
    final_model = build_model()
    final_model.fit(texts, labels)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(final_model, MODEL_PATH)

    print(f"\nFinal model saved to: {MODEL_PATH}")
    print(f"Holdout accuracy: {accuracy:.3f}")

    show_sample_predictions(final_model)

    print("\nTraining completed successfully.")


if __name__ == "__main__":
    main()
