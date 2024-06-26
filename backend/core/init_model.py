# backend/core/init_model.py

from transformers import EncoderDecoderModel, BertTokenizerFast
from safetensors.torch import load_file
import torch

def load_model(model_path = "models/bert2bert_shared-spanish-finetuned-summarization"):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    state_dict = load_file(f'{model_path}/model.safetensors')
    model = EncoderDecoderModel.from_pretrained(model_path, state_dict=state_dict).to(device)
    tokenizer = BertTokenizerFast.from_pretrained(model_path)
    return model, tokenizer