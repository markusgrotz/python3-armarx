#!/usr/bin/env python3
import enum

import time
import numpy as np
from typing import List, Optional

import armarx.arviz as viz
from armarx.math.transform import Transform


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
    DeleteAll = 1
    DeleteType = 2


class Spawner:

    def __init__(self):
        self.type: SpawnerType = SpawnerType.Box
        self.position = np.zeros(3, float)
        self.size = 100.
        self.color = (0, 0, 0)

    def visualize(self, i: int, layer: viz.Layer):
        interaction_kwargs = dict(selection=True, transform=True, scaling="xyz",
                                  context_menu_options=["Delete All", "Delete All of Type"])
        name = f"Spawner_{i}"

        if type == SpawnerType.Box:
            layer.add(viz.Box(name, position=self.position, size=self.size, color=self.color)
                      .enable_interaction(**interaction_kwargs))
        elif type == SpawnerType.Cylinder:
            layer.add(viz.Cylinder(name, position=self.position, radius=0.5 * self.size, height=self.size, color=self.color)
                      .enable_interaction(**interaction_kwargs))
        elif type == SpawnerType.Sphere:
            layer.add(
                viz.Sphere(name, position=self.position, radius=0.5 * self.size, color=self.color)
                .enable_interaction(**interaction_kwargs))


class SpawnedObject:

    def __init__(self):
        self.index = 0
        self.source: Optional[Spawner] = None
        self.transform = Transform()
        self.scale = np.ones(3, float)

    def visualize(self, layer: viz.Layer):
        name = f"Object_{self.index}"

        initial = Transform()
        initial.translation = self.source.position
        pose = self.transform * initial

        source = self.source
        if source.type == SpawnerType.Box:
            layer.add(viz.Box(id=name, pose=pose, scale=self.scale, size=source.size, color=source.color))
        elif source.type == SpawnerType.Cylinder:
            layer.add(viz.Cylinder(id=name, pose=pose, scale=self.scale, radius=source.size * 0.5, height=source.size,
                                   color=source.color))
        elif source.type == SpawnerType.Sphere:
            layer.add(viz.Cylinder(id=name, pose=pose, scale=self.scale, radius=source.size * 0.5, color=source.color))


class SpawnersState:

    def __init__(self, origin: np.ndarray):
        self.origin = origin

        spawners: List[Spawner] = []
        
        """
            Eigen.Vector3f origin

            std.vector<Spawner> spawners
            SpawnedObject spawnedObject
            int spawnedObjectCounter = 0
            std.vector<SpawnedObject> objects

            viz.Layer layerSpawners
            viz.Layer layerObjects
        """
"""

struct SpawnersState
{
    SpawnersState(Eigen.Vector3f origin)
        : origin(origin)
    {
        float size = 100.0f
        {
            Spawner& spawner = spawners.emplace_back()
            spawner.type = SpawnerType.Box
            spawner.position = origin + Eigen.Vector3f(750.0f, 500.0f, 0.5f * size)
            spawner.color = viz.Color.cyan()
        }
        {
            Spawner& spawner = spawners.emplace_back()
            spawner.type = SpawnerType.Cylinder
            spawner.position = origin + Eigen.Vector3f(1250.0f, 500.0f, 0.5f * size)
            spawner.color = viz.Color.magenta()
        }
        {
            Spawner& spawner = spawners.emplace_back()
            spawner.type = SpawnerType.Sphere
            spawner.position = origin + Eigen.Vector3f(1000.0f, 750.0f, 0.5f * size)
            spawner.color = viz.Color.yellow()
        }
    }

    void visualize(viz.Client& arviz)
    {
        layerSpawners = arviz.layer("Spawners")

        int index = 0
        for (Spawner& spawner: spawners)
        {
            spawner.visualize(index, layerSpawners)
            index += 1
        }

        layerObjects = arviz.layer("SpawnedObjects")
    }

    void handle(viz.InteractionFeedback const& interaction,
                viz.StagedCommit* stage)
    {
        Spawner* spawner = nullptr
        for (int i = 0 i < (int)spawners.size() ++i)
        {
            std.string name = "Spawner_" + std.to_string(i)
            if (interaction.element() == name)
            {
                spawner = &spawners[i]
            }
        }

        switch (interaction.type())
        {
        case viz.InteractionFeedbackType.Select:
        {
            # Create a spawned object
            spawnedObject.index = spawnedObjectCounter++
            spawnedObject.source = spawner
            spawnedObject.transform = Eigen.Matrix4f.Identity()
            spawnedObject.scale.setOnes()
        } break

        case viz.InteractionFeedbackType.Transform:
        {
            # Update state of spawned object
            spawnedObject.transform = interaction.transformation()
            spawnedObject.scale = interaction.scale()
            if (interaction.isTransformBegin() || interaction.isTransformDuring())
            {
                # Visualize all other objects except the currently spawned one
                layerObjects.clear()
                for (auto& object : objects)
                {
                    object.visualize(layerObjects)
                }
                stage.add(layerObjects)
            }
            if (interaction.isTransformEnd())
            {
                spawnedObject.visualize(layerObjects)
                stage.add(layerObjects)
            }
        } break

        case viz.InteractionFeedbackType.Deselect:
        {
            # Save state of spawned object
            objects.push_back(spawnedObject)
        } break

        case viz.InteractionFeedbackType.ContextMenuChosen:
        {
            SpawnerOption option = (SpawnerOption)(interaction.chosenContextMenuEntry())
            switch (option)
            {
            case SpawnerOption.DeleteAll:
            {
                objects.clear()
                layerObjects.clear()

                stage.add(layerObjects)
            } break
            case SpawnerOption.DeleteType:
            {
                auto newEnd = std.remove_if(objects.begin(), objects.end(),
                               [spawner](SpawnedObject const& obj)
                {
                   return obj.source == spawner
                })
                objects.erase(newEnd, objects.end())

                layerObjects.clear()
                for (auto& object : objects)
                {
                    object.visualize(layerObjects)
                }

                stage.add(layerObjects)
            } break
            }
        }

        default:
        {
            # Ignore other interaction types
        } break
        }
    }


}
"""


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

        """
        SpawnersState spawners(origin2)
        """

        sliders.visualize(self.arviz)
        stage.add([sliders.layer_interact, sliders.layer_result])

        """
        spawners.visualize(arviz)
        stage.add(spawners.layerSpawners)
        stage.add(spawners.layerObjects)
        """

        result = self.arviz.commit(stage)
        print(f"Initial commit at revision: {result.revision}")

        cycle_duration = 0.025  # s
        try:
            print("Press Ctrl+C to interrupt...")
            while True:
                cycle_start = time.time()

                result = self.arviz.commit(stage)

                # Reset the stage, so that it can be rebuild during the interaction handling
                stage.reset()

                stage.request_interaction(sliders.layer_interact)
                """
                stage.request_interaction(spawners.layerSpawners)
                """

                for interaction in result.interactions:
                    if interaction.layer == "Sliders":
                        print(f"Processing slider interactions ... (revision {result.revision})")
                        sliders.handle(interaction, stage)

                    """
                    if (interaction.layer() == "Spawners")
                        spawners.handle(interaction, &stage)
                    """

                cycle_remaining = cycle_duration - (time.time() - cycle_start)
                if cycle_remaining > 0:
                    time.sleep(cycle_remaining)

        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    example = ArVizInteractExample()
    example.run()
    print("Finished.")
