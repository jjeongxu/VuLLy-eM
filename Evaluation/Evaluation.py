import os, json, time, uuid, re, sys
from pathlib import Path
from tqdm import tqdm
from sklearn.metrics import f1_score, accuracy_score, classification_report


try:
    from openai import OpenAI
    client = OpenAI(api_key="API-Key")                 # Secret API-Key
    is_v1  = True
    from openai import OpenAIError as OAIErr
except ModuleNotFoundError:
    import openai
    client = openai
    is_v1  = False
    from openai.error import OpenAIError as OAIErr

# Initializing things..
DATA_PATH   = Path("converted_test_dataset.jsonl")               # Test set path
FT_MODEL    = "Fine-tuned Model ID"                              # Fine-tuned Model ID
PLAIN_MODEL = "gpt-3.5-turbo"                                    # Plain Model ID
POS_LABEL   = "1"                                                # For f1_score()

SYSTEM_PROMPT = (
    "You are a vulnerability detection model. "
    "Reply ONLY with 1 (vulnerable) or 0 (safe)."
)
USER_TEMPLATE = (
    "Check if the following code has vulnerabilities.\n"
    "```\n{code}\n```\n"
    "Reply only '1' or '0'. 1 if Vulnerable, 0 if Safe."
)

MAX_RETRY = 3
DELAY_SEC = 2

def load_jsonl(path: Path):
    inputs, labels = [], []
    with path.open(encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            inputs.append(obj["input"].strip())
            labels.append(str(obj["label"]))      # 숫자 → 문자열
    return inputs, labels

def call_gpt(model: str, prompt: str): # Reference: https://joymaster.tistory.com/entry/ChatGPT-API-%EC%9D%B4%EC%9A%A9%ED%95%98%EA%B8%B0-GPT4-GPT35Davinci
    for attempt in range(MAX_RETRY):
        try:
            if is_v1:
                r = client.chat.completions.create(
                    model=model,
                    temperature=0.3,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": prompt}
                    ],
                )
                return r.choices[0].message.content.strip()
            else:
                r = client.ChatCompletion.create(
                    model=model,
                    temperature=0.3,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": prompt}
                    ],
                )
                return r["choices"][0]["message"]["content"].strip()
        except OAIErr as e:
            if attempt == MAX_RETRY - 1:
                raise
            time.sleep(DELAY_SEC * 2**attempt)

def normalize(txt: str) -> str: # Check whether response is 0(secure) or 1(vuln)
    m = re.search(r"\b([01])\b", txt)
    return m.group(1) if m else "0"

def evaluate(model, inputs, labels, sample_print=3):
    preds = []
    for idx, code in enumerate(tqdm(inputs, desc=f"Query {model[:40]}")):
        prompt = USER_TEMPLATE.format(code=code)
        out    = call_gpt(model, prompt)
        if idx < sample_print:                      # print Test
            print(f"\n── Sample {idx} ({model}) ──\n{out}\n")
        preds.append(normalize(out))

    f1  = f1_score(labels, preds, pos_label=POS_LABEL)
    acc = accuracy_score(labels, preds)
    rep = classification_report(
        labels, preds,
        target_names=["Safe (0)", "Vulnerable (1)"],
        digits=2,
        zero_division=0
    )
    return f1, acc, rep


def main():
    if not DATA_PATH.exists():
        sys.exit(f"File not found: {DATA_PATH}")

    inputs, labels = load_jsonl(DATA_PATH)

    print("\n=== Fine-tuned model ===")
    f1, acc, rep = evaluate(FT_MODEL, inputs, labels)
    print(f"F1 : {f1:.4f}\nAcc: {acc:.4f}\n{rep}")

    print("\n=== Plain model ===")
    f1, acc, rep = evaluate(PLAIN_MODEL, inputs, labels)
    print(f"F1 : {f1:.4f}\nAcc: {acc:.4f}\n{rep}")

if __name__ == "__main__":
    main()
