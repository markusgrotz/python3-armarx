#!/usr/bin/env python3

import time

import numpy as np
import transforms3d as tf3d

import armarx
import armarx.arviz as viz


def fill_test_layer(layer: viz.Layer, time_sec):
    delta = 20 * np.sin(time_sec)
    layer.elements += [
        viz.Box("box", position=(100 * np.sin(time_sec), 0, 0),
                size=100, color=(255, 0, 0)),
        viz.Ellipsoid("ellipsoid", position=(0, 100, 150), color=(0, 0, 255),
                      axis_lengths=(70 + delta, 70 - delta, 30)),
        viz.Cylinder("cylinder", position=(150, 100 * np.sin(time_sec), 0),
                     radius=50, height=100, color=(0, 255, 0)),
        viz.Pose("pose", position=(-150, 0, 100*np.sin(time_sec))),
        viz.Text("text", text="Test Text", position=(0, 0, 300),
                 scale=4.0, color=(0, 0, 0)),
    ]
    arrow = viz.Arrow("arrow")
    mod_time = np.fmod(time_sec, 2*np.pi)
    arrow.length = 200 + 100 * np.sin(mod_time)
    dir_rot = tf3d.axangles.axangle2mat((0, 0, 1), mod_time)
    arrow.direction = dir_rot @ (1, 0, 0)
    arrow.position[0] = -500
    arrow.position[2] = +300
    arrow.color = (0, 0, 255)
    layer.add(arrow)


def fill_example_layer(layer: viz.Layer, time_sec):
    layer.add(viz.ArrowCircle("circle", position=(300, 0, 0), color=(255, 0, 255),
                              radius=100, width=10,
                              completion=np.sin(np.fmod(time_sec, 2*np.pi))))

    poly = viz.Polygon("poly", position=(1000, 0, 0), color=(0, 128, 255, 128),
                       line_color=(0, 0, 255), line_width=1.0)
    offset = 50 * (1.0 + np.sin(time_sec))
    poly.points = [
        [-200.0 - offset, -200.0 - offset, 0.0],
        [-200.0, +200.0, 0.0],
        [+200.0 + offset, +200.0 + offset, 0.0],
        [+200.0, -200.0, 0.0],
    ]
    layer.elements.append(poly)

    poly = viz.Polygon("poly", position=(1500, 0, 0), color=(255, 128, 0, 128),
                       line_width=0.0)
    offset = 20 * (1.0 + np.sin(time_sec))
    poly.points = [
        [-100.0 - offset, -100.0 - offset, 0.0],
        [-100.0, +100.0, 0.0],
        [+100.0 + offset, +100.0 + offset, 0.0],
        [+100.0, -100.0, 0.0],
    ]
    layer.add(poly)

    mesh = viz.Mesh("mesh", position=(-500, 0, 1000))
    mesh.vertices = [
        [-100.0, -100.0, 0.0],
        [-100.0, +100.0, 0.0],
        [+100.0, +100.0, 0.0],
        [+100.0, +100.0, 200.0],
    ]
    mesh.colors = [
        [255, 0, 0, 255],
        [0, 255, 0, 255],
        [0, 0, 255, 255],
    ]
    mesh.faces = [
        [0, 1, 2,
         0, 1, 2],
        [1, 2, 3,
         0, 1, 2]
    ]
    layer.add(mesh)

    robot = viz.Robot("robot", position=(500, 0, 0),
                      file=("Armar6RT", "Armar6RT/robotmodel/Armar6-SH/Armar6-SH.xml"))
    full_model = True
    if full_model:
        robot.use_full_model()
    else:
        robot.use_collision_model()
        robot.override_color((0, 255, 128, 128))

    value = 0.5 * (1.0 + np.sin(time_sec))
    robot.joint_angles["ArmR2_Sho1"] = value
    robot.joint_angles["ArmR3_Sho2"] = value

    robot.get_ice_data()

    layer.add(robot)


def fill_points_layer(layer: viz.Layer, time_sec):
    pc = viz.PointCloud("points", position=(2000, 0, 400), transparency=0.0,
                        point_size=3)
    num = 50
    points = np.zeros((2*num+1, 2*num+1, 7))
    # Form of a point: [x y z r g b a]

    xs, ys = np.meshgrid(np.arange(-num, num+1), np.arange(-num, num+1))
    phases = time_sec + xs / 50.0
    height_ts = np.clip(0.5 * (1.0 + np.sin(phases)), 0, 1)

    positions = np.stack([4 * xs, 4 * ys, 100 * height_ts], axis=-1)
    pc.points = positions.reshape((-1, 3))
    # pc.points is widened to shape (..., 7) to include color.

    green_blues = np.stack([255 * height_ts, 255 * (1 - height_ts)], axis=-1)
    pc.point_colors[:, 0] = 255
    pc.point_colors[:, 3] = 255
    pc.point_colors[:, 1:3] = green_blues.reshape((-1, 2))

    layer.add(pc)


def fill_objects_layer(layer: viz.Layer, time_sec):
    layer.elements += [
        viz.Object("Amicelli", position=(100 * np.sin(time_sec), 1000, 0),
                   orientation=tf3d.axangles.axangle2mat((1, 0, 0), np.pi/2),
                   project="ArmarXObjects",
                   filename="ArmarXObjects/KIT/Amicelli/Amicelli.xml",
                   override_color=(128, 128, 255, 128)),

        viz.Object("workbench", position=(300 + 100 * np.sin(time_sec), 1000, 0),
                   project="ArmarXObjects",
                   filename="ArmarXObjects/OML/workbench/workbench.xml",
                   scale=0.1),
    ]


def main():
    # Create a client with a name.
    arviz = viz.Client("ArViz Python Example")

    # Basic usage: Create layers, fill them, and commit them.
    origin_layer = arviz.layer("Origin")
    origin_layer.add(viz.Pose("origin"))
    permanent_layer = arviz.layer("Permanent")
    permanent_layer.elements += [viz.Box("box", position=(2000, 0, 0), size=200, color=(255, 165, 0))]
    arviz.commit([origin_layer, permanent_layer])  # This is a network call.

    # Example usage in a loop:

    # Create a Stage: A collection of layers to be committed together.
    stage = arviz.begin_stage()
    # Create layers using stage - they are stored in the stage.
    test_layer = stage.layer("Test")
    example_layer = stage.layer("Example")
    points_layer = stage.layer("Points")
    objects_layer = stage.layer("Objects")

    try:
        print("Press Ctrl+C to stop.")
        while True:
            time_sec = time.time()

            # Clear and the layers
            print("Filling layers ...   ", end="", flush=True)
            test_layer.clear()
            fill_test_layer(test_layer, time_sec)
            example_layer.clear()
            fill_example_layer(example_layer, time_sec)
            points_layer.clear()
            # fill_points_layer(points_layer, time_sec)  # This is a bit slow.
            objects_layer.clear()
            fill_objects_layer(objects_layer, time_sec)
            print(" (took {:.3f} s)".format(time.time() - time_sec))

            # Commit the stage
            print("Committing layers ...", end="", flush=True)
            time_start = time.time()
            arviz.commit(stage)
            print(" (took {:.3f} s)".format(time.time() - time_start))

            time.sleep(0.02)
    except KeyboardInterrupt:
        # Ctrl + C was pressed.
        pass


if __name__ == '__main__':
    main()
