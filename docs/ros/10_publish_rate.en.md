---
title: ROS2 Setting Publish Rates
---

# ROS2 Setting Publish Rates

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Set the simulation frame rate and give different ROS 2 publishers different publish rates. Action Graphs tick every simulation frame, so publisher rates are integer divisions of the simulation rate.

## Isaac Simulation Gate

In `turtlebot_tutorial.usd`, create an IMU sensor under `/World/turtlebot3_burger/base_link/imu_link`, build an IMU graph with an **Isaac Simulation Gate** (step = 2 → publish every other frame), **Isaac Read IMU Node** (imuPrim = the sensor), and **ROS2 Publish Imu** (frameId `imu_link`).

## Rates Within the SDG Pipeline

For Camera/RTX Lidar helpers, set the **frameSkipCount** on each helper node — skipping N frames publishes every N+1 frames (the internal Simulation Gate step is set automatically). Example: LaserScan helper frameSkipCount 11 (≈5 Hz at 60 FPS), RGB camera helper 3 (≈15 Hz), camera info helper 5 (≈10 Hz); disable unneeded helpers/render products via their `enabled` attribute.

## Setting Simulation Frame Rates

Two Script Editor approaches (both set the *target* rate; actual FPS depends on the machine):

```python
# carb settings (affects OnPlaybackTick; not persistent across stop/play)
import carb
physics_rate = 60
carb.settings.get_settings().set_bool("/app/runLoops/main/rateLimitEnabled", True)
carb.settings.get_settings().set_int("/app/runLoops/main/rateLimitFrequency", int(physics_rate))
carb.settings.get_settings().set_int("/persistent/simulation/minFrameRate", int(physics_rate))
```

```python
# TimeCodesPerSecond + target framerate (affects IsaacReadSimulationTime; persistent)
import omni
physics_rate = 60
timeline = omni.timeline.get_timeline_interface()
stage = omni.usd.get_context().get_stage()
timeline.stop()
stage.SetTimeCodesPerSecond(physics_rate)
timeline.set_target_framerate(physics_rate)
timeline.play()
```

TimeCodesPerSecond can only be set once before a scene is played — reload the scene to change it.

## Checking Rates

`ros2 topic hz /topic_name` — expected: `/clock` ~60 Hz, `/imu` ~30, `/scan` ~5, `/camera_1/rgb/image_raw` ~15, `.../camera_info` ~10. If images publish slowly, reduce the render product resolution. For troubleshooting, try `./isaac-sim.sh --reset-user` or the experimental `./isaac-sim.fabric.sh --reset-user`.

## Next Steps

- [Tutorial 11: ROS 2 Quality of Service (QoS)](11_qos.md)
