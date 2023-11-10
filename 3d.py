import os
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


# Euclidean distance (2d)
def euclidean_distance(target_x: float, target_y: float, target_z: float,
                       user_x: float, user_y: float, user_z: float) -> float:
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

    # simulate the 3d data
    target_z = list(sorted(np.random.normal(0, 50, len(target))))
    user_z = list()

    for i in target_z:
        user_z.append(i + np.random.random() * 10)

    for item in target:
        target_x.append(item["x"])
        target_y.append(item["y"])

    for item in user:
        user_x.append(item["x"])
        user_y.append(item["y"])

    return target_x, target_y, user_x, user_y, target_z, user_z[0:len(user_x)]


if __name__ == "__main__":
    print("Hello World")

    # load data
    target_x, target_y, user_x, user_y, target_z, user_z = data_loader()
    print("target_x: ", len(target_x))
    print("target_y: ", len(target_y))
    print("user_x: ", len(user_x))
    print("user_y: ", len(user_y))
    print("target_z: ", len(target_z))
    print("user_z: ", len(user_z))

    mapping = list()
    # calculate the euclidean distance
    for i in range(len(user_x)):
        min_index = 0
        min_distance = 100000000
        for j in range(len(target_x)):
            distance = euclidean_distance(target_x[j], target_y[j], target_z[j], user_x[i], user_y[i], user_z[i])
            if distance < min_distance:
                min_distance = distance
                min_index = j
        mapping.append({"user": (user_x[i], user_y[i], user_z[i]),
                        "target": (target_x[min_index], target_y[min_index], target_z[min_index]),
                        "distance": min_distance})

    # draw the target and user curve
    # plt.subplot(2, 1, 1)
    f1 = plt.figure()
    ax = f1.add_subplot(projection='3d')
    plt.plot(target_x, target_y, target_z, label="target", color="red")
    plt.plot(user_x, user_y, user_z, label="user", color="blue")

    # draw the mapping curve
    for item in mapping:
        plt.plot([item["user"][0], item["target"][0]],
                 [item["user"][1], item["target"][1]],
                 [item["user"][2], item["target"][2]],
                 color="green", linestyle="-", linewidth=0.5)

    plt.xlabel("x")
    plt.ylabel("y")
    # plt.zlabel("z")
    plt.legend()
    # plt.savefig("curve.png", dpi=600, bbox_inches='tight')
    plt.show()

    # draw the distribution of the distance
    # plt.subplot(2, 1, 2)
    # f2 = plt.figure()
    # distance = list()
    # for item in mapping:
    #     distance.append(item["distance"])
    # plt.hist(distance, bins=20)
    # plt.savefig("distribution.png", dpi=600, bbox_inches='tight')
    # plt.show()


