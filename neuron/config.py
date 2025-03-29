import os
import torch

DATA_DIR = "data"
LOGS_DIR = "logs"
CHECKLIST_FILE = "Чек-лист.docx"
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
TORCH_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)