import numpy as np

import utils
import json

OUTLIER_THRESHOLD = 0.04


def get_point_key(data, point):
    for i in data:
        if data[i]["x"] == point["x"] and data[i]["y"] == point["y"] and data[i]["z"] == point["z"]:
            return i
    return None


def handle_mapping(user, device, item, user_data_index, user_data_item, target_data, result):
    mapping = utils.cal_curve_mapping(user_data_item, target_data)
    cleaned_mapping = []
    for map_index, map_item in enumerate(mapping):
        if map_item["distance"] > OUTLIER_THRESHOLD:
            print(f"[{user}][{device}][{item}][iter: {user_data_index}]Outlier found: {map_item['distance']}")
            user_data_item.pop(get_point_key(user_data_item, map_item["user"]))
            continue

        duplicate_found = next((j for j in cleaned_mapping if j["target"] == map_item["target"]), None)
        if duplicate_found:
            if map_item["distance"] >= duplicate_found["distance"]:
                print(f"[{user}][{device}][{item}][iter: {user_data_index}]Removed duplicate mapping: {map_index}")
                user_data_item.pop(get_point_key(user_data_item, map_item["user"]))
                continue
            else:
                print(f"[{user}][{device}][{item}][iter: {user_data_index}]Update mapping: from {duplicate_found} to {map_item}")
                cleaned_mapping.remove(duplicate_found)
                user_data_item.pop(get_point_key(user_data_item, duplicate_found["user"]))

        cleaned_mapping.append(map_item)

    distances = [i["distance"] for i in cleaned_mapping]
    avg_distance = np.mean(distances)
    median_distance = np.median(distances)

    result[user][device][item].append({
        "mapping": cleaned_mapping,
        "avg_distance": avg_distance,
        "median_distance": median_distance
    })

    return user_data_item


def main():
    with open("data/Test3/preprocessed_data.json", "r") as f:
        data = json.load(f)

    result = dict()
    for user, user_data in data.items():
        result[user] = dict()
        for device, device_data in user_data.items():
            result[user][device] = {
                "inner": [],
                "outer": []
            }
            for item in ["inner", "outer"]:
                for user_data_index, user_data_item in enumerate(device_data[item]["data"]):
                    cleaned_user_data_item = handle_mapping(user, device, item, user_data_index, user_data_item, device_data[item]["target"], result)
                    data[user][device][item]["data"][user_data_index] = cleaned_user_data_item  # update data with cleaned user_data_item

    with open("data/Test3/Target_Inner.json", "w") as f:
        json.dump(data["P01"]["Controller"]["inner"]["target"], f)

    with open("data/Test3/Target_Outer.json", "w") as f:
        json.dump(data["P01"]["Controller"]["outer"]["target"], f)

    with open("data/Test3/Data_Inner.json", "w") as f:
        json.dump(data["P01"]["Controller"]["inner"]["data"], f)

    with open("data/Test3/Data_Outer.json", "w") as f:
        json.dump(data["P01"]["Controller"]["outer"]["data"], f)


if __name__ == "__main__":
    main()
