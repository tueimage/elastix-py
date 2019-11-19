# elastix-py
A Python wrapper for the Elastix image registration software package. This package allows you to call Elastix and Transformix from Python. 

### Installation

Using `pip`, you can install from this repository:

`pip install git+https://github.com/tueimage/elastix-py`

The package requires `numpy` and `SimpleITK`, which can be installed with `pip` as well:

`pip install SimpleITK`
`pip install numpy`

### Tutorial

A Python script that covers most the functionality is included in the [`example.py`](example.py) file.

### Using the 3D image viewer

```python
import numpy as np
import matplotlib.pyplot as plt
image = sitk.GetArrayFromImage(sitk.ReadImage('/Users/Koen/repos/essential-skills/example_data/chest_ct.mhd'))
for i in range(len(image)):
    image[i, i, i] = 0
fig, ax = plt.subplots()
Slicer(image).plot(ax)
plt.show()
```
