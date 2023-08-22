# 版权所有 (c) 2023 by kexw
#
# 特此免费授予任何获得此软件及其相关文档文件（“软件”）副本的人无限制的使用权，
# 包括但不限于使用、复制、修改、合并、发布、分发、再许可和/或销售软件的副本的权利，
# 并允许向其提供软件的人遵循以下条件：
#
# 本软件仅供学习和研究使用。在大规模使用或商业化前，请确保得到相关第三方平台或接口的正式授权。
# 任何因未经授权使用第三方接口或平台而导致的法律纠纷或损害，用户需自行承担全部责任。


# 导入必要的库
from flask import Flask, request, jsonify, g
import pymysql
import random
import json
import time
import requests


# 需要修改的配置
 # 机器人的 UID
BOT_UID = 4
 #ai图片网站 
kexw_url = "https://rightbrain.art"
 #ai图片网站cookies
cookies_list = [
    "satoken=xxxxx; token=xxxxx",
    "satoken=xxxxx; token=xxxxx " ]
 #VoceChat地址
kexw_boturl = "http://127.0.0.1:3009"
 #VoceChat Bot的key
kexw_key = " Bot的key"
 #VoceChat 管理员的Token 
kexw_sudokey = "管理员的Token"
#mysql
kexw_host = "127.0.0.1"
kexw_user = "账号"
kexw_password = "数据库账号密码"
kexw_port = 3306  #数据库端口默认3306
kexw_database = "数据库账号"


# 设置默认的用户状态
USER_STATE = {}
DATABASE_INITIALIZED = False
# 设置默认的模型方向选择
MODEL_DIRECTION = {
    "1": {
        "model_id": "62a46462-fa74-441c-b141-640a16248av11",
        "neg_prompt": "worst quality,low quality,lowres,bad image,jpeg artifacts,bad anatomy,watermarks,blur,messy"
    },
    "2": {
        "model_id": "62a46462-fa74-441c-b141-640a16248av13",
        "neg_prompt": "worst quality,low quality,lowres,bad image,jpeg artifacts,bad anatomy,watermarks,blur,messy"
    },
    "3": {
        "model_id": "62a46462-fa74-441c-b141-640a16248av12",
        "neg_prompt": "worst quality,low quality,lowres,bad image,jpeg artifacts,bad anatomy,watermarks,blur,messy"
    },
    "4": {
        "model_id": "62a46462-fa74-441c-b141-640a16248a72",
        "neg_prompt": "worst quality,low quality,lowres,bad image,jpeg artifacts,bad anatomy,watermarks,blur,messy"
    },
    "5": {
        "model_id": "62a46462-fa74-441c-b141-640a16248a71",
        "neg_prompt": "worst quality,low quality,lowres,bad image,jpeg artifacts,bad anatomy,watermarks,blur,messy"
    },
    "6": {
        "model_id": "62a46462-fa74-441c-b141-640a16248a09",
        "neg_prompt": "(worst quality:2), (low quality:2), (normal quality:2), lowres, paintings, sketches, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot"
    }
}


model_id_to_name = {
    "62a46462-fa74-441c-b141-640a16248av11": "人像",
    "62a46462-fa74-441c-b141-640a16248av13": "二次元",
    "62a46462-fa74-441c-b141-640a16248av12": "设计",
    "62a46462-fa74-441c-b141-640a16248a72": "虚拟建模",
    "62a46462-fa74-441c-b141-640a16248a71": "3D二次元",
    "62a46462-fa74-441c-b141-640a16248a09": "写真",
    # 其他模型ID和名称...
}
# 设置默认的采集器选项
SAMPLER_OPTIONS = {
    "1": "DPM++ SDE Karras",
    "2": "DPM++ 2S a",
    "3": "Euler a",
    "4": "DDIM"
}
headers = {
    'Content-Type': 'text/markdown',
    'accept': 'application/json;charset=utf-8',
    'x-api-key': kexw_key
}
# 设置默认的图像比例
IMAGE_RATIO = {
    "1": {"imageRatio": "3:4", "width": 602, "height": 770},
    "2": {"imageRatio": "1:1", "width": 680, "height": 680},
    "3": {"imageRatio": "2:3", "width": 514, "height": 770},
    "4": {"imageRatio": "9:16", "width": 512, "height": 912},
    "5": {"imageRatio": "4:3", "width": 770, "height": 602},
    "6": {"imageRatio": "3:2", "width": 770, "height": 514},
    "7": {"imageRatio": "16:9", "width": 912, "height": 512}
}
app = Flask(__name__)

def get_db():
    # """
    # mysql数据库连接
    # """
    if 'db' not in g:
        g.db = pymysql.connect(
            host=kexw_host,
            user=kexw_user,
            password=kexw_password,
            port=kexw_port,
            database=kexw_database
        )
    return g.db


@app.teardown_appcontext
def close_db(error):
    # 请求结束时再次关闭数据库。
    if 'db' in g:
        g.db.close()


def send_message_to_user(uid, message):
    requests.post(f"{kexw_boturl}/api/bot/send_to_user/{uid}",
                  data=message.encode('utf-8'), headers=headers)


def create_table():
    """创建数据库表格。"""
    db = get_db()
    cursor = db.cursor()

    # 检查 kexw_botimg 表是否已经存在
    cursor.execute("SHOW TABLES LIKE 'kexw_botimg'")
    result = cursor.fetchone()

    # 如果 kexw_botimg 表不存在，创建它
    if not result:
        cursor.execute("""
        CREATE TABLE `kexw_botimg` (
            `uid` int(11) NOT NULL,
            `model_id` varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
            `prompt` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
            `neg_prompt` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
            `imageRatio` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
            `sampler` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
            `loraid` int(11) NULL DEFAULT NULL,
            `lora_keyword` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
            `height` double NULL DEFAULT NULL,
            `width` double NULL DEFAULT NULL,
            PRIMARY KEY (`uid`) USING BTREE
        ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;
        """)
        db.commit()


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    return "Hello, this is a GET request!"
    try:
        create_table()  # 创建数据库表格
        data = request.get_json()
        from_uid = data['from_uid']
        print('收到的信息：')
        print(data)

        from_uid = data['from_uid']
        print('发送者 UID：')
        print(from_uid)

        bot_mid = data['mid']
        # 打印 bot_mid 变量，验证是否成功保存
        print("bot_mid2:", bot_mid)

        # 如果消息发送者是机器人本身，什么都不做。
        if from_uid == BOT_UID:
            return jsonify(status='success'), 200

        webtext = data['detail']['content']
        handle_user_message(from_uid, webtext)

    except Exception as e:
        print(f"Error occurred: {e}")
        # 为新用户插入记录
        db = get_db()
        cursor = db.cursor()
        # 查询数据库
        cursor.execute("INSERT INTO `kexw_botimg` (`uid`) VALUES (%s)", (from_uid,))
        db.commit()

        webtext = data['detail']['content']
        handle_user_message(from_uid, webtext)
    return jsonify(status='success'), 200


def handle_user_message(from_uid, webtext):
    db = get_db()
    cursor = db.cursor()
    # 查询数据库

    cursor.execute('SELECT height FROM kexw_botimg WHERE uid = %s', (from_uid,))

    row = cursor.fetchone()[0]
    print("Fetched row:", row)

    # 判断用户当前的状态
    headers = {
        'Content-Type': 'text/markdown',
        'accept': 'application/json;charset=utf-8',
        'x-api-key': kexw_key
    }
    # 检查用户是否想要修改模型方向
    if webtext.lower() == "修改模型方向":
        USER_STATE[from_uid] = 'selecting_model_direction'
        bot_message = '请选择新的模型生成方向 \t \n\n 1.人像       \n      2.二次元  \n 3.设计       \n     4.虚拟建模  \n 5.3D二次元  \n  6.写真'
        send_message_to_user(from_uid, bot_message)
        return

        # 检查用户是否想要查看默认参数

    # 检查用户是否想要修改采集器选项
    if webtext.lower() == "修改采集器选项":
        USER_STATE[from_uid] = 'selecting_sampler_options'
        bot_message = '请选择新的采集器选项\t \n\n  1. DPM++ SDE Karras   \n   2. DPM++ 2S a   \n  3. Euler a   \n  4. DDIM'
        send_message_to_user(from_uid, bot_message)
        return

    # 检查用户是否想要修改图像比例
    if webtext.lower() == "修改图片比例":
        USER_STATE[from_uid] = 'selecting_image_ratio'
        bot_message = '请选择新的图像比例\t \n\n 1. 长图 [3:4]   2. 方图 [1:1]  \n 3. 长图 [2:3]   4. 长图 [9:16] \n  5. 宽图 [4:3]   6. 宽图 [3:2] \n  7. 宽图 [16:9]'
        send_message_to_user(from_uid, bot_message)
        return
    if webtext.lower() == "默认参数":
        cursor.execute('SELECT height, model_id, sampler, imageRatio, width, neg_prompt FROM kexw_botimg WHERE uid = %s',
                       (from_uid,))
        row = cursor.fetchone()
        if row:
            height, model_id, sampler, image_ratio, width, neg_prompt = row
            model_direction_name = model_id_to_name.get(model_id, "未知模型")

            bot_message = f"用户 {from_uid} 的默认参数：\n\n"
            bot_message += f"模型方向：{model_direction_name}\n"
            bot_message += f"采集器选项：{sampler}\n"
            bot_message += f"图像比例：{image_ratio}\n"
            bot_message += f"图片宽度：{width}\n"
            bot_message += f"图片高度：{height}\n"
            bot_message += f"反向描述词：{neg_prompt}\n"

            send_message_to_user(from_uid, bot_message)
        else:
            bot_message = "找不到该用户的默认参数。"
            send_message_to_user(from_uid, bot_message)

        return
    # 检查用户是否在选择选项过程中（12345）
    if USER_STATE.get(from_uid) in ['selecting_model_direction', 'selecting_sampler_options', 'selecting_image_ratio']:
        if webtext in ["1", "2", "3", "4", "5", "6"]:
            # 根据用户的选择更新数据库中的相应字段
            option = webtext
            if USER_STATE[from_uid] == 'selecting_model_direction':
                if option in MODEL_DIRECTION:
                    model_id = MODEL_DIRECTION[option]['model_id']
                    neg_prompt = MODEL_DIRECTION[option]['neg_prompt']
                    cursor.execute('UPDATE kexw_botimg SET model_id = %s, neg_prompt = %s WHERE uid = %s',
                                   (model_id, neg_prompt, from_uid))
                else:
                    bot_message = '输入无效，请选择1-6的数值'
                    send_message_to_user(from_uid, bot_message)
                    return
            elif USER_STATE[from_uid] == 'selecting_sampler_options':
                if option in SAMPLER_OPTIONS:
                    sampler = SAMPLER_OPTIONS[option]
                    cursor.execute('UPDATE kexw_botimg SET sampler = %s WHERE uid = %s', (sampler, from_uid))
                else:
                    bot_message = '输入无效，请选择1-5的数值'
                    send_message_to_user(from_uid, bot_message)
                    return
            elif USER_STATE[from_uid] == 'selecting_image_ratio':
                if option in IMAGE_RATIO:
                    imageRatio = IMAGE_RATIO[option]['imageRatio']
                    width = IMAGE_RATIO[option]['width']
                    height = IMAGE_RATIO[option]['height']
                    cursor.execute('UPDATE kexw_botimg SET imageRatio = %s, width = %s, height = %s WHERE uid = %s',
                                   (imageRatio, width, height, from_uid))
                else:
                    bot_message = '输入无效，请选择1-5的数值'
                    send_message_to_user(from_uid, bot_message)
                    return

            db.commit()
            USER_STATE[from_uid] = 'init'
            bot_message = '修改成功！'
            send_message_to_user(from_uid, bot_message)
            return

    if row is None:

        if from_uid not in USER_STATE or USER_STATE[from_uid] == 'init':
            USER_STATE[from_uid] = 'selecting_model_direction'
            bot_message = '请选择默认模型生成方向 \t \n\n 1.人像       \n      2.二次元  \n 3.设计       \n     4.虚拟建模  \n 5.3D二次元  \n  6.写真'
            requests.post(f"{kexw_boturl}/api/bot/send_to_user/" + str(from_uid),
                          data=bot_message.encode('utf-8'), headers=headers)
            return

        elif USER_STATE[from_uid] == 'selecting_model_direction':
            if webtext not in MODEL_DIRECTION:
                bot_message = '输入无效，请选择1-6的数值'
            else:
                # 保存模型方向到数据库
                model_id = MODEL_DIRECTION[webtext]['model_id']
                neg_prompt = MODEL_DIRECTION[webtext]['neg_prompt']
                cursor.execute('UPDATE kexw_botimg SET model_id = %s, neg_prompt = %s WHERE uid = %s',
                               (model_id, neg_prompt, from_uid))
                db.commit()
                USER_STATE[from_uid] = 'model_direction_selected'
                bot_message = '模型方向已选择，现在请选择采集器选项\t \n\n  1. DPM++ SDE Karras   \n   2. DPM++ 2S a   \n  3. Euler a   \n  4. DDIM'
                requests.post(f"{kexw_boturl}/api/bot/send_to_user/" + str(from_uid),
                              data=bot_message.encode('utf-8'), headers=headers)
            return

        elif USER_STATE[from_uid] == 'model_direction_selected':
            if webtext not in SAMPLER_OPTIONS:
                bot_message = '输入无效，请选择1-4的数值'
                requests.post(f"{kexw_boturl}/api/bot/send_to_user/" + str(from_uid),
                              data=bot_message.encode('utf-8'), headers=headers)
            else:
                # 保存采集器选项到数据库
                sampler = SAMPLER_OPTIONS[webtext]
                cursor.execute('UPDATE kexw_botimg SET sampler = %s WHERE uid = %s', (sampler, from_uid))
                db.commit()
                USER_STATE[from_uid] = 'sampler_selected'
                bot_message = '采集器选项已选择，现在请选择图像比例...请选择默认图像比例 \t \n\n 1. 长图 [3:4]   2. 方图 [1:1]  \n 3. 长图 [2:3]   4. 长图 [9:16] \n  5. 宽图 [4:3]   6. 宽图 [3:2] \n  7. 宽图 [16:9]'
                requests.post(f"{kexw_boturl}/api/bot/send_to_user/" + str(from_uid),
                              data=bot_message.encode('utf-8'), headers=headers)
            return

        elif USER_STATE[from_uid] == 'sampler_selected':
            if webtext not in IMAGE_RATIO:
                bot_message = '输入无效，请选择1-7的数值'
                requests.post(f"{kexw_boturl}/api/bot/send_to_user/" + str(from_uid),
                              data=bot_message.encode('utf-8'), headers=headers)
            else:
                # 保存图像比例到数据库
                imageRatio = IMAGE_RATIO[webtext]['imageRatio']
                width = IMAGE_RATIO[webtext]['width']
                height = IMAGE_RATIO[webtext]['height']
                cursor.execute('UPDATE kexw_botimg SET imageRatio = %s, width = %s, height = %s WHERE uid = %s',
                               (imageRatio, width, height, from_uid))
                db.commit()
                USER_STATE[from_uid] = 'init'
                bot_message = '# 已设置完成默认参数\n如需修改，请发送 : \n1. 修改模型方向\n1. 修改采集器选项\n1. 修改图片比例\n\n### 生成图片格式 \n#### `图片的关键词`|`负面关键词`|`输入文本强度。默认可以7上限15`|`输入步数默认可以20（生成图片的步数） `|`输入照片模式0.普通，1.高清`|`输入生成的张数，默认。如果照片模式是高清，这里只能输入2,如果是普通无上限`\n\n## 花里长着小猫的花朵，动物|正常的花朵|7|20|高清|2'
                requests.post(f"{kexw_boturl}/api/bot/send_to_user/" + str(from_uid),
                              data=bot_message.encode('utf-8'), headers=headers)
            return
    else:

        # 如果model_id不为空，直接请求生成图片
        parts = webtext.split('|')
        prompt = parts[0].strip()
        cfgScale = int(parts[2].strip())
        step_num = int(parts[3].strip())
        image_text = parts[4].strip().lower()
        if image_text == '高清':
            use_hd = 1
        elif image_text == '超清':
            use_hd = 2
        else:
            use_hd = 0
        image_num = int(parts[5].strip())
        neg_prompt = parts[1].strip() if len(parts) > 1 else ''

        # 查询数据库获取模型方向，采集器选项，图像比例等
        cursor.execute('SELECT model_id, sampler, imageRatio, width, height, neg_prompt FROM kexw_botimg WHERE uid = %s',
                       (from_uid,))
        roww = cursor.fetchone()
        model_id = roww[0]
        sampler = roww[1]
        imageRatio = roww[2]
        width = roww[3]
        height = roww[4]

        # 如果neg_prompt为空，那么从数据库中获取
        if not neg_prompt:
            neg_prompt = roww[5]


        # 根据模型ID获取模型名称
        model_direction_name = model_id_to_name.get(model_id, "未知模型")

        bot_message = f'**图片正在生成中请稍后....**\n \t \n 您的默认参数\n \t \n\n选择的模型：{model_direction_name}\t \n\n图片描述词: {prompt}\t \n\n反向描述词: {neg_prompt}\t \n\n 图片清晰度:{image_text} \t \n\n图像比例：  {imageRatio}\t \n\n 采样器：{sampler} \t \n\n输入步数:{step_num} \t \n\n输入张数:{image_num}'
        requests.post(f"{kexw_boturl}/api/bot/send_to_user/" + str(from_uid),
                      data=bot_message.encode('utf-8'), headers=headers)

        # POST 请求的数据
        # POST 请求的数据
        data = {
            "model": model_id,
            "relation": True,
            "imageRatio": imageRatio,
            "width": width,
            "height": height,
            "useHd": use_hd,
            "imageNum": image_num,
            "stepNum": step_num,
            "cfgScale": cfgScale,
            "sampler": sampler,
            "seed": -1,
            "negPrompt": neg_prompt,
            "loraId": "",
            "loraWeight": "",
            "loraKeyword": "",
            "prompt": prompt
        }

        cookie = random.choice(cookies_list)

        header = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.99 Safari/537.36",
            "Cookie": cookie
        }

        # 发送创建图片请求
        create_url = f"{kexw_url}/apis/text2image/create"
        response = requests.post(create_url, headers=header, data=json.dumps(data))

        # 解析响应并获取 'requestid'
        json_response = response.json()
        print(json_response)  # 打印响应内容
        if json_response.get('data'):
            requestid = json_response.get('data', {}).get('requestid')
        else:
            print("No 'data' in the response")
            return

        # 使用 'requestid' 发送获取图片请求，直到列表中有数据
        while True:
            get_image_url = f"{kexw_url}/apis/superImage/getImage?requestid={requestid}"
            response = requests.get(get_image_url, headers=header)
            json_response = response.json()
            print(json_response)

            # 提取 'list' 字段
            if json_response.get('data') and json_response.get('data', {}).get('list'):
                image_list = json_response.get('data', {}).get('list', [])
                if image_list:
                    break
            else:
                print("No 'data' in the response, retrying...")

            # 暂停五秒再进行下一次尝试
            time.sleep(5)

        # 提取所有图片的 URL
        image_urls = [url for url in image_list if url != "willBePreview"]

        # 按照你的描述生成标题和标签
        get_title = f"图片描述词: {prompt}"
        get_tags = f"选择的模型：{model_id_to_name.get(model_id)}"
        get_tags += f"\n反向描述词: {neg_prompt}\n图片清晰度: 高清\n图像比例：{imageRatio}\n采样器：{sampler}\n输入步数:{step_num}\n输入张数:{image_num}"

        # 构建并发送消息给用户，注意这里需要为每个图片 URL 构建一个图片链接
        bot_message = f"### {get_title}\n{get_tags}"
        heade = {
            'Content-Type': 'text/markdown',
            'accept': 'application/json;charset=utf-8',
            'x-api-key': kexw_key
        }
        for image_url in image_urls:
            bot_message += f"\n![]({image_url})"
        requests.post(f"{kexw_boturl}/api/bot/send_to_user/{from_uid}", data=bot_message.encode('utf-8'),
                      headers=heade)
        data = request.get_json()

        bot_mid = data['mid']
        bot_mid = bot_mid + 1
        # 打印 bot_mid 变量，验证是否成功保存
        print("bot_mid3:", bot_mid)
        # 构建 删除消息
        # 定义请求头
        head = {
            'accept': 'application/json; charset=utf-8',
            'X-API-Key':kexw_sudokey 
              }
        requests.delete(f"{kexw_boturl}/api/message/{bot_mid}", headers=head, data={})

        print(bot_message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5321, debug=True)
