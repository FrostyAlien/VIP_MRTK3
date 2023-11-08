import os
import json
import numpy as np
import matplotlib.pyplot as plt


# Euclidean distance (2d)
def euclidean_distance(target_x: float, target_y: float, user_x: float, user_y: float) -> float:
    return np.sqrt((target_x - user_x) ** 2 + (target_y - user_y) ** 2)


def data_loader() -> (list, list, list, list):
    with open("data/Zhuang_TwoControllersTarget.json", "r") as f:
        target = json.load(f)["m_PixelCoodinates"]
    f.close()

    with open("data/Zhuang_TwoControllersUser.json", "r") as f:
        user = json.load(f)["m_PixelCoodinates"]
    f.close()

    target_x = list()
    target_y = list()
    user_x = list()
    user_y = list()

    for item in target:
        target_x.append(item["x"])
        target_y.append(item["y"])

    for item in user:
        user_x.append(item["x"])
        user_y.append(item["y"])

    return target_x, target_y, user_x, user_y


if __name__ == "__main__":
    print("Hello World")

    # load data
    target_x, target_y, user_x, user_y = data_loader()
    print("target_x: ", target_x)
    print("target_y: ", target_y)
    print("user_x: ", user_x)
    print("user_y: ", user_y)

    mapping = list()
    # calculate the euclidean distance
    for i in range(len(user_x)):
        min_index = 0
        min_distance = 100000000
        for j in range(len(target_x)):
            distance = euclidean_distance(target_x[j], target_y[j], user_x[i], user_y[i])
            if distance < min_distance:
                min_distance = distance
                min_index = j
        mapping.append({"user": (user_x[i], user_y[i]), "target": (target_x[min_index], target_y[min_index]),
                        "distance": min_distance})

    # draw the target and user curve
    # plt.subplot(2, 1, 1)
    f1 = plt.figure()
    plt.plot(target_x, target_y, label="target", color="red")
    plt.plot(user_x, user_y, label="user", color="blue")

    # draw the mapping curve
    for item in mapping:
        plt.plot([item["user"][0], item["target"][0]], [item["user"][1], item["target"][1]],
                 color="green", linestyle="-")

    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.savefig("curve.png", dpi=600, bbox_inches='tight')
    plt.show()

    # draw the distribution of the distance
    # plt.subplot(2, 1, 2)
    f2 = plt.figure()
    distance = list()
    for item in mapping:
        distance.append(item["distance"])
    plt.hist(distance, bins=20)
    plt.savefig("distribution.png", dpi=600, bbox_inches='tight')
    plt.show()


