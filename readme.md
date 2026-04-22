# Agreement Error Detector 

This project detects subject-verb agreement errors in English sentences using a fine-tuned transformer model.

## 🚀 Features
- Detects agreement errors (e.g., "She go" → "go" highlighted)
- Handles complex cases like:
  - "The group of students are..."
  - "Everyone have..."
- Hybrid approach (ML + rule-based correction)
- Dark UI frontend

---

## 🏗️ Tech Stack

### Frontend
- React (Vite)

### Backend
- FastAPI

### AI Model
- Fine-tuned RoBERTa (Hugging Face Transformers)

---


added one more model for complete error detections

that modesl usese sentence level classification to detect the errors usiing the roberta model

## ⚙️ Setup Instructions

### 1. Clone repo

```bash
git clone https://github.com/YOUR_USERNAME/agreement-error-detector.git
cd agreement-error-detector

##   backend setup
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
 
## Run Backend
uvicorn app:app --reload --port 8000


