from transformers import AutoModelForSequenceClassification


def build_model(cfg: dict):
    return AutoModelForSequenceClassification.from_pretrained(cfg["base_model"], num_labels=3)
