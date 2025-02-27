'''
Author: laihuihang laihuihang@foxmail.com
Date: 2024-08-05 14:23:13
LastEditors: laihuihang laihuihang@foxmail.com
LastEditTime: 2024-08-07 10:22:46
FilePath: /morphingdb_test/muti_query/import_dataset.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
## conversation
## datatime user_id comment image

## user
## user_id passwd birthday location

import uuid
import random
import pandas as pd
import numpy as np
import psycopg2
import os
from datetime import datetime, timedelta
import evadb

db_config = {
    "dbname": "postgres",
    "host": "localhost",
    "port": "5432",
    "user": "postgres",
    "password": "123456"
}

# 连接数据库
conn = psycopg2.connect(**db_config)
cur = conn.cursor()



location_list = ['杭州', '宁波', '温州', '嘉兴','湖州','绍兴','金华','衢州','舟山','台州','丽水']

start_date = datetime(1960, 1, 1)
conversation_start_time = datetime(2024, 1, 1)
end_date = datetime.now()

pre_path_text = os.path.dirname(os.path.dirname(__file__)) + "/data/text/sst2"
df = pd.read_csv(pre_path_text+'/data/train.tsv', sep='\t')
pre_path_image = os.path.dirname(os.path.dirname(__file__))
image_name = os.listdir(pre_path_image + '/data/image/image-net/data/')

def generate_user():
    user_id = str(uuid.uuid4())
    pass_wd = "morphingdb"
    birthday = (start_date + timedelta(days=random.randint(0, (end_date - start_date).days))).strftime('%Y-%m-%d')
    location = random.choice(location_list)
    return user_id, pass_wd, birthday, location 

def generate_conservation(user_id):
    random_days = random.randint(0, (end_date - conversation_start_time).days)
    datetime_with_random_offset = (conversation_start_time + timedelta(days=random_days))
    datatime = datetime_with_random_offset.strftime('%Y-%m-%d %H:%M:%S')
    user_id = user_id
    image = random.choice(image_name)
    random_index = np.random.choice(df.index)
    random_sentence = df.loc[random_index, 'sentence']
    comment = random_sentence
    return datatime, user_id, image, comment

def format_layer(layer):
    return ', '.join(f"[{', '.join(map(str, row))}]" for row in layer)


def morphing_insert():
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    cur.execute("drop table if exists " + "user_table;")
    cur.execute("drop table if exists " + "conversation_vector;")
    cur.execute("drop table if exists " + "conversation_url;")
    cur.execute("create table if not exists " + "user_table" + " (user_id text PRIMARY KEY, passwd text, birthday text, location text);")
    cur.execute("create table if not exists " + "conversation_vector" + " (datatime text, user_id text PRIMARY KEY, comment mvec, image mvec);")
    cur.execute("create table if not exists " + "conversation_url" + " (datatime text, user_id text PRIMARY KEY, comment text, image text);")
    conn.commit()

    pre_path = os.path.dirname(os.path.dirname(__file__))

    for i in range(10000):
        res = generate_user()
        sql1 = f"INSERT INTO " + "user_table" + " (user_id, passwd, birthday, location) VALUES ('{}', '{}', '{}', '{}');".format(res[0], res[1], res[2], res[3])
        cur.execute(sql1)
        res = generate_conservation(res[0])
        sql2 = f"INSERT INTO " + "conversation_url" + " (datatime, user_id, comment, image) VALUES ('{}', '{}', '{}', '{}');".format(res[0], res[1], res[3].replace("'","''"), res[2])
        cur.execute(sql2)
        sql3 = f"INSERT INTO " + "conversation_vector" + " (datatime, user_id, comment, image) VALUES ('{}', '{}', {}, {});".format(res[0], res[1], "text_to_vector('{}','{}')".format(pre_path+"/models/spiece.model.old",res[3].replace("'","''")), "image_to_vector(224,224,0.4914,0.4822,0.4465,0.2023,0.1994,0.2010, '{}')".format(pre_path_image+"/data/image/image-net/data/"+res[2]))
        cur.execute(sql3)
        conn.commit()

def evadb_insert():
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    cursor = evadb.connect().cursor()
    # cursor.query("DROP TABLE IF EXISTS images").df()
    # index=0
    # for i in range(10000):
    #     index+=1
    #     sql = "LOAD IMAGE '{}' INTO images".format("/data/data/image/image-net/data/" + image_name[index])
    #     print(sql)
    #     cursor.query(sql).df()
    cursor.query("DROP TABLE IF EXISTS conversation_origin").df()
    cursor.query("""CREATE TABLE IF NOT EXISTS conversation_origin (
            datetime TEXT,
            user_id TEXT,
            comment TEXT,
            image TEXT);
            """).df()

    cur.execute("select * from conversation_url;")
    url_rows = cur.fetchall()

    index = 0
    for row in url_rows:
        datetime = row[0]
        user_id = row[1]
        comment = row[2]
        image = pre_path_image + "/data/image/image-net/data/" + image_name[index]
        # # print("image", image)
        # formatted_str = ','.join('[' + format_layer(layer) + ']' for layer in image)
        # formatted_str = '[' + formatted_str + ']'
        # dimension_str_list = []
        # # 遍历数组的每一行
        # for i in range(image.shape[0]):
        #     # 创建一个空列表，用于存储当前行的像素字符串
        #     row_list = []
        #     for j in range(image.shape[1]):
        #         # 将当前像素的 RGB 值转换为用逗号分隔的字符串
        #         pixel_str = ','.join(map(str, image[i, j]))
        #         # 将像素字符串添加到当前行的列表
        #         row_list.append(f"[{pixel_str}]")
        #     # 将当前行的像素列表用空格分隔并添加到维度字符串列表
        #     dimension_str_list.append(f"[{', '.join(row_list)}]")

        # # 将所有行的字符串用换行符分隔，形成最终的三维数组字符串表示
        # image_str = ','.join(dimension_str_list)
        # image_str = '[' + image_str + ']'

        # # #print(image_str)
        #print("index", index)
        index += 1
        # if index == 10:
        #     index = 0
        sql = "INSERT INTO conversation_origin (datetime, user_id, comment, image) VALUES('{}', '{}', \"{}\", '{}')".format(datetime, user_id, comment.replace("'","''"), image)
        #print("sql", sql)
        cursor.query(sql).df()






if __name__ == "__main__":
    morphing_insert()
    evadb_insert()
