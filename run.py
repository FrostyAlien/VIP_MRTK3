import utils
import json


def main():
    with open("preprocessed_data.json", "r") as f:
        data = json.load(f)

    result = dict()
    for user in data.keys():
        result[user] = dict()

        for device in data["P02"].keys():
            result[user][device] = {
                "inner": [],
                "outer": []
            }
            for item in ["inner", "outer"]:
                for user_data in data["P02"][device][item]["data"]:
                    mapping, avg_distance, median_distance = utils.cal_curve_mapping(
                        user_data, data["P02"][device][item]["target"]
                    )
                    result[user][device][item].append(
                        {
                            # "mapping": mapping,
                            "avg_distance": avg_distance,
                            "median_distance": median_distance
                        }
                    )

    with open("processed_data.json", "w") as f:
        json.dump(result, f)


if __name__ == "__main__":
    main()
