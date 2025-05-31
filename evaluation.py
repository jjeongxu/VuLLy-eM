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



def test_model(code):
    response = client.chat.completions.create(
    model = "gpt-3.5-turbo",   #fine-tuning model id
    messages = [
        {"role": "system", "content": "Returns 1 if your code has a vulnerability,  0 if it is secure."},
        {"role": "user", "content": "Check if the following code has vulnerabilities.\n{code}"}
      ]
    )

    answer = response.choices[0].message.content
    return answer

y_true = []         # 실제값
y_prediction = []   # 예측값

for item in test_dataset:
    y_true.append(item["label"])
    prediction = test_model(item["input"])
    prediction = "1" if "1" in prediction else "0"  # 정규화
    y_prediction.append(prediction)

print("F1 Score: ", f1_score(y_true, y_prediction, pos_label = "1"))
print("Accuracy:", accuracy_score(y_true, y_prediction))
print(classification_report(y_true, y_prediction, target_names=["Safe (0)", "Vulnerable (1)"]))
