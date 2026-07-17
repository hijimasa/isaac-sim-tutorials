---
title: ROS2 Setting Publish Rates
---

# ROS2 Setting Publish Rates

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Set the simulation rate and give different sensor types (IMU, RTX Lidar, Camera) different ROS 2 publish rates. Non-RTX sensors are gated per frame with the Isaac Simulation Gate node; RTX sensors are scheduled via the `omni:sensor:tickRate` attribute on the sensor prim (multi-tick rendering).

## Non-RTX Sensors: Isaac Simulation Gate

In `turtlebot_tutorial.usd`, create an IMU sensor under `/World/turtlebot3_burger_processed/Geometry/base_footprint/base_link/imu_link` (right-click the prim > Create > Isaac > Sensors > Imu Sensor), build an IMU graph with an **Isaac Simulation Gate** (step = 2 → publish every other frame), **Isaac Read IMU Node** (imuPrim = the sensor), and **ROS2 Publish Imu** (frameId `imu_link`).

## RTX Sensors: omni:sensor:tickRate

The former **frameSkipCount** parameter on ROS2 helper nodes is now deprecated. Instead, set **`omni:sensor:tickRate`** on the sensor prim: on the 2D Lidar prim `Example_Rotary_2D` set it to 5 (and set `omni:sensor:Core:scanRateBaseHz` to 5 to match — the two must be equal), and on `/World/Camera_1` apply the `OmniSensorAPI` schema and set the tick rate to 15, e.g. from the Script Editor:

```python
import isaacsim.core.experimental.utils.prim as prim_utils

for path in ("/World/Camera_1", "/World/Camera_2"):
    camera_prim = prim_utils.get_prim_at_path(path)
    camera_prim.ApplyAPI("OmniSensorAPI")
    camera_prim.GetAttribute("omni:sensor:tickRate").Set(15)
```

Disable unneeded helpers/render products via their `enabled` attribute.

## Setting the Simulation Rate (Advanced)

Set the physics, timeline, and run-loop rates coherently with `SimulationManager.setup_simulation(dt=1.0 / target_hz)` plus `RenderingManager.set_dt(1.0 / target_hz)` in a standalone Python script (both set the *target* rate; actual FPS depends on the machine), then run it with:

```bash
./python.sh test_ros2_publish_rates.py \
--/app/runLoops/main/rateLimitEnabled=true \
--/app/runLoops/main/rateLimitFrequency=60 \
--/app/runLoops/main/manualModeEnabled=true
```

Note: Isaac Sim 6.0 has a known fatal crash in the full UI app when playing after changing these rates from their default of 60.0.

## Checking Rates

`ros2 topic hz /topic_name` — expected: `/clock` = target_hz (~60 Hz), `/imu` = target_hz/2 (~30), `/scan` = min(R_lidar, target_hz) = 5 Hz, `/camera_1/rgb/image_raw` and `.../camera_info` = min(R_cam, target_hz) = 15 Hz. OnPlaybackTick-driven topics scale with target_hz; multi-tick RTX sensors hold their configured Hz. If images publish slowly, reduce the render product resolution. For troubleshooting, try `./isaac-sim.sh --reset-user` or the experimental `./isaac-sim.fabric.sh --reset-user`.

## Next Steps

- [Tutorial 11: ROS 2 Quality of Service (QoS)](11_qos.md)
