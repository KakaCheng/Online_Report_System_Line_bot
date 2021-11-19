#本函式參考出處: https://medium.com/%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92%E7%9F%A5%E8%AD%98%E6%AD%B7%E7%A8%8B/google-facenet%E4%BA%BA%E8%87%89%E8%BE%A8%E8%AD%98%E7%B3%BB%E7%B5%B1%E5%AF%A6%E4%BD%9C-with-google-colab-3b973acf9479

from os import listdir
from os.path import isdir
from PIL import Image
from numpy import savez_compressed, asarray, load, expand_dims, array
from mtcnn.mtcnn import MTCNN
from sklearn.preprocessing import LabelEncoder, Normalizer
from sklearn.svm import SVC
from keras.models import load_model
from error_map import face_recognition_err
import joblib
import json
import cv2

#Kaka: 載入model
my_model = joblib.load("models/trainingModel.pkl")
facenet_model  =  load_model("models/facenet_keras.h5", compile=False)
with open("models/labels.json", "r", encoding = "utf-8") as f:
  labels_dict = json.load(f)

# extract_face(filename: 檔名,  required_size: 2D, 縮放大小)
# 功能: 擷取人臉影像
def extract_face(filename,  required_size=(160,  160)):

    #初始化
    face_array = []
    pos_arr = [] #[x1, y1, x2, y2]
    
    #Kaka: 載入圖檔
    image  =  Image.open(filename)
    #Kaka: 轉換成RGB格式
    image  =  image.convert('RGB')
    #Kaka: 轉換成Array
    pixels  =  asarray(image)
    #Kaka: 轉換為偵測子
    detector  =  MTCNN()
    #Kaka: 抓出人臉物件
    results  =  detector.detect_faces(pixels)
    if len(results) == 0:
        return [], []
    # #Kaka: 回傳位置，只抓第一個人臉物件
    # x1,  y1,  width,  height  = results[0]['box']
    # x1,  y1  =  abs(x1),  abs(y1)
    # x2,  y2  =  x1  +  width,  y1  +  height
    # #Kaka: 擷取人臉影像
    # face  =  pixels[y1:y2,  x1:x2]
    # #Kaka: 縮放人臉大小
    # image  =  Image.fromarray(face)
    # image  =  image.resize(required_size)

    # face_array  =  asarray(image)

    #Kaka: 回傳位置，抓出所有可被辨識的人臉物件
    for i in results:
        x1,  y1,  width,  height  = i['box']
        x1,  y1  =  abs(x1),  abs(y1)
        x2,  y2  =  x1  +  width,  y1  +  height
        #Kaka: 擷取人臉影像
        face  =  pixels[y1:y2,  x1:x2]
        #Kaka: 縮放人臉大小
        image  =  Image.fromarray(face)
        image  =  image.resize(required_size)

        #記錄人臉
        face_array.append(asarray(image))
        #記錄位置
        pos_arr.append([x1, y1, x2, y2])

    return  face_array, pos_arr

# load_faces10(directory: 資料夾路徑)
# 功能: 批量載入影像
def load_faces10(directory):
    #Kaka: 初始化
    except_file = list()
    files = list()
    faces  =  list()

    for  filename in  listdir(directory):
        path  =  directory  +  filename
        print(path)
        filename = filename[:-4]
        try:
            #取出人臉影像
            face, pos_arr =  extract_face(path)
            #Kaka: 將截圖的臉放到集合裡
            if len(face) == 0:
                faces.append(face)
                #Kaka: 將檔名放到集合裡
                files.append(filename)
        except(IndexError,IsADirectoryError,OSError):
            #Kaka: 將讀取有問題的資料夾放到集合裡
            except_file.append(filename)
            pass

    #Kaka: 回傳臉集合、檔名集合、有問題的檔案集合
    return  faces, files, except_file

# load_dataset10(directory: 資料夾路徑)
# 功能: 批量載入資料夾
def load_dataset10(directory):
    X,  y  =  list(),  list()
    #Kaka: 初始化
    list_file = []
    list_except_file = []

    for  subdir in  listdir(directory):
        #Kaka: 抓出資料夾
        path  =  directory  +  subdir  +  '/'
        if  not  isdir(path):
            continue

        #Kaka: 抓出人臉列表
        faces, files, list_except_file =  load_faces10(path)
        list_file.append(files)
        #Kaka: 建立特徵
        labels  =  [subdir for  _  in  range(len(faces))]

        print('>loaded %d examples for class: %s'  %  (len(faces),  subdir))
        X.extend(faces)
        y.extend(labels)
    
    #Kaka: 回傳 臉(array), 標籤人名(aray), 所有資料夾(list), 有問題的資料夾(list)
    return  asarray(X),  asarray(y), list_file, list_except_file

# get_embedding(model: 模型,  face_pixels: 人臉影像)
# 功能: 人臉嵌入
def get_embedding(model,  face_pixels):
    # scale pixel values
    face_pixels  =  face_pixels.astype('float32')
    # standardize pixel values across channels (global)
    mean,  std  =  face_pixels.mean(),  face_pixels.std()
    face_pixels  =  (face_pixels  -  mean)  /  std
    # transform face into one sample
    samples  =  expand_dims(face_pixels,  axis=0)
    # make prediction to get embedding
    yhat  =  model.predict(samples)

    return  yhat[0]

# recognize(img_path: 影像路徑)
# 功能: 人臉辨認
def recognize(img_path):

    #初始化
    classification_res_arr = []    
    class_index_arr = []
    class_probability_arr = []
    is_LOW_CONFIDENCE = True

    #Kaka: 載入圖檔
    marked_image = array(Image.open(img_path))

    #Kaka: 擷取人臉
    face, pos_arr = extract_face(img_path)
    if len(face) == 0:
        return face_recognition_err.NO_FACE_INFO, [], marked_image

    for i in range(len(face)):

        #Kaka: 人臉嵌入
        embedding  =  get_embedding(facenet_model,  face[i])

        samples = expand_dims(embedding,  axis = 0)

        #Kaka: 模型預測
        yhat_class = my_model.predict(samples)
        yhat_prob = my_model.predict_proba(samples)

        #Kaka: 取得預測結果
        class_index  =  labels_dict[str(yhat_class[0])] #人名
        class_probability  =  yhat_prob[0, yhat_class[0]]  *  100 #預測值

        if class_probability <= 0.03:
            is_LOW_CONFIDENCE &= False
            classification_res_arr.append([face_recognition_err.SUCCESS, class_index, class_probability])
            cv2.rectangle(marked_image, pos_arr[i][0:2], pos_arr[i][2:], [255, 0, 0], 3)            
        else:
            classification_res_arr.append([face_recognition_err.LOW_CONFIDENCE, class_index, class_probability])
            cv2.rectangle(marked_image, pos_arr[i][0:2], pos_arr[i][2:], [0, 255, 0], 3)
            
    if is_LOW_CONFIDENCE:
        return face_recognition_err.LOW_CONFIDENCE, classification_res_arr, Image.fromarray(marked_image)
    
    return face_recognition_err.SUCCESS, classification_res_arr, Image.fromarray(marked_image)