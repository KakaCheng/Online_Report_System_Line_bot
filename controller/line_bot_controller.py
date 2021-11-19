from error_map import *
from linebot import LineBotApi, WebhookHandler
from service.service import *

class line_bot_event_controller():

    @classmethod
    def handle_image_message(cls, line_bot_api, event) -> int:
        ret = line_bot_event_controller_err.SUCCESS
        reply_msg_arr = []

        if not global_controller_var.manage_image_flag:
            print(f"[Error][handle_image_message][handle_image_message]: global_controller_var.manage_image_flag is false")
            return line_bot_event_controller_err.FLOW_FAIL
        
        ret, ret_img_path = image_service.line_user_upload_image(line_bot_api, event, reply_msg_arr)
        if ret == image_service_err.SUCCESS:
            global_controller_var.manage_image_flag = False
            message_reply_service.text_reply(line_bot_api, event, reply_msg_arr)

        return line_bot_event_controller_err.SUCCESS
    
    @classmethod
    def handle_rich_menu(cls, line_bot_api, event) -> int:
        ret = line_bot_event_controller_err.SUCCESS

        ret = rich_menu_service.show_menu(line_bot_api, event)
        if not rich_menu_service_err.SUCCESS:
            return line_bot_event_controller_err.SERVICE_FAIL

        return line_bot_event_controller_err.SUCCESS

    @classmethod
    def handle_message_reply(cls, line_bot_api, event) -> int:
        ret = line_bot_event_controller_err.SUCCESS

        ret = message_reply_service.text_reply(line_bot_api, event)
        if ret != message_reply_service_err.SUCCESS:
            return line_bot_event_controller_err.SERVICE_FAIL

        return line_bot_event_controller_err.SUCCESS
    
    @classmethod
    def handle_location_message_reply(cls, line_bot_api, event) -> int:
        ret = line_bot_event_controller_err.SUCCESS

        ret = message_reply_service.text_reply(line_bot_api, event)
        if ret != message_reply_service_err.SUCCESS:
            return line_bot_event_controller_err.SERVICE_FAIL

        global_controller_var.manage_location_flag = False
        return line_bot_event_controller_err.SUCCESS