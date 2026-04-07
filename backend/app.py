from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
import spacy

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "./final_lang8_model_20k"

label2id = {"O": 0, "AGR_ERR": 1}
id2label = {v: k for k, v in label2id.items()}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
nlp = spacy.load("en_core_web_sm")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH, local_files_only=True)
model.to(device)
model.eval()


class SentenceRequest(BaseModel):
    sentence: str


def rule_based_fix(tokens, preds):
    text = " ".join(tokens).lower()

    singular_patterns = [
        "group of",
        "number of",
        "list of",
        "collection of",
        "set of",
        "series of",
    ]

    if any(p in text for p in singular_patterns):
        for i, tok in enumerate(tokens):
            if tok.lower() in ["are", "were", "have"]:
                preds[i] = "AGR_ERR"

    if "everyone" in text or "each of" in text:
        for i, tok in enumerate(tokens):
            if tok.lower() == "have":
                preds[i] = "AGR_ERR"

    return preds


def predict_tokens(sentence: str):
    doc = nlp(sentence)
    tokens = [token.text for token in doc]

    encoded = tokenizer(
        tokens,
        is_split_into_words=True,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=256
    )

    word_ids = encoded.word_ids(batch_index=0)
    encoded = {k: v.to(device) for k, v in encoded.items()}

    with torch.no_grad():
        outputs = model(**encoded)

    logits = outputs.logits
    predictions = torch.argmax(logits, dim=-1).squeeze().cpu().tolist()

    final_preds = []
    used_word_ids = set()

    for pred, word_id in zip(predictions, word_ids):
        if word_id is None:
            continue
        if word_id in used_word_ids:
            continue
        used_word_ids.add(word_id)
        final_preds.append(id2label[pred])

    final_preds = rule_based_fix(tokens, final_preds)

    result = []
    for tok, lab in zip(tokens, final_preds):
        result.append({
            "token": tok,
            "label": lab
        })

    return result


@app.get("/")
def root():
    return {"message": "Agreement error detection API running"}


@app.post("/predict")
def predict(req: SentenceRequest):
    sentence = req.sentence.strip()
    if not sentence:
        return {"tokens": []}

    tokens = predict_tokens(sentence)
    return {"tokens": tokens}