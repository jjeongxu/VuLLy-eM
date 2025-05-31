import argparse
import json

SYS_PROMPT = "I want you to act as a vulnerability detection model."

def make_chat_record(orig: dict) -> dict:
    user_msg = f"{orig.get('instruction', '').rstrip()}\n```{orig.get('input', '').lstrip()}```"
    assistant_msg = orig.get('output', '')

    return {
        "messages": [
            {"role": "system",    "content": SYS_PROMPT},
            {"role": "user",      "content": user_msg},
            {"role": "assistant", "content": assistant_msg}
        ]
    }

def main():
    cnt_in, cnt_out = 0, 0
    with open('/content/Cleanvul_Processed_Dataset.jsonl', "r", encoding="utf-8") as fin, \
         open('/content/Cleanvul_GPT_Trainset.jsonl', "w", encoding="utf-8") as fout: # in_file_path && out_file_path

        for line in fin:
            if not line.strip():
                continue
            cnt_in += 1
            orig = json.loads(line)
            chat_rec = make_chat_record(orig)
            fout.write(json.dumps(chat_rec, ensure_ascii=False) + "\n")
            cnt_out += 1

main()