import os
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

USERID = "P09"
mode = "inner"


# Euclidean distance (3d)
def euclidean_distance(target_x: float, target_y: float, target_z: float,
                       user_x: float, user_y: float, user_z: float) -> float:
    return np.sqrt((target_x - user_x) ** 2 + (target_y - user_y) ** 2 + (target_z - user_z) ** 2)


def data_loader() -> (list, list, list, list):
    with open("data/Target_Inner.json", "r") as f:
        target_inner = json.load(f)
    f.close()

    with open("data/Target_Outer.json", "r") as f:
        target_outer = json.load(f)
    f.close()

    target_inner_x = list()
    target_inner_y = list()
    target_inner_z = list()

    target_outer_x = list()
    target_outer_y = list()
    target_outer_z = list()

    for item in target_inner:
        # print(item)
        target_inner_x.append(target_inner[item]["x"])
        target_inner_y.append(target_inner[item]["y"])
        target_inner_z.append(target_inner[item]["z"])

    for item in target_outer:
        target_outer_x.append(target_outer[item]["x"])
        target_outer_y.append(target_outer[item]["y"])
        target_outer_z.append(target_outer[item]["z"])

    return target_inner_x, target_inner_y, target_inner_z, \
        target_outer_x, target_outer_y, \
        target_outer_z


def cal_curve_mapping(user_data, target):
    mapping = list()
    distance_list = list()

    for user in user_data.values():
        min_index = 0
        min_point = {}
        min_distance = 100000000

        for j in target:
            distance = euclidean_distance(target[j]["x"], target[j]["y"], target[j]["z"],
                                          user["x"], user["y"], user["z"])
            if distance < min_distance:
                min_distance = distance
                # min_index = j
                min_point = target[j]

        mapping.append({"user": user, "target": min_point, "distance": min_distance})
        distance_list.append(min_distance)

    return mapping


def main():
    target_x, target_y, target_z, \
        target_outer_x, target_outer_y, target_outer_z, = data_loader()

    with open(f"data/Test_{USERID}/result.json", "r") as f:
        users = json.load(f)
    f.close()

    controller_mapping = users[USERID]["Controller"][mode]
    hand_mapping = users[USERID]["Hand"][mode]
    pen_mapping = users[USERID]["Pen"][mode]

    # draw the target and user curve
    # plt.subplot(2, 1, 1)
    f1 = plt.figure()
    ax = f1.add_subplot(projection='3d')

    if mode == "inner":
        plt.plot(target_x, target_y, target_z, label="target_inner", color="cyan", linewidth=3.5)
    else:
        plt.plot(target_outer_x, target_outer_y, target_outer_z, label="target_outer", color="black", linewidth=3.5)

    # plt.plot(target_outer_x, target_outer_y, target_outer_z, label="target_outer", color="black", linewidth=3.5)

    # draw the user curve
    count = 0
    for trial in controller_mapping:
        controller_user_curve_x = list()
        controller_user_curve_y = list()
        controller_user_curve_z = list()
        for item in trial["mapping"]:
            controller_user_curve_x.append(item["user"]["x"])
            controller_user_curve_y.append(item["user"]["y"])
            controller_user_curve_z.append(item["user"]["z"])
        plt.plot(controller_user_curve_x, controller_user_curve_y, controller_user_curve_z, label=f"controller_{count}",
                 color="red", linewidth=1.0)
        count += 1

    count = 0
    for trial in hand_mapping:
        hand_user_curve_x = list()
        hand_user_curve_y = list()
        hand_user_curve_z = list()
        for item in trial["mapping"]:
            hand_user_curve_x.append(item["user"]["x"])
            hand_user_curve_y.append(item["user"]["y"])
            hand_user_curve_z.append(item["user"]["z"])
        plt.plot(hand_user_curve_x, hand_user_curve_y, hand_user_curve_z, label=f"hand_{count}", color="green",
                 linewidth=1.0)

    count = 0
    for trial in pen_mapping:
        pen_user_curve_x = list()
        pen_user_curve_y = list()
        pen_user_curve_z = list()
        for item in trial["mapping"]:
            pen_user_curve_x.append(item["user"]["x"])
            pen_user_curve_y.append(item["user"]["y"])
            pen_user_curve_z.append(item["user"]["z"])
        plt.plot(pen_user_curve_x, pen_user_curve_y, pen_user_curve_z, label=f"pen_{count}", color="royalblue",
                 linewidth=1.0)
        count += 1

    plt.xlabel("x")
    plt.ylabel("y")
    ax.set_zlabel("z")
    # plt.legend()

    ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1),
              ncol=2, borderaxespad=0)
    f1.subplots_adjust(right=0.55)
    f1.suptitle('Right-click to hide all\nMiddle-click to show all\nPress i to toggle inner\nPress o to toggle outer',
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
        self.color_visibility = {'red': True, 'blue': True}

        self.lookup_artist, self.lookup_handle = self._build_lookups(legend)
        self._setup_connections()

        self.update()

    def _setup_connections(self):
        for artist in self.legend.texts + self.legend.legendHandles:
            artist.set_picker(10)  # 10 points tolerance

        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        # Connect additional click events for hiding and showing all plots
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
            new_visibility = not self.lookup_artist[handle][0].get_visible()
            for artist in self.lookup_artist[handle]:
                artist.set_visible(new_visibility)
                # Update visibility based on color filters as well
                if hasattr(artist, 'get_color'):
                    artist_color = artist.get_color()
                    artist.set_visible(new_visibility and self.color_visibility.get(artist_color, True))
            self.update()

    def on_click(self, event):
        if event.button == 3:  # Right-click to hide all
            for artist in self.lookup_handle.keys():
                artist.set_visible(False)
            for color in self.color_visibility:
                self.color_visibility[color] = False
            self.update()
        elif event.button == 2:  # Middle-click to show all
            for artist in self.lookup_handle.keys():
                artist.set_visible(True)
            for color in self.color_visibility:
                self.color_visibility[color] = True
            self.update()

    def update(self):
        # Update legend handle visibility based on associated artists
        for handle, artists in self.lookup_artist.items():
            visible = any(artist.get_visible() for artist in artists)
            handle.set_visible(visible)

        # Update artist visibility based on both their individual setting and color filter
        for artist in self.lookup_handle.keys():
            if hasattr(artist, 'get_color'):
                artist_color = artist.get_color()
                if artist_color in self.color_visibility:
                    # Apply individual and color visibility
                    artist.set_visible(artist.get_visible() and self.color_visibility[artist_color])

        self.fig.canvas.draw()

    def toggle_color(self, color):
        # Flip the visibility state for the specified color
        self.color_visibility[color] = not self.color_visibility[color]

        for artist in self.lookup_handle.keys():
            if hasattr(artist, 'get_color'):
                artist_color = artist.get_color()
                if artist_color == color:
                    # Set visibility based on the new color filter state
                    artist.set_visible(self.color_visibility[color])

        self.update()

    def show(self):
        plt.show()


if __name__ == "__main__":
    # load data

    # plt.savefig("curve.png", dpi=600, bbox_inches='tight')
    fig, ax, leg = main()


    # Create a switch function for each color
    def switch_red():
        leg.toggle_color('red')


    def switch_blue():
        leg.toggle_color('blue')


    # Connect the switch functions to key presses
    plt.connect('key_press_event', lambda event: switch_red() if event.key == 'i' else None)
    plt.connect('key_press_event', lambda event: switch_blue() if event.key == 'o' else None)

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
