import utils
import json


def main():
    with open("preprocessed_data.json", "r") as f:
        data = json.load(f)

    result = dict()
    for user in data.keys():
        result[user] = dict()

        for device in data[user].keys():
            result[user][device] = {
                "inner": [],
                "outer": []
            }
            for item in ["inner", "outer"]:
                for user_data in data[user][device][item]["data"]:
                    mapping, avg_distance, median_distance = utils.cal_curve_mapping(
                        user_data, data[user][device][item]["target"]
                    )
                    result[user][device][item].append(
                        {
                            "mapping": mapping,
                            "avg_distance": avg_distance,
                            "median_distance": median_distance
                        }
                    )

    with open("processed_data.json", "w") as f:
        json.dump(result, f)


    # temp code

    with open("Target_Inner.json", "w") as f:
        json.dump(data["P03"]["Pen"]["inner"]["target"], f)

    with open("Target_Outer.json", "w") as f:
        json.dump(data["P03"]["Pen"]["outer"]["target"], f)

    with open("Data_Inner.json", "w") as f:
        json.dump(data["P03"]["Pen"]["inner"]["data"], f)

    with open("Data_Outer.json", "w") as f:
        json.dump(data["P03"]["Pen"]["outer"]["data"], f)


if __name__ == "__main__":
    main()
