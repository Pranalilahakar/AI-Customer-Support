# Ticket Category Classifier — Evaluation Report

## 1. Overview

The AI Customer Support & Ticket Management System uses a machine-learning classifier to recommend a category for incoming support tickets.

The classifier uses TF-IDF text features and Logistic Regression to classify tickets into four categories:

- `account_access`
- `billing`
- `general_inquiry`
- `technical_issue`

The purpose of this evaluation is to measure the model's initial classification performance on a holdout test dataset and document its limitations.

## 2. Dataset Summary

The training dataset is located at:

`backend/data/ticket_categories.csv`

| Metric | Result |
|---|---:|
| Total valid examples | 48 |
| Incomplete rows skipped | 0 |
| Number of categories | 4 |
| Examples per category | 12 |
| Training examples | 36 |
| Holdout test examples | 12 |

The dataset is small and balanced, with 12 examples per category. Each category has three examples in the holdout test set.

## 3. Evaluation Results

**Overall holdout accuracy: 91.7% (11 out of 12 examples classified correctly).**

| Category | Precision | Recall | F1-score | Test examples |
|---|---:|---:|---:|---:|
| Account access | 1.00 | 1.00 | 1.00 | 3 |
| Billing | 1.00 | 1.00 | 1.00 | 3 |
| General inquiry | 1.00 | 0.67 | 0.80 | 3 |
| Technical issue | 0.75 | 1.00 | 0.86 | 3 |
| **Overall accuracy** | — | — | **0.92** | **12** |

### Interpretation

- **Account access:** All three test examples were classified correctly.
- **Billing:** All three test examples were classified correctly.
- **General inquiry:** Two of the three examples were classified correctly.
- **Technical issue:** All three actual technical-issue examples were classified correctly, although one prediction in this category was a false positive.

The confusion matrix showed one general inquiry incorrectly classified as a technical issue. The remaining 11 examples were classified correctly.

## 4. Prediction Confidence

Sample prediction confidence scores ranged from **0.388 to 0.563**.

These scores reflect the classifier's output for the selected class. They should not be treated as guaranteed probabilities that a prediction is correct.

The confidence range and the small evaluation dataset indicate that further testing and a larger dataset are needed before considering confidence-based automation.

## 5. Limitations

The current evaluation has several limitations:

1. **Small dataset:** Only 48 valid examples were available.
2. **Small holdout set:** The test set contains just 12 examples, with three per category.
3. **Limited representativeness:** The dataset may not capture the language, spelling variations, ambiguity, and diversity of real customer-support tickets.
4. **Uncertain generalization:** An accuracy of 91.7% on this small holdout set does not establish that the classifier will achieve similar accuracy in production.
5. **Confidence limitations:** Prediction confidence should not be interpreted as a guarantee of correctness.

These results should be considered preliminary prototype evaluation results.

## 6. Responsible Use

- Treat predicted categories as recommendations, not unquestionable decisions.
- Allow support agents to correct misclassified tickets.
- Do not use these metrics alone to justify autonomous customer-impacting decisions.
- Keep training data free of passwords, authentication codes, and unnecessary sensitive customer information.
- Evaluate the model again when the training dataset changes.

## 7. Recommended Improvements

The following improvements are recommended:

1. Collect more diverse and representative support-ticket examples.
2. Verify category labels for accuracy and consistency.
3. Expand the dataset across all four categories.
4. Use stratified cross-validation or another suitable evaluation strategy alongside a holdout test set.
5. Track per-category precision, recall, F1-score, and the confusion matrix.
6. Test the classifier on realistic examples that were not used during training.
7. Consider a human-review threshold for uncertain predictions only after that threshold has been evaluated.
8. Re-run the evaluation whenever the model or training data changes.

## 8. Reproducing the Evaluation

Run the following commands from the `backend` directory.

Train the classifier and produce the evaluation output:

```powershell
python .\app\ai\train_classifier.py
```

Run the backend tests:

```powershell
python -m pytest .\tests -q
```

The latest recorded backend test result was:

```text
36 passed, 1 warning
```

The warning concerned a Starlette/httpx test-client compatibility deprecation.

## 9. Conclusion

The initial classifier achieved **91.7% holdout accuracy on 12 test examples**, correctly classifying 11 of them. This is a promising demonstration that text classification can assist ticket categorization in the project.

However, the small dataset and holdout set substantially limit the strength of this result. The classifier should remain an assistive prototype while the dataset is expanded and evaluation is strengthened.

The reported metrics describe the recorded evaluation run and should be regenerated when the training data, model, or evaluation procedure changes.
