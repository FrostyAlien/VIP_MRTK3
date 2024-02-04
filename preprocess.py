import os
import json
import numpy as np

data_path = 'data/Accuracy'
dir_list = os.listdir(data_path)


def drop_useless_data(data):
    return data[0]["m_Positions"]


def split_inner_outer(data):
    inner = []
    outer = []

    # order: inner, outer, inner, outer, ...
    split_data = []
    temp = []
    prev_key = 0

    for key, value in data.items():
        current_key = int(key.split('_')[0])
        if current_key < prev_key:
            split_data.append(temp)
            temp = []
        temp.append(value)
        prev_key = current_key

    if temp:
        split_data.append(temp)

    for i in range(len(split_data)):
        if i % 2 == 0:
            inner.append(split_data[i])
        else:
            outer.append(split_data[i])

    return inner, outer


# data_path/[ID]/[Controller, Hand, Pen]/[data, Target_Inner, Target_Outer]
p_id = ""
device_name = ""
all_data = dict()

for ID in dir_list:
    p_id = ID.split('_')[0]
    print(p_id)
    p_data = dict()

    for device in os.listdir(data_path + '/' + ID):
        device_name = device.split('_')[0]
        print(device_name)
        for item in os.listdir(data_path + '/' + ID + '/' + device):
            print(item)
            with open(data_path + '/' + ID + '/' + device + '/' + item, 'r') as f:
                json_data = json.load(f)

                if 'Target_Inner' in item:
                    print("Target_Inner found")
                    target_inner = json_data
                elif 'Target_Outer' in item:
                    print("Target_Outer found")
                    target_outer = json_data
                else:
                    print("Data found")
                    data = json_data

        # preprocess
        data = data[0]["m_Positions"]
        # print(data)
        target_inner = target_inner["m_Positions"]
        target_outer = target_outer["m_Positions"]
        data_inner, data_outer = split_inner_outer(data)

        inner = {
            "target": target_inner,
            "data": data_inner
        }

        outer = {
            "target": target_outer,
            "data": data_outer
        }

        p_data[device_name] = {
            "inner": inner,
            "outer": outer
        }

    all_data[p_id] = p_data

# print(all_data)

with open('preprocessed_data.json', 'w') as f:
    json.dump(all_data, f)
