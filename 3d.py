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
    with open("data/Zhuang_TrackedLeftController_LeftHand_RightController_Target_Inner.json", "r") as f:
        target_inner = json.load(f)["m_Positions"]
    f.close()

    with open("data/Zhuang_TrackedLeftController_LeftHand_RightController_Target_Outer.json", "r") as f:
        target_outer = json.load(f)["m_Positions"]
    f.close()

    target_inner_x = list()
    target_inner_y = list()
    target_inner_z = list()

    target_outer_x = list()
    target_outer_y = list()
    target_outer_z = list()

    # user_x = list()
    # user_y = list()
    # user_z = list()

    # simulate the 3d data
    # target_z = list(sorted(np.random.normal(0, 50, len(target))))
    # user_z = list()

    # for i in target_z:
    #     user_z.append(i + np.random.random() * 10)

    for item in target_inner:
        # print(item)
        target_inner_x.append(target_inner[item]["x"])
        target_inner_y.append(target_inner[item]["y"])
        target_inner_z.append(target_inner[item]["z"])

    for item in target_outer:
        target_outer_x.append(target_outer[item]["x"])
        target_outer_y.append(target_outer[item]["y"])
        target_outer_z.append(target_outer[item]["z"])

    # for item in user:
    #     user_x.append(item["x"])
    #     user_y.append(item["y"])
    #     user_z.append(item["z"])

    return target_inner_x, target_inner_y, target_inner_z, \
        target_outer_x, target_outer_y, \
        target_outer_z
    # ,user_x, user_y, user_z


def main():
    target_x, target_y, target_z, \
        target_outer_x, target_outer_y, target_outer_z, = data_loader()

    # print("target_x: ", len(target_x))
    # print("target_y: ", len(target_y))
    # # print("user_x: ", len(user_x))
    # # print("user_y: ", len(user_y))
    # print("target_z: ", len(target_z))
    # print("user_z: ", len(user_z))

    with open("data/Zhuang_TrackedLeftController_LeftHand_RightController.json", "r") as f:
        user = json.load(f)
    f.close()

    user_mapping = dict()

    count = 0
    for item in user:
        mapping_inner = list()
        mapping_outer = list()

        user_x = list()
        user_y = list()
        user_z = list()

        for i in item["m_Positions"]:
            user_x.append(item["m_Positions"][i]["x"])
            user_y.append(item["m_Positions"][i]["y"])
            user_z.append(item["m_Positions"][i]["z"])

        # calculate the euclidean distance
        for i in range(len(user_x)):
            min_index = 0
            min_distance = 100000000

            min_outer_index = 0
            min_outer_distance = 100000000
            for j in range(len(target_x)):
                distance = euclidean_distance(target_x[j], target_y[j], target_z[j], user_x[i], user_y[i], user_z[i])
                outer_distance = euclidean_distance(target_outer_x[j], target_outer_y[j], target_outer_z[j],
                                                    user_x[i], user_y[i], user_z[i])
                if distance < min_distance:
                    min_distance = distance
                    min_index = j

                if outer_distance < min_outer_distance:
                    min_outer_distance = outer_distance
                    min_outer_index = j


            mapping_inner.append({"user": (user_x[i], user_y[i], user_z[i]),
                                  "target": (target_x[min_index], target_y[min_index], target_z[min_index]),
                                  "distance": min_distance})
            mapping_outer.append({"user": (user_x[i], user_y[i], user_z[i]),
                                  "target": (target_outer_x[min_outer_index], target_outer_y[min_outer_index],
                                             target_outer_z[min_outer_index]),
                                  "distance": min_outer_distance})

        # user_mapping[item["m_id"]] = {"user": [user_x, user_y, user_z], "inner": mapping_inner, "outer": mapping_outer}
        user_mapping[count] = {"user": [user_x, user_y, user_z], "inner": mapping_inner, "outer": mapping_outer}
        count += 1

        # print(user_mapping)

    # draw the target and user curve
    # plt.subplot(2, 1, 1)
    f1 = plt.figure()
    ax = f1.add_subplot(projection='3d')
    plt.plot(target_x, target_y, target_z, label="target_inner", color="cyan")
    plt.plot(target_outer_x, target_outer_y, target_outer_z, label="target_outer", color="orange")

    # draw the mapping curve
    for id in user_mapping:

        # if id != 0:
        #     continue

        plt.plot(user_mapping[id]["user"][0], user_mapping[id]["user"][1], user_mapping[id]["user"][2], label=id)

        inner = user_mapping[id]["inner"]
        outer = user_mapping[id]["outer"]

        for mapping in inner:
            plt.plot([mapping["user"][0], mapping["target"][0]],
                     [mapping["user"][1], mapping["target"][1]],
                     [mapping["user"][2], mapping["target"][2]],
                     linestyle="-", linewidth=0.5, color="red", alpha=0.5, label="_"+str(id))

        for mapping in outer:
            plt.plot([mapping["user"][0], mapping["target"][0]],
                     [mapping["user"][1], mapping["target"][1]],
                     [mapping["user"][2], mapping["target"][2]],
                     linestyle="-", linewidth=0.5, color="blue", alpha=0.5, label="_"+str(id))

    plt.xlabel("x")
    plt.ylabel("y")
    # plt.zlabel("z")
    # plt.legend()

    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1),
              ncol=2, borderaxespad=0)
    f1.subplots_adjust(right=0.55)
    f1.suptitle('Right-click to hide all\nMiddle-click to show all',
                va='top', size='large')

    leg = interactive_legend()

    return f1, ax, leg


def interactive_legend(ax=None):
    if ax is None:
        ax = plt.gca()
    if ax.legend_ is None:
        ax.legend()

    return InteractiveLegend(ax.get_legend())


class InteractiveLegend(object):
    def __init__(self, legend):
        self.legend = legend
        self.fig = legend.axes.figure

        self.lookup_artist, self.lookup_handle = self._build_lookups(legend)
        self._setup_connections()

        self.update()

    def _setup_connections(self):
        for artist in self.legend.texts + self.legend.legendHandles:
            artist.set_picker(10)  # 10 points tolerance

        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def _build_lookups(self, legend):
        labels = [t.get_text() for t in legend.texts]
        handles = legend.legendHandles
        label2handle = dict(zip(labels, handles))
        handle2text = dict(zip(handles, legend.texts))

        lookup_artist = {}
        lookup_handle = {}
        for artist in legend.axes.get_children():
            if isinstance(artist, plt.Line2D):  # We're only interested in line artists here
                label = artist.get_label()
                if label in labels:
                    handle = label2handle[label]
                    lookup_artist[handle] = [artist]
                    lookup_handle[artist] = handle
                elif label.startswith('_') and label[1:] in labels:
                    # This artist corresponds to a main plot line, store it as well
                    main_label = label[1:]
                    main_handle = label2handle[main_label]
                    if main_handle not in lookup_artist:
                        lookup_artist[main_handle] = []
                    lookup_artist[main_handle].append(artist)
                    lookup_handle[artist] = main_handle

        return lookup_artist, lookup_handle

    def on_pick(self, event):
        handle = event.artist
        if handle in self.lookup_artist:
            # Toggle visibility of all associated artists with this legend item
            for artist in self.lookup_artist[handle]:
                artist.set_visible(not artist.get_visible())
            self.update()

    def on_click(self, event):
        if event.button == 3:
            visible = False
        elif event.button == 2:
            visible = True
        else:
            return

        for artist in self.lookup_artist.values():
            artist.set_visible(visible)
        self.update()

    def update(self):
        for handle, artists in self.lookup_artist.items():
            visible = any(artist.get_visible() for artist in artists)
            handle.set_visible(visible)  # Update legend handle visibility based on associated artists
            for artist in artists:
                # Update the visibility of corresponding '_name' artists
                if hasattr(artist, 'get_label') and artist.get_label().startswith('_'):
                    # Find all artists that have a matching '_name' and toggle their visibility
                    name_to_match = artist.get_label()[1:]
                    for other_artist in self.legend.axes.get_children():
                        if isinstance(other_artist, plt.Line2D) and other_artist.get_label() == name_to_match:
                            other_artist.set_visible(visible)

        self.fig.canvas.draw()

    def show(self):
        plt.show()


if __name__ == "__main__":
    # load data

    # plt.savefig("curve.png", dpi=600, bbox_inches='tight')
    fig, ax, leg = main()
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
