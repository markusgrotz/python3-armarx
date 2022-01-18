#!/usr/bin/env python3

from typing import Optional

import numpy as np
import transforms3d as tf3d

import armarx
import armarx.arviz as viz


class SingleSlider:

    def __init__(self, name: str, color):
        self.box = viz.Box(name)
        self.color = color

        self.initial = np.zeros(3, float)
        self.translation = np.zeros(3, float)


class SliderState:

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
        self.x.box.enable_interaction(translation="x", hide_during_transform=True)

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
        interaction.element
        transform = interaction.transformation
        translation = transform.position


        """
        SingleSlider* slider = nullptr
        if (element == "BoxX")
        {
            slider = &x
        }
        else if (element == "BoxY")
        {
            slider = &y
        }
        else if (element == "BoxZ")
        {
            slider = &z
        }
        else
        {
            ARMARX_WARNING << "Unknown interaction: " << element
            return
        }

        switch (interaction.type())
        {
        case viz.InteractionFeedbackType.Transform:
        {
            slider->translation = translation

            Eigen.Vector3f spherePosition(
                        x.initial.x() + x.translation.x(),
                        y.initial.y() + y.translation.y(),
                        z.initial.z() + z.translation.z())
            sphere.position(spherePosition)

            stage->add(layerResult)
        } break

        case viz.InteractionFeedbackType.Select:
        {
            // Do nothing
        } break

        case viz.InteractionFeedbackType.Deselect:
        {
            // If an object is deselected, we apply the transformation
            slider->initial = slider->initial + slider->translation
            slider->translation = Eigen.Vector3f.Zero()
            ARMARX_IMPORTANT << "Setting position to "
                             << slider->initial.transpose()
            slider->box.position(slider->initial)

            stage->add(layerInteract)
        } break

        default:
        {
            // Do nothing for the other interaction types
        } break
        }
        """

"""
struct SlidersState
{
    void handle(viz.InteractionFeedback const& interaction,
                viz.StagedCommit* stage)
    {
        

    }

    Eigen.Vector3f origin
    SingleSlider x
    SingleSlider y
    SingleSlider z

    viz.Sphere sphere

    viz.Layer layerInteract
    viz.Layer layerResult
}


enum class SpawnerType
{
    Box,
    Cylinder,
    Sphere,
}

enum class SpawnerOption
{
    DeleteAll = 0,
    DeleteType = 1,
}

struct Spawner
{
    SpawnerType type = SpawnerType.Box

    Eigen.Vector3f position = Eigen.Vector3f.Zero()
    float size = 100.0f
    viz.Color color = viz.Color.black()

    void visualize(int i, viz.Layer& layer)
    {
        viz.InteractionDescription interaction = viz.interaction()
                                                  .selection().transform().scaling()
                                                  .contextMenu({"Delete All", "Delete All of Type"})
        std.string name = "Spawner_" + std.to_string(i)
        switch (type)
        {
        case SpawnerType.Box:
        {
            viz.Box box = viz.Box(name)
                           .position(position)
                           .size(size)
                           .color(color)
                           .enable(interaction)
            layer.add(box)
        } break
        case SpawnerType.Cylinder:
        {
            viz.Cylinder cylinder = viz.Cylinder(name)
                                     .position(position)
                                     .radius(size*0.5f)
                                     .height(size)
                                     .color(color)
                                     .enable(interaction)
            layer.add(cylinder)
        } break
        case SpawnerType.Sphere:
        {
            viz.Sphere sphere = viz.Sphere(name)
                                 .position(position)
                                 .radius(size*0.5f)
                                 .color(color)
                                 .enable(interaction)
            layer.add(sphere)
        } break
        }
    }
}

struct SpawnedObject
{
    int index = 0
    Spawner* source = nullptr
    Eigen.Matrix4f transform = Eigen.Matrix4f.Identity()
    Eigen.Vector3f scale = Eigen.Vector3f.Ones()

    void visualize(viz.Layer& layer)
    {
        viz.InteractionDescription interaction = viz.interaction().none()
        std.string name = "Object_" + std.to_string(index)

        Eigen.Matrix4f initial = Eigen.Matrix4f.Identity()
        initial.block<3, 1>(0, 3) = source->position
        Eigen.Matrix4f pose = transform * initial

        switch (source->type)
        {
        case SpawnerType.Box:
        {
            viz.Box box = viz.Box(name)
                           .pose(pose)
                           .scale(scale)
                           .size(source->size)
                           .color(source->color)
                           .enable(interaction)
            layer.add(box)
        } break
        case SpawnerType.Cylinder:
        {
            viz.Cylinder cylinder = viz.Cylinder(name)
                                     .pose(pose)
                                     .scale(scale)
                                     .radius(source->size * 0.5f)
                                     .height(source->size)
                                     .color(source->color)
                                     .enable(interaction)
            layer.add(cylinder)
        } break
        case SpawnerType.Sphere:
        {
            viz.Sphere sphere = viz.Sphere(name)
                                 .pose(pose)
                                 .scale(scale)
                                 .radius(source->size * 0.5f)
                                 .color(source->color)
                                 .enable(interaction)
            layer.add(sphere)
        } break
        }
    }
}

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
            // Create a spawned object
            spawnedObject.index = spawnedObjectCounter++
            spawnedObject.source = spawner
            spawnedObject.transform = Eigen.Matrix4f.Identity()
            spawnedObject.scale.setOnes()
        } break

        case viz.InteractionFeedbackType.Transform:
        {
            // Update state of spawned object
            spawnedObject.transform = interaction.transformation()
            spawnedObject.scale = interaction.scale()
            if (interaction.isTransformBegin() || interaction.isTransformDuring())
            {
                // Visualize all other objects except the currently spawned one
                layerObjects.clear()
                for (auto& object : objects)
                {
                    object.visualize(layerObjects)
                }
                stage->add(layerObjects)
            }
            if (interaction.isTransformEnd())
            {
                spawnedObject.visualize(layerObjects)
                stage->add(layerObjects)
            }
        } break

        case viz.InteractionFeedbackType.Deselect:
        {
            // Save state of spawned object
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

                stage->add(layerObjects)
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

                stage->add(layerObjects)
            } break
            }
        }

        default:
        {
            // Ignore other interaction types
        } break
        }
    }

    Eigen.Vector3f origin

    std.vector<Spawner> spawners
    SpawnedObject spawnedObject
    int spawnedObjectCounter = 0
    std.vector<SpawnedObject> objects

    viz.Layer layerSpawners
    viz.Layer layerObjects
}

/**
 * @defgroup Component-ArVizInteractExample ArVizInteractExample
 * @ingroup RobotAPI-Components
 *
 * An example for how to visualize 3D elements via the 3D visualization
 * framework ArViz.
 *
 * The example creates several layers, fills them with visualization
 * elements, and commits them to ArViz.
 *
 * To see the result:
 * \li Start the component `ArVizStorage`
 * \li Open the gui plugin `ArViz`
 * \li Start the component `ArVizInteractExample`
 *
 * The scenario `ArVizInteractExample` starts the necessary components,
 * including the example component.
 *
 *
 * A component which wants to visualize data via ArViz should:
 * \li `#include <RobotAPI/libraries/RobotAPIComponentPlugins/ArVizComponentPlugin.h>`
 * \li Inherit from the `armarx.ArVizComponentPluginUser`. This adds the
 *     necessary properties (e.g. the topic name) and provides a
 *     ready-to-use ArViz client called `arviz`.
 * \li Use the inherited ArViz client variable `arviz` of type `viz.Client`
 *     to create layers, add visualization elements to the layers,
 *     and commit the layers to the ArViz topic.
 *
 * \see ArVizInteractExample
 *
 *
 * @class ArVizInteractExample
 * @ingroup Component-ArVizInteractExample
 *
 * @brief An example for how to use ArViz.
 *
 * @see @ref Component-ArVizInteractExample
 */
struct ArVizInteractExample :
    virtual armarx.Component,
    // Deriving from armarx.ArVizComponentPluginUser adds necessary properties
    // and provides a ready-to-use ArViz client called `arviz`.
    virtual armarx.ArVizComponentPluginUser
{
    std.string getDefaultName() const override
    {
        return "ArVizInteractExample"
    }

    armarx.PropertyDefinitionsPtr createPropertyDefinitions() override
    {
        armarx.PropertyDefinitionsPtr defs(new ComponentPropertyDefinitions(getConfigIdentifier()))
        return defs
    }

    void onInitComponent() override
    { }

    void onConnectComponent() override
    {
        task = new RunningTask<ArVizInteractExample>(this, &ArVizInteractExample.run)
        task->start()
    }

    void onDisconnectComponent() override
    {
        const bool join = true
        task->stop(join)
        task = nullptr
    }

    void onExitComponent() override
    { }


    void run()
    {
        viz.StagedCommit stage

        viz.Layer regions = arviz.layer("Regions")
        Eigen.Vector3f origin1(-2000.0f, 0.0f, 0.0f)
        Eigen.Vector3f origin2(0.0f, 0.0f, 0.0f)
        Eigen.Vector3f origin3(-2000.0f, -2000.0f, 0.0f)
        Eigen.Vector3f origin4(0.0f, -2000.0f, 0.0f)
        {
            viz.Cylinder separatorX = viz.Cylinder("SeparatorX")
                                       .fromTo(origin1, origin1 + 4000.0f * Eigen.Vector3f.UnitX())
                                       .radius(5.0f)
            regions.add(separatorX)

            viz.Cylinder separatorY = viz.Cylinder("SeparatorY")
                                       .fromTo(origin4, origin4 + 4000.0f * Eigen.Vector3f.UnitY())
                                       .radius(5.0f)
            regions.add(separatorY)

            stage.add(regions)
        }


        SlidersState sliders(origin1 + Eigen.Vector3f(500.0f, 500.0f, 0.0f))
        SpawnersState spawners(origin2)

        sliders.visualize(arviz)
        stage.add(sliders.layerInteract)
        stage.add(sliders.layerResult)

        spawners.visualize(arviz)
        stage.add(spawners.layerSpawners)
        stage.add(spawners.layerObjects)

        viz.CommitResult result = arviz.commit(stage)
        ARMARX_INFO << "Initial commit at revision: " << result.revision()

        CycleUtil c(25.0f)
        while (!task->isStopped())
        {
            result = arviz.commit(stage)

            // Reset the stage, so that it can be rebuild during the interaction handling
            stage.reset()

            stage.requestInteraction(sliders.layerInteract)
            stage.requestInteraction(spawners.layerSpawners)

            viz.InteractionFeedbackRange interactions = result.interactions()
            for (viz.InteractionFeedback const& interaction : interactions)
            {
                if (interaction.layer() == "Sliders")
                {
                    sliders.handle(interaction, &stage)
                }
                if (interaction.layer() == "Spawners")
                {
                    spawners.handle(interaction, &stage)
                }
            }

            c.waitForCycleDuration()
        }
    }

    RunningTask<ArVizInteractExample>.pointer_type task

}

ARMARX_DECOUPLED_REGISTER_COMPONENT(ArVizInteractExample)


int main(int argc, char* argv[])
{
    return armarx.DecoupledMain(argc, argv)
}



"""