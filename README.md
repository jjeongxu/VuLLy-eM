### "VuLLy-eM: Bully Vulnerabilities using LLMs"

A team project for the AI Programming course at Gachon University, Semester 1 2025



```
CleanVul and PatchDB were used as the train dataset. However, PatchDB cannot be made public due to licensing issues, so it is not uploaded to this project's GitHub.
```



## Steps to reproduce 1(Fine-tuning by yourself)

- Evaluation.py(https://github.com/jjeongxu/VuLLy-eM/blob/main/Evaluation/Evaluation.py)와 테스트셋(https://github.com/jjeongxu/VuLLy-eM/blob/main/Evaluation/converted_test_dataset.jsonl)을 Colab(https://colab.google/) 환경에서 구동하여 평가를 진행했습니다.



1. https://platform.openai.com/settings/organization/billing/overview 에 접속하여 **"Add payment details"** 클릭

   -> **Add Payment Details**에서 결제 정보 입력

   -> **Initial credit purchase** 에 $20, 나머지는 설정값 크게 상관 없음 (이후 창에서는 Continue 하면 다시 결제 될 것 같아 Continue를 눌러보지 못했습니다. 이러한 방식으로 결제 하셔서 금액 충전하시면 됩니다)

   ![image-20250607210118317](https://github.com/user-attachments/assets/3d982f39-e41f-4040-90f3-09b8630c9167)


![image-20250607210419006](https://github.com/user-attachments/assets/22ad5470-21a4-47eb-a1be-31b0b4ad9521)


![image-20250607210339711](https://github.com/user-attachments/assets/012bfb47-2505-46b6-853a-7fbc52adb13f)


2. https://platform.openai.com/finetune 에 접속하여 좌측 "DASHBOARD에서 API KEYS 선택"![image-20250607204018683](https://github.com/user-attachments/assets/1288eb24-6b35-4768-8606-c96c7e7525c5)


3. 우측 상단 **"Create new secret key"** 선택 후,  **Name**에 이름 입력, 나머지는 기본 설정으로 두고 **"Create secret key"** 클릭(API secret key는 발급 받은 이후 다시 확인 불가능하므로 따로 메모해두기)

![image-20250607204119949](https://github.com/user-attachments/assets/0968fe73-5cb5-447f-9768-15b29ec16212)


![image-20250607204135259](https://github.com/user-attachments/assets/291dd590-91fc-4cdf-aba9-c1749272c135)


4. 좌측 **"DASHBOARD"**에서 **"Fine-tuning"** 선택. 우측 상단 **"+ Create 클릭"**

![image-20250607204448223](https://github.com/user-attachments/assets/7ecdab13-4cef-4639-b356-b8874b2a3f93)




5. **Method** -> Supervised

​	**Base Model** -> gpt-3.5-turbo-0125

​	**Suffix** -> 원하는 모델 이름

​	**Seed** -> 1337

​	**Training data** -> Upload new 선택 후 https://github.com/jjeongxu/VuLLy-eM/blob/main/Train_Datasets/file-train_merged.jsonl 사용

​	**Validation data** -> Upload new 선택 후 https://github.com/jjeongxu/VuLLy-eM/blob/main/Train_Datasets/file-validation_merged.jsonl 사용

​	**나머지는 모두 Auto**

​	우측 아래 **"Create"** 클릭

![image-20250607204813062](https://github.com/user-attachments/assets/1c7a885d-149a-42f5-899a-4ea0d22489bb)


![image-20250607204833578](https://github.com/user-attachments/assets/3df4d9b6-d49c-4b8c-89e5-363286163355)


5. Fine-tuning이 완료되면 테스트셋(https://github.com/jjeongxu/VuLLy-eM/blob/main/Evaluation/converted_test_dataset.jsonl) 저장

6. Evaluation.py(https://github.com/jjeongxu/VuLLy-eM/blob/main/Evaluation/Evaluation.py)의  Line 9의 **"API-Key"**에 

   ```
   client = OpenAI(api_key="API-Key")
   ```

   에 Step2에서 할당받은 API Key 입력

   

   Evaluation.py의 Line 19와 Line 20에서

   ```
   DATA_PATH   = Path("converted_test_dataset.jsonl")               # Test set path
   FT_MODEL    = "Fine-tuned Model ID"                              # Fine-tuned Model ID
   ```

   **DATA_PATH**에 Step5에서 다운로드 받은 테스트셋 경로 입력

   **FT_MODEL**에 Fine-tune된 **Output model**(아래 사진 참고) 복사해서 입력

   

   ![image-20250607205319104](https://github.com/user-attachments/assets/bd9876da-0961-4182-9818-724fd584a920)


​	7. 이후 Evaluation.py 스크립트 실행하여 평가 진행



## Steps to reproduce 2(Evaluation using our project's Fine-tuned model)

**API key**와 **Model ID**는 사이버 캠퍼스 통해서 **김정수 **연락처로 연락 주시면 전송 드리겠습니다.



Evaluation.py(https://github.com/jjeongxu/VuLLy-eM/blob/main/Evaluation/Evaluation.py)의  Line 9의 **"API-Key"**에 

```
client = OpenAI(api_key="API-Key")
```

에 API Key 입력



Evaluation.py의 Line 19와 Line 20에서

```
DATA_PATH   = Path("converted_test_dataset.jsonl")               # Test set path
FT_MODEL    = "Fine-tuned Model ID"                              # Fine-tuned Model ID
```

**DATA_PATH**에 테스트셋(https://github.com/jjeongxu/VuLLy-eM/blob/main/Evaluation/converted_test_dataset.jsonl) 다운로드 후 경로 입력

**FT_MODEL**에 Fine-tune된 **Output model ID** 입력



이후, Evaluation.py 스크립트 실행하여 평가 진행
