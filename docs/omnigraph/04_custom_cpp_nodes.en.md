---
title: Custom C++ Nodes
---

# Custom C++ Nodes

!!! info "Preliminary version"
    This English page is a preliminary summary. The Japanese page is the primary, fully detailed document — see it for the complete walkthrough.

## Overview

For C++ nodes, the Node Definition (`.ogn`) is the same as for [Custom Python Nodes](03_custom_python_nodes.md); only the implementation is C++. Examples of including OmniGraph nodes are in the extension template's GitHub repo.

To use custom C++ nodes you must **build** your custom C++ extension — follow the Kit C++ Extension Template instructions. Python nodes need no build (good for prototyping); C++ nodes require a build but offer performance benefits for compute-heavy work.
