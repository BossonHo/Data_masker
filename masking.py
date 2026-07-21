# masking.py
import re
import spacy
from langdetect import detect, LangDetectException

# 1. 初始化模型字典，用於快取已載入的模型
NLP_MODELS = {}

# 2. 定義模型名稱對應的語言
MODEL_MAP = {
    'zh': "zh_core_web_lg",
    'en': "en_core_web_sm",
    # 支援更多語言時，可以在此處擴展
}

def get_nlp_model(lang_code):
    """
    根據語言代碼取得或載入對應的 spaCy 模型。
    """
    model_name = MODEL_MAP.get(lang_code)
    
    if not model_name:
        # 如果語言不在列表內，預設使用中文模型
        model_name = MODEL_MAP['zh']
    
    if model_name not in NLP_MODELS:
        try:
            print(f"正在載入 spaCy 模型: {model_name}...")
            # 載入模型並存入快取
            NLP_MODELS[model_name] = spacy.load(model_name)
        except OSError:
            # 如果模型未下載，提醒使用者並返回 None
            print(f"錯誤：無法載入模型 '{model_name}'。請執行 'python -m spacy download {model_name}'")
            return None 
            
    return NLP_MODELS[model_name]


# PII 正則表達式 (通用格式，與語言無關)
PII_PATTERNS = {
    "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    "PHONE": r'(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4})',
    "SSN": r'\b\d{3}-\d{2}-\d{4}\b', 
    "TW_ID": r'[A-Z]\d{9}', 
}

# NER 實體標籤 (統一 NER 遮罩的名稱)
NER_LABELS = {
    "PERSON": "[NAME]",
    "PER": "[NAME]", 
    "ORG": "[ORG]",
    "LOC": "[GPE/LOC]",
    "GPE": "[GPE/LOC]",
}


def mask_text(text, mode="semantic"):
    """
    text: str, 原始文字
    mode: "semantic" or "strict"
    """
    
    # 1. 語言偵測
    try:
        lang_code = detect(text)
    except LangDetectException:
        # 偵測失敗，預設為中文
        lang_code = 'zh' 
    
    # 2. 取得對應語言的 spaCy 模型
    nlp = get_nlp_model(lang_code)
    
    if not nlp:
        # 如果模型載入失敗，則只執行 PII 正則表達式遮罩
        masked_text = text
    else:
        masked_text = text
        doc = nlp(text)

        # --- NER Masking ---
        entities = sorted(doc.ents, key=lambda x: len(x.text), reverse=True)
        
        for ent in entities:
            label = ent.label_
            if label in NER_LABELS:
                placeholder = NER_LABELS[label] if mode == "semantic" else "*****"
                masked_text = re.sub(re.escape(ent.text), placeholder, masked_text)

    # --- Regex-based Masking ---
    final_masked_text = masked_text
    for label, pattern in PII_PATTERNS.items():
        placeholder = f"[{label}]" if mode == "semantic" else "*****"
        final_masked_text = re.sub(pattern, placeholder, final_masked_text)

    return final_masked_text