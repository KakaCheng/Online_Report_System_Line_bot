from google.cloud import storage
from keras.models import load_model
from linebot.models import RichMenu, TextSendMessage, ImageSendMessage, StickerSendMessage, QuickReply, QuickReplyButton, CameraAction, CameraRollAction, LocationAction
from models.face_recognition import recognize
from error_map import *
import joblib
import json
import os

class global_controller():
    manage_image_flag = False #是否允許處理使用者回傳的圖片
    manage_location_flag = False #是否允許處理使用者回傳的圖片
global_controller_var = global_controller()

class image_service():

    @classmethod
    def line_user_upload_image(cls, line_bot_api, event, reply_msg_arr = [], marked_image = []) -> int:

        #Kaka: 初始化
        reply_msg = ""
        marked_image_path = ""
        bucket_name = "line-face-model-db"        
        #Kaka: 下載圖檔
        image_blob = line_bot_api.get_message_content(event.message.id)
        temp_file_path = f"{event.message.id}.png"

        with open(temp_file_path, 'wb') as fd:
            for chunk in image_blob.iter_content():
                fd.write(chunk)
        
        #Kaka: 上傳至Cloud Storage
        cls.update_img_to_storage(temp_file_path, bucket_name, "ori_img/")

        #Kaka: 人臉辨識
        ret, classification_res_arr, marked_image = recognize(temp_file_path)

        #Kaka: 刪除圖檔
        try:
            os.remove(temp_file_path)
        except:
            print(f"[Error][image_service][line_user_upload_image]: remove {temp_file_path} fail")
            return image_service_err.DEL_FILE_FAIL, marked_image_path

        if ret == face_recognition_err.NO_FACE_INFO:
            reply_msg_arr.append(TextSendMessage(text = "該圖片可能未包含人臉資訊"))
        elif ret == face_recognition_err.LOW_CONFIDENCE:
            reply_msg_arr.append(TextSendMessage(text = "該人未在通緝名單內"))
        else:
            index_str = ""
            marked_image_path = f"{event.message.id}_modify.png"
            for i in classification_res_arr:
                if i[0] == face_recognition_err.SUCCESS:
                    index_str += (i[1] + "\n")

            reply_msg_arr.append(TextSendMessage(text = "成功辨識:\n" + str(index_str)))
            
            #Kaka: 存標註後的圖檔
            try:
                marked_image.save(marked_image_path)
            except:
                print(f"[Error][image_service][line_user_upload_image]: save {marked_image_path} fail")
                os.remove(temp_file_path)
                return image_service_err.SAVE_FILE_FAIL, marked_image_path

            #Kaka: 上傳至Cloud Storage         
            cls.update_img_to_storage(marked_image_path, bucket_name, "modify_img/")

            #Kaka: 更新reply_msg_arr
            url = f"https://storage.googleapis.com/{bucket_name}/modify_img/" +  marked_image_path 
            reply_msg_arr.append(ImageSendMessage(original_content_url = url, preview_image_url = url))

            #Kaka: 刪除圖檔
            try:
                os.remove(marked_image_path)
            except:
                print(f"[Error][image_service][line_user_upload_image]: remove {marked_image_path} fail")
                os.remove(temp_file_path)
                return image_service_err.DEL_FILE_FAIL, marked_image_path

        return image_service_err.SUCCESS, marked_image_path

    @classmethod
    def update_img_to_storage(cls, img_name, bucket_name, blob_path):
        
        # 建立跟cloud storage 溝通的客戶端
        storage_client = storage.Client()

        # 正式上傳檔案至bucket內
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path + img_name)
        blob.upload_from_filename(img_name)

        return image_service_err.SUCCESS        

class rich_menu_service():

    @classmethod
    def show_menu(cls, line_bot_api, event) -> int:
        #Kaka: 初始化
        filename = "service/icon/rich_menu_001"

        #Kaka: 開啟圖檔
        try:
            img = open(filename + ".jpg", "rb")
        except:
            print(f"[Error][rich_menu_service][show_menu]: open {filename}.png fail")
            return rich_menu_service_err.OPEN_FILE_FAIL
        
        #Kaka: 開啟json檔
        try:
            with open(filename + ".json", "r", encoding = "utf-8") as f:
                menu_info_json = json.load(f)
        except:
            print(f"[Error][rich_menu_service][show_menu]: open {filename}.json fail")
            return rich_menu_service_err.OPEN_FILE_FAIL

        #Kaka: 產生rich menu
        try:
            rich_menu_id = line_bot_api.create_rich_menu(rich_menu = RichMenu.new_from_json_dict(menu_info_json))
            img_menu_link = line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg", img)
            user_menu = line_bot_api.link_rich_menu_to_user(event.source.user_id, rich_menu_id)
        except:
            print(f"[Error][rich_menu_service][show_menu]: create rich menu fail")
            return rich_menu_service_err.CREATE_RICH_MENU_FAIL

        return rich_menu_service_err.SUCCESS

class message_reply_service():

    #Kaka: 字串回應特殊字元
    robot_reply_text = "::@"

    #Kaka: 產生quick reply menu
    camera_quick_reply_button = QuickReplyButton(action = CameraAction(label = "使用相機拍照"))
    camera_roll_quick_reply_button = QuickReplyButton(action = CameraRollAction(label = "使用相簿照片"))
    location_quick_reply_button = QuickReplyButton(action = LocationAction(label = "定位資訊上傳"))

    qicuk_reply_text_tuple = (
        TextSendMessage(text = "第一步，請將照片上傳", quick_reply = QuickReply(items = [camera_quick_reply_button, camera_roll_quick_reply_button])),
        TextSendMessage(text = "第二步，請將定位資訊上傳", quick_reply = QuickReply(items = [location_quick_reply_button]))
    )
    
    quick_reply_dict = {
        robot_reply_text + "我要通報": qicuk_reply_text_tuple[0],
    }

    #Kaka 載入貼圖資訊
    try:
        with open("service/sticker_info.json", "r") as f:
            sticker_info_json = json.load(f)
    except:
        print(f"[Error][message_reply_service]: open sticker_info.json fail")
    
    @classmethod
    def text_reply(cls, line_bot_api, event, reply_msg_arr = None) -> int:

        if event.message.type == "text":
            user_msg = event.message.text
            if user_msg.find(cls.robot_reply_text) != -1:
                val = cls.quick_reply_dict.get(user_msg)
                if val != None:            
                    line_bot_api.reply_message(event.reply_token, val)
                    global_controller_var.manage_image_flag = True #下一步處理影片資訊
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "查無關鍵字QQ"))

        elif event.message.type == "image":
            if reply_msg_arr[0].text.find("成功辨識:") != -1:
                reply_msg_arr.append(cls.qicuk_reply_text_tuple[1])
                global_controller_var.manage_location_flag = True #下一步處理定位資訊
            line_bot_api.reply_message(event.reply_token, reply_msg_arr)

        elif event.message.type == "location":
            sticker = StickerSendMessage(                
                package_id = cls.sticker_info_json["0"]["packageId"], 
                sticker_id = cls.sticker_info_json["0"]["stickerId"])
            line_bot_api.reply_message(event.reply_token, sticker)

        return message_reply_service_err.SUCCESS
