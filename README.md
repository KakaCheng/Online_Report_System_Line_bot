# Online_Report_System_Line_bot (通緝犯線上舉發系統)
## 學習目標 
1. 訓練AI人臉辨識模型
2. 將AI人臉辨識模型部署在GCP上
3. 透過line-bot-sdk與使用者互動

**本專案為檢視自我學習成效，無任何商業利益。**\
**對於人臉辨識所使用的資料，也只是作為測試使用，無其他用意，也因此不提供測資，僅說明訓練方式與參考出處**

## 開發目的
### 目前民間舉發流程概述 \[1]
- 如何查詢是否為通緝犯
1. 外逃/重要緊急通緝犯會公布照片與姓名
2. 進到官方警政系統，輸入姓名與身分證字號方可查詢
- 如何舉發
1. 書面備案
2. 電話描述

- 現有檢舉流程存在的可能缺陷
1. 不可能知道通緝犯個資\
&emsp;&emsp;- 改善方式: 使用**AI人臉辨識**，在民眾未知個資的情形下也可以查詢通緝犯
2. 舉發方式不方便又不親民\
&emsp;&emsp;- 改善方式: **LINE APP是廣泛使用的通訊軟體**，透過問答式流程來提供線索給警方

## 流程說明



## 實際開發
### 訓練模型
1. 按照\[2]取得**facenet_keras.h5**並訓練模型
3. 將訓練好的模型檔命名為**trainingModel.pkl**
4. 將訓練過程所使用到資料標籤檔命名為**labels.json**
5. 將**facenet_keras.h5**、**trainingModel.pkl**與**labels.json**放置於\models下

### 部署於GCP上
1. 將整包專案複製於GCP雲端上
2. 於Cloud Shell輸入安裝指令
```
pip3 install -r requirements.txt
```
3. 進行Cloud Build
```
gcloud config set project YOUR-PROJECT-ID
gcloud builds submit  --tag gcr.io/$GOOGLE_CLOUD_PROJECT/online-report-system:1.0.0.0
```
4. 於Cloud Run下部署映像檔
5. 將生成的網址貼至Line Developer webhook

## 成果


## 參考資料
\[1]: 
https://laws010.com/blog/criminal-offense/circular-order/circular-order-01 \
\[2]:
https://medium.com/%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92%E7%9F%A5%E8%AD%98%E6%AD%B7%E7%A8%8B/google-facenet%E4%BA%BA%E8%87%89%E8%BE%A8%E8%AD%98%E7%B3%BB%E7%B5%B1%E5%AF%A6%E4%BD%9C-with-google-colab-3b973acf9479

