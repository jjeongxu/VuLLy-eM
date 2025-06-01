from openai import OpenAI
import json
from sklearn.metrics import f1_score, classification_report, accuracy_score

client = OpenAI(api_key="")  #api key

test_dataset = []

with open("/content/file-test_merged.jsonl", "r") as f:
    for line in f:
        item = json.loads(line)

        label = next(m["content"].strip() for m in item["messages"] if m["role"] == "assistant") #test_set label 추출
        code = next(m["content"] for m in item["messages"] if m["role"] == "user") #test_set code 추출

        if label in ["0", "1"]:
            test_dataset.append({"input": code, "label": label})



def test_model(code, model_name):
    response = client.chat.completions.create(
        model=model_name,
        temperature=0,
        messages=[
            {"role": "system",
             "content": "You are a vulnerability detection model. Output 1 for vulnerable, 0 for safe."},
            {"role": "user",
             "content": f"Check if the following code has vulnerabilities.\n```c\n{code}\n```\nReturn only 1 or 0."}
        ]
    )
    return response.choices[0].message.content.strip()

y_true = []         # 실제값
y_prediction = []   # 예측값

for item in test_dataset:
    y_true.append(item["label"])
    prediction_text = test_model(item["input"], "gpt-3.5-turbo")  # plain
    prediction = "1" if prediction_text.startswith("1") else "0"
    y_prediction.append(prediction)

print("F1 Score: ", f1_score(y_true, y_prediction, pos_label = "1"))
print("Accuracy:", accuracy_score(y_true, y_prediction))
print(classification_report(y_true, y_prediction, target_names=["Safe (0)", "Vulnerable (1)"]))
