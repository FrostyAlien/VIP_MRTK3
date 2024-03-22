import numpy as np
import csv
import utils
import json

#OUTLIER_THRESHOLD = 0.04
ACTIVATE_THRESHOLD = 0.04
DEACTIVATE_THRESHOLD = 0.025

#OUTLIER_THRESHOLD = 999

data_path = 'data/AR_3-12'

def get_point_key(data, point):
    for i in data:
        if data[i]["x"] == point["x"] and data[i]["y"] == point["y"] and data[i]["z"] == point["z"]:
            return i
    return None


def handle_mapping(user, device, item, user_data_index, user_data_item, target_data, result):
    # Calculate the mapping between user data and target data
    mapping = utils.cal_curve_mapping(user_data_item, target_data)
    cleaned_mapping = []
    activate_filtering = False  # Flag to activate filtering based on thresholds

    for map_index, map_item in enumerate(mapping):
        if activate_filtering:
            # If filtering is activated, remove all points until a point is found within DEACTIVATE_THRESHOLD
            if map_item["distance"] <= DEACTIVATE_THRESHOLD:
                activate_filtering = False  # Deactivate filtering
                print(f"[{user}][{device}][{item}][iter: {user_data_index}]Deactivation threshold passed: {map_item['distance']}")
            else:
                # Remove points exceeding DEACTIVATE_THRESHOLD while filtering is active
                print(f"[{user}][{device}][{item}][iter: {user_data_index}]Removed due to filtering: {map_item['distance']}")
                user_data_item.pop(get_point_key(user_data_item, map_item["user"]))
                continue
        elif map_item["distance"] > ACTIVATE_THRESHOLD:
            # Activate filtering when a point exceeds ACTIVATE_THRESHOLD
            activate_filtering = True
            print(f"[{user}][{device}][{item}][iter: {user_data_index}]Activation threshold passed: {map_item['distance']}")
            user_data_item.pop(get_point_key(user_data_item, map_item["user"]))
            continue

        # Check for duplicate mappings and keep only the one with the smallest distance
        duplicate_found = next((j for j in cleaned_mapping if j["target"] == map_item["target"]), None)
        if duplicate_found:
            if map_item["distance"] >= duplicate_found["distance"]:
                # Remove the current mapping if a duplicate with a smaller distance exists
                print(f"[{user}][{device}][{item}][iter: {user_data_index}]Removed duplicate mapping: {map_index}")
                user_data_item.pop(get_point_key(user_data_item, map_item["user"]))
                continue
            else:
                # Update mapping if the current one has a smaller distance than the duplicate
                print(f"[{user}][{device}][{item}][iter: {user_data_index}]Update mapping: from {duplicate_found} to {map_item}")
                cleaned_mapping.remove(duplicate_found)
                user_data_item.pop(get_point_key(user_data_item, duplicate_found["user"]))

        # Add the current mapping to the cleaned mapping list
        cleaned_mapping.append(map_item)

    # Calculate average and median distances for the cleaned mappings
    distances = [i["distance"] for i in cleaned_mapping]
    avg_distance = np.mean(distances)
    median_distance = np.median(distances)

    # Append the results to the result dictionary
    result[user][device][item].append({
        "mapping": cleaned_mapping,
        "avg_distance": avg_distance,
        "median_distance": median_distance
    })

    return user_data_item


def main():
    with open(f"{data_path}/preprocessed_data.json", "r") as f:
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

                with open(f"{data_path}/{user}_{device}_{item}.json", "w") as f:
                    json.dump(data[user][device][item]["data"], f)
                with open(f"{data_path}/{user}_{device}_{item}_target.json", "w") as f:
                    json.dump(device_data[item]["target"], f)

    with open(f"{data_path}/result.json", "w") as f:
        json.dump(result, f)

    # Create a new result without 'mapping' attribute
    result_without_mapping = dict()
    for user, user_data in result.items():
        result_without_mapping[user] = dict()
        for device, device_data in user_data.items():
            result_without_mapping[user][device] = {
                "inner": [{"avg_distance": i["avg_distance"], "median_distance": i["median_distance"]} for i in device_data["inner"]],
                "outer": [{"avg_distance": i["avg_distance"], "median_distance": i["median_distance"]} for i in device_data["outer"]]
            }

    # Export the new result
    with open(f"{data_path}/result_without_mapping.json", "w") as f:
        json.dump(result_without_mapping, f)

    # Organize data by device and export to CSV files
    devices = set(device for user_data in result.values() for device in user_data.keys())
    for device in devices:
        with open(f"{data_path}/{device}_result.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["PID", "trail number", "accuracy", "inner/outer"])
            for user, user_data in result.items():
                if device in user_data:
                    for item in ["inner", "outer"]:
                        for i, data_item in enumerate(user_data[device][item]):
                            writer.writerow([user, i+1, data_item["median_distance"], item[0]])


if __name__ == "__main__":
    main()
