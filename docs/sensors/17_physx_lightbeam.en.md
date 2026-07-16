---
title: PhysX SDK Lightbeam Sensor
---

# PhysX SDK Lightbeam Sensor

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

The PhysX SDK Lightbeam sensor uses PhysX raycasts to detect whether an object has intersected a light beam. Specify the number of rays and height to build a safety light "curtain".

## Usage

Run `Robotics Examples > Sensors > Lightbeam` (activate via `Windows > Examples > Robotics Examples`). Press PLAY to populate the per-beam data — whether each beam was hit, the linear depth of the hit, and the exact xyz hit position. `SHIFT + LEFT_CLICK` to drag the cube or sensor and watch the readings change.
