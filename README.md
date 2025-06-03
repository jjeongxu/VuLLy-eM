### "VuLLy-eM: Bully Vulnerabilities using LLMs"

A team project for the AI Programming course at Gachon University, Semester 1 2025



```
CleanVul and PatchDB were used as the train dataset. However, PatchDB cannot be made public due to licensing issues, so it is not uploaded to this project's GitHub.
```



## Steps to reproduce 1(Fine-tuning by yourself)

1. https://platform.openai.com/finetune 에 접속하여, API 키 할당받기

2. **<u>Train set</u>**으로 https://github.com/jjeongxu/VuLLy-eM/blob/main/Train_Datasets/file-train_merged.jsonl 를 사용 

   **<u>Validation set</u>**으로 https://github.com/jjeongxu/VuLLy-eM/blob/main/Train_Datasets/file-validation_merged.jsonl 를 사용하여 Fine-tuning 진행

3. Test set으로 https://github.com/jjeongxu/VuLLy-eM/blob/main/Evaluation/converted_test_dataset.jsonl 를 사용하여, https://github.com/jjeongxu/VuLLy-eM/blob/main/Evaluation/Evaluation.py 스크립트로 Evaluation 진행



## Steps to reproduce 2(Evaluation using our project's Fine-tuned model)

1. 해당 프로젝트에서 Fine-tune 해둔 (a) **<u>Output Model</u>**과 (b) **<u>API Key</u>**를 사용 -> https://github.com/jjeongxu/VuLLy-eM/blob/main/Evaluation/Evaluation.py 스크립트 실행하여 Evaluation 진행
