#!/usr/bin/env python3
import enum

import time
import numpy as np
from typing import List, Optional

import armarx.arviz as viz
from armarx.math.transform import Transform
from armarx.tools.cycle_clock import CycleClock


# SLIDER EXAMPLE

class SingleSlider:

    def __init__(self, name: str, color):
        self.box = viz.Box(name)
        self.color = color

        self.initial: np.ndarray = np.zeros(3, float)
        self.translation: np.ndarray = np.zeros(3, float)


class SlidersState:

    ARROW_LENGTH = 1000.0

    def __init__(self, origin: np.ndarray):
        self.origin = np.array(origin)

        self.x = SingleSlider("BoxX", (255, 0, 0))
        self.y = SingleSlider("BoxY", (0, 255, 0))
        self.z = SingleSlider("BoxZ", (0, 0, 255))

        self.sphere = viz.Sphere("Sphere")

        self.layer_interact: Optional[viz.Layer] = None
        self.layer_result: Optional[viz.Layer] = None

        # Initialize
        box_size = 50
        arrow_length = 0.5 * self.ARROW_LENGTH

        self.x.initial = self.origin + (arrow_length, 0.0, 0.0)
        self.x.box.position = self.x.initial
        self.x.box.color = self.x.color
        self.x.box.size = box_size
        self.x.box.enable_interaction(translation="xyzl", hide_during_transform=True)

        self.y.initial = self.origin + (0, arrow_length, 0.0)
        self.y.box.position = self.y.initial
        self.y.box.color = self.y.color
        self.y.box.size = box_size
        self.y.box.enable_interaction(translation="y", hide_during_transform=True)

        self.z.initial = self.origin + (0, 0, arrow_length)
        self.z.box.position = self.z.initial
        self.z.box.color = self.z.color
        self.z.box.size = box_size
        self.z.box.enable_interaction(translation="z", hide_during_transform=True)

        self.sphere.position = self.origin + arrow_length * np.ones(3, float)
        self.sphere.color = (255, 128, 0)
        self.sphere.radius = 30

    def visualize(self, arviz: viz.Client):
        self.layer_interact = arviz.layer("Sliders")

        arrow_width = 10.0

        arrow_x = viz.Arrow(
            "ArrowX",
            color=(255, 0, 0),
            from_to=(self.origin, self.origin + (self.ARROW_LENGTH, 0, 0)),
            width=arrow_width,
        )
        self.layer_interact.add(arrow_x)

        arrow_y = viz.Arrow(
            "ArrowY",
            color=(0, 255, 0),
            from_to=(self.origin, self.origin + (0, self.ARROW_LENGTH, 0)),
            width=arrow_width,
        )
        self.layer_interact.add(arrow_y)

        arrow_z = viz.Arrow(
            "ArrowZ",
            color=(0, 0, 255),
            from_to=(self.origin, self.origin + (0, 0, self.ARROW_LENGTH)),
            width=arrow_width,
        )
        self.layer_interact.add(arrow_z)

        self.layer_interact.elements += [self.x.box, self.y.box, self.z.box]

        self.layer_result = arviz.layer("SlidersResult")
        self.layer_result.add(self.sphere)

    def handle(self, interaction: viz.InteractionFeedback, stage: viz.Stage):
        element = interaction.element
        transform = interaction.transformation
        translation = transform.translation

        slider_dict = {slider.box.id: slider for slider in [self.x, self.y, self.z]}
        slider: Optional[SingleSlider] = slider_dict.get(element, None)
        if slider is None:
            print(f"Unknown interaction: '{element}'")
            return

        type = interaction.type
        Types = viz.InteractionFeedbackType

        if type == Types.Transform:
            slider.translation = translation
            self.sphere.position = (
                self.x.initial[0] + self.x.translation[0],
                self.y.initial[1] + self.y.translation[1],
                self.z.initial[2] + self.z.translation[2],
            )
            stage.add(self.layer_result)

        elif type == Types.Select:
            pass  # Do nothing

        elif type == Types.Deselect:
            # If an object is deselected, we apply the transformation
            slider.initial = slider.initial + slider.translation
            slider.translation = np.zeros(3, float)
            print(f"Setting position to {slider.initial.T}")
            slider.box.position = slider.initial

            stage.add(self.layer_interact)

        else:
            pass  # Do nothing for the other interaction types


# SPAWNER EXAMPLE

class SpawnerType(enum.IntEnum):
    Box = 1
    Cylinder = 2
    Sphere = 3


class SpawnerOption(enum.IntEnum):
    DeleteAll = 0
    DeleteType = 1


class Spawner:

    def __init__(
            self,
            type: SpawnerType = SpawnerType.Box,
            position: Optional[np.ndarray] = None,
            size=100.0,
            color=(0, 0, 0)
    ):
        self.type = type
        self.position = np.zeros(3, float) if position is None else position
        self.size = size
        self.color = color

    def visualize(self, i: int, layer: viz.Layer):
        interaction_kwargs = dict(selection=True, transform=True, scaling="xyz",
                                  context_menu_options=["Delete All", "Delete All of Type"])
        name = f"Spawner_{i}"

        if self.type == SpawnerType.Box:
            layer.add(viz.Box(name, position=self.position, size=self.size, color=self.color)
                      .enable_interaction(**interaction_kwargs))
        elif self.type == SpawnerType.Cylinder:
            layer.add(viz.Cylinder(name, position=self.position, radius=0.5 * self.size, height=self.size, color=self.color)
                      .enable_interaction(**interaction_kwargs))
        elif self.type == SpawnerType.Sphere:
            layer.add(
                viz.Sphere(name, position=self.position, radius=0.5 * self.size, color=self.color)
                .enable_interaction(**interaction_kwargs))
        else:
            raise ValueError(f"Unexcpected enum value {self.type}.")


class SpawnedObject:

    def __init__(
            self,
            index=0,
            source: Spawner = None,
            transform: Optional[Transform] = None,
            scale: np.ndarray = None,
    ):
        self.index = index
        self.source = source
        self.transform = Transform() if transform is None else transform
        self.scale = np.ones(3, float) if scale is None else scale

    def visualize(self, layer: viz.Layer):
        name = f"Object_{self.index}"

        initial = Transform()
        initial.translation = self.source.position
        pose = self.transform * initial

        source = self.source
        if source.type == SpawnerType.Box:
            layer.add(viz.Box(id=name, pose=pose, scale=self.scale, size=source.size, color=source.color)
                      .enable_interaction())
        elif source.type == SpawnerType.Cylinder:
            layer.add(viz.Cylinder(id=name, pose=pose, scale=self.scale, radius=source.size * 0.5, height=source.size,
                                   color=source.color).enable_interaction())
        elif source.type == SpawnerType.Sphere:
            layer.add(viz.Sphere(id=name, pose=pose, scale=self.scale, radius=source.size * 0.5, color=source.color)
                      .enable_interaction())
        else:
            raise ValueError(f"Unexpected enum value: {source.type}.")

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} "
            f"index={self.index} "
            f"source type={self.source.type.name} "
            f"transl={np.round(self.transform.translation, 3)} "
            f"scale={np.round(self.scale, 3)}>"
        )


class SpawnersState:

    def __init__(self, origin: np.ndarray):
        self.origin = origin

        self.spawners: List[Spawner] = []
        self.spawned_object: Optional[SpawnedObject] = None
        self.spawned_object_counter = 0
        self.objects: List[SpawnedObject] = []

        self.layer_spawners: Optional[viz.Layer] = None
        self.layer_objects: Optional[viz.Layer] = None

        # Initialize
        size = 100.0

        self.spawners += [
            Spawner(type=SpawnerType.Box,
                    position=origin + (750, 500, 0.5 * size),
                    color=(0, 255, 255)),
            Spawner(type=SpawnerType.Cylinder,
                    position=origin + (1250, 500, 0.5 * size),
                    color=(255, 0, 128)),
            Spawner(type=SpawnerType.Sphere,
                    position=origin + (1000, 750, 0.5 * size),
                    color=(255, 255, 0)),
        ]

    def visualize(self, arviz: viz.Client):
        self.layer_spawners = arviz.layer("Spawners")

        for index, spawner in enumerate(self.spawners):
            spawner.visualize(index, self.layer_spawners)

        self.layer_objects = arviz.layer("Spawned Objects")

    def handle(self, interaction: viz.InteractionFeedback, stage: viz.Stage):
        spawner: Optional[Spawner] = None
        for i in range(len(self.spawners)):
            name = f"Spawner_{i}"
            if interaction.element == name:
                spawner = self.spawners[i]
                break
        assert spawner is not None, f"Interaction element: {interaction.element}"

        Types = viz.InteractionFeedbackType
        if interaction.type == Types.Select:
            # Create a spawned object.
            print(f"\tSelected {spawner.type.name}.")
            assert self.spawned_object is None, f"Already spawned object: {self.spawned_object}"
            self.spawned_object = SpawnedObject(
                index=self.spawned_object_counter,
                source=spawner,
                transform=Transform(),
                scale=np.ones(3, float)
            )
            self.spawned_object_counter += 1
            print(f"\tSpawned object {self.spawned_object}.")

        elif interaction.type == Types.Transform and self.spawned_object is not None:
            print(f"\tTransformed {spawner.type.name}.")
            # Update state of spawned object.
            print(f"\tUpdate spawned object {self.spawned_object}.")
            self.spawned_object.transform = interaction.transformation
            self.spawned_object.scale = interaction.scale
            if interaction.is_transform_begin:
                self.layer_objects.clear()
                for obj in self.objects:
                    obj.visualize(self.layer_objects)
                stage.add(self.layer_objects)
            if interaction.is_transform_end:
                self.spawned_object.visualize(self.layer_objects)
                stage.add(self.layer_objects)

        elif interaction.type == Types.Deselect and self.spawned_object is not None:
            print(f"\tDeselected {spawner.type.name}.")
            # Store spawned object.
            print(f"\tStore spawned object {self.spawned_object}.")
            self.objects.append(self.spawned_object)
            self.spawned_object = None

        elif interaction.type == Types.ContextMenuChosen:
            print(f"\tContext menu #{interaction.chosen_context_menu_entry}.")
            option = interaction.chosen_context_menu_entry
            if option == SpawnerOption.DeleteAll:
                self.objects.clear()
                self.layer_objects.clear()

                stage.add(self.layer_objects)

            elif option == SpawnerOption.DeleteType:
                self.objects = [obj for obj in self.objects
                                if obj.source is not spawner]

                self.layer_objects.clear()
                for obj in self.objects:
                    obj.visualize(self.layer_objects)

                stage.add(self.layer_objects)

        else:
            # Ignore other interaction types.
            pass


# MAIN

class ArVizInteractExample:

    @classmethod
    def get_name(cls):
        return "ArVizInteractExample"

    def __init__(self, name: str = None):
        self.name = name or self.get_name()
        self.arviz = viz.Client(self.get_name())

    def run(self):
        stage = self.arviz.begin_stage()

        regions = stage.layer("Regions")

        origin1 = np.array([-2000.0, 0.0, 0.0])
        origin2 = np.array([0.0, 0.0, 0.0])
        origin3 = np.array([-2000.0, -2000.0, 0.0])
        origin4 = np.array([0.0, -2000.0, 0.0])

        regions.add(viz.Cylinder("SeparatorX", from_to=(origin1, origin1 + (4000, 0, 0)), radius=5))
        regions.add(viz.Cylinder("SeparatorY", from_to=(origin4, origin4 + (0, 4000, 0)), radius=5))

        sliders = SlidersState(origin=origin1 + (500, 500, 0))
        spawners = SpawnersState(origin2)

        sliders.visualize(self.arviz)
        stage.add([sliders.layer_interact, sliders.layer_result])

        spawners.visualize(self.arviz)
        stage.add([spawners.layer_spawners, spawners.layer_objects])

        result = self.arviz.commit(stage)
        print(f"Initial commit at revision: {result.revision}")

        try:
            print("Press Ctrl+C to interrupt...")

            cycle = CycleClock(duration_seconds=0.025)
            while True:

                result = self.arviz.commit(stage)

                # Reset the stage, so that it can be rebuild during the interaction handling
                stage.reset()

                stage.request_interaction(sliders.layer_interact)
                stage.request_interaction(spawners.layer_spawners)

                if len(result.interactions) > 0:
                    print(f"Received {len(result.interactions)} interactions.")

                for interaction in result.interactions:
                    if interaction.layer == "Sliders":
                        print(f"Processing slider interaction ... (revision {result.revision})")
                        sliders.handle(interaction, stage)

                    if interaction.layer == "Spawners":
                        print(f"Processing spawner interaction ... (revision {result.revision})")
                        spawners.handle(interaction, stage)

                cycle.wait_for_next_cycle()

        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    example = ArVizInteractExample()
    example.run()
    print("Finished.")
