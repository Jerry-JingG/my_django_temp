import pytesseract
from PIL import Image
import re
import cv2
import numpy as np
import os
import requests

class recog_bill():
    def __init__(self,image):
        self.image=np.array(image)

    def crop_relative(self,image, top_ratio, bottom_ratio, left_ratio, right_ratio):
        """
        根据比例裁剪图像区域
        :param image: OpenCV格式图像
        :param top_ratio: 上边界的比例（0到1之间）
        :param bottom_ratio: 下边界的比例（0到1之间）
        :param left_ratio: 左边界的比例（0到1之间）
        :param right_ratio: 右边界的比例（0到1之间）
        :return: 裁剪后的图像区域
        """
        height, width = image.shape[:2]
        top = int(height * top_ratio)
        bottom = int(height * bottom_ratio)
        left = int(width * left_ratio)
        right = int(width * right_ratio)
        
        return image[top:bottom, left:right]


    def is_night_mode(self,image):
        """
        判断图像是否处于黑夜模式
        :param image: 输入的彩色图像（BGR格式）
        :return: True 表示黑夜模式, False 表示正常模式
        """
        # 将图像转换为灰度图像
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 计算平均亮度
        mean_brightness = np.mean(gray_image)
        
        # 设置亮度阈值 (根据实际情况调整)
        brightness_threshold = 100
        
        # 统计主要颜色分布（这里简单地判断白色像素的比例）
        light_pixels_ratio = np.sum(gray_image > 200) / gray_image.size
        
        # 设置白色像素比例的阈值 (根据实际情况调整)
        light_pixels_threshold = 0.5
        
        # 判断是否为黑夜模式
        if mean_brightness < brightness_threshold and light_pixels_ratio < light_pixels_threshold:
            return True  # 黑夜模式
        else:
            return False  # 正常模式



    def recognize(self,image,top,bot,left,right,config='',lang=None):
        # print(image)

        if self.is_night_mode(image):
        #黑夜模式
            gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            cropped_image=cv2.bitwise_not(gray)
            cropped_image=self.crop_relative(cropped_image,top,bot,left,right)
        else:
            #正常模式
            image_cv = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cropped_image=self.crop_relative(image_cv,top,bot,left,right)


        # _, cropped_image = cv2.threshold(cropped_image, 150, 255, cv2.THRESH_BINARY_INV)
        marked_image_path="wxcloudrun/cropped_image.png"
        cv2.imwrite(marked_image_path,cropped_image)
        text = pytesseract.image_to_string(cropped_image, config=config,lang=lang)
        if lang=='chi_sim':
            cleaned_text=re.sub(r'\s', '', text)
            cleaned_text=re.sub(r'“', '', cleaned_text)
            return cleaned_text
        return text

    def extract_info(self,text, keyword, pattern=None):
        lines = text.splitlines()
        for line in lines:
            if keyword in line:
                
                if pattern:
                    match = re.search(pattern, line)
                    if match:
                        return match.group().strip()
                else:
                    return line.replace(keyword, '').strip()
        return None


    # 提取关键词之间的文本
    def extract_between_keywords(self,text, start_keyword, end_keyword=None):
        if end_keyword:
            pattern = re.compile(r'{}(.*?){}'.format(re.escape(start_keyword), re.escape(end_keyword)), re.S)
        else:
            pattern = re.compile(r'{}(.*)'.format(re.escape(start_keyword)),re.S)
        matches = pattern.findall(text)
        return [match.strip() for match in matches]


    def distill_from_bill(self):
        number_config = r'-c tessedit_char_whitelist=0123456789-. --psm 6'
        detail_config=r'--oem 2 --psm 6'
        chinese='chi_sim'
        text_amount=self.recognize(self.image,0.23,0.35,0.1,0.9,config=number_config)
        pay_to=self.recognize(self.image,0.2,0.25,0.1,0.9,lang=chinese)
        message=self.recognize(self.image,0.3,0.65,0.0,1.0,lang=chinese,config=detail_config)

        # print(message)

        #提取并且处理信息
        recipient = self.extract_info(pay_to, "扫二维码付款-给")
        amount_pattern = r'-\d+\.?\d*'
        amount = self.extract_info(text_amount, "-", amount_pattern)
        if amount and amount.startswith('-'):
            amount=amount[1:]
        status = self.extract_between_keywords(message, "当前状态", "收款方备注")
        remark = self.extract_between_keywords(message, "收款方备注", "付款方留言")
        note = self.extract_between_keywords(message, "付款方留言", "支付方式")
        payment_method = self.extract_between_keywords(message, "支付方式", "转账时间")
        transfer_time = self.extract_between_keywords(message, "转账时间", "转账单号")
        bill_id=self.extract_between_keywords(message,"转账单号")

        message_dict={
            "status":status,
            "remark":remark,
            "id":note,
            "method":payment_method,
            "time":transfer_time,
            "bill":bill_id
        }
        


        # 输出提取的信息
        print("\n提取出的信息如下：")
        print(f"给谁付款: {recipient}")
        print(f"付款金额: {amount}")
        print(f"当前状态: {status[0] if status else '未找到'}")
        print(f"收款方备注: {remark[0] if remark else '未找到'}")
        print(f"付款方留言: {note[0] if note else '未找到'}")
        print(f"支付方式: {payment_method[0] if payment_method else '未找到'}")
        print(f"转账时间: {transfer_time[0] if transfer_time else '未找到'}")
        print(f"转账单号: {bill_id[0] if bill_id else '未找到'}")
        return message_dict


# 打开图片并进行预处理
image_path = "wxcloudrun/image.jpg"
image = Image.open(image_path)
img_response = requests.get("https://7072-prod-7gh8xx1o7d00c9a2-1328894167.tcb.qcloud.la/image/WechatIMG302.jpg")
img_response.raise_for_status()


# 6. 将图片数据转换为 NumPy 数组
image_np = np.frombuffer(img_response.content, np.uint8)
image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
bill=recog_bill(image)
bill.distill_from_bill()
