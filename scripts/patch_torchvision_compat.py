"""Compatibility shim: torchvision >= 0.27 renamed transforms.functional_tensor
to transforms._functional_tensor. basicsr/realesrgan/gfpgan still import the old
path, so re-export the private module under the legacy name.

Installed into the venv site-packages by scripts/patch_torchvision_compat.py.
"""

from torchvision.transforms._functional_tensor import *  # noqa: F401,F403
