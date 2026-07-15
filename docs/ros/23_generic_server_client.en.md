---
title: ROS 2 Generic Server and Client
---

# ROS 2 Generic Server and Client

!!! info "Preliminary version"
    This is a concise English version. See the Japanese page for the full detailed walkthrough.

## Learning Objectives

Serve and call **any** ROS 2 service type from Isaac Sim. List services with `ros2 interface list --only-srvs`; definitions live under `share/<pkg>/srv/<name>` with request and response sections.

## Generic Server

Two nodes: **ROS2 Service Server Request** (receives) and **ROS2 Service Server Response** (replies). Connect Request's **Server Handle** → Response's Server Handle (shared server) and Request's **On received** → Response's On received (reply only on request). Both nodes must be set to the same type (e.g. std_srvs / srv / SetBool); the Request node's *outputs* get the request fields, the Response node's *inputs* get the response fields. The Service Name is configurable.

![Server graph](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_server_1.PNG)

Test after Play:

```bash
ros2 service call /service_name std_srvs/srv/SetBool "{data: true}"
```

## Generic Client

A single **ROS2 Service Client** node — inputs are the request fields, outputs the response fields. After Play it issues requests per its inputs. Combining server and client in one graph lets you exercise the round trip entirely inside OmniGraph.

![Server + client](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/_images/tutorial_ros2_server_client_1.PNG)

## Next Steps

- [Tutorial 24: ROS 2 Service for Manipulating Prims Attributes](24_prim_service.md)
