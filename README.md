# `elastix-py`
A Python wrapper for the Elastix image registration software package. This package allows you to call Elastix and Transformix from Python. 

### Installation

Using `pip`, you can install from this repository:

`pip install git+https://github.com/tueimage/elastix-py`

The package requires `numpy` and `SimpleITK`, which can be installed with `pip` as well:

```bash
pip install SimpleITK
pip install numpy
```

You will also need to install Elastix yourself from [http://elastix.lumc.nl/download.php](http://elastix.lumc.nl/download.php).

Set the `elastix_path` and `transformix_path` to the paths where you installed the binaries for `elastix` and `transformix` when using the `ElastixInterface` and `TransformixInterface` classes.
For windows, these paths need to point to the `.exe` files.

### Tutorial

A Python script that covers most the functionality is included in the [`example.py`](example.py) file.

### Minimal working example

```python
import elastix

el = elastix.ElastixInterface(elastix_path=ELASTIX_PATH)

el.register(
    fixed_image=fixed_image_path,
    moving_image=moving_image_path,
    parameters=[parameter_file_path],
    output_dir='results')

result_path = os.path.join('results', 'result.0.tiff')
```

Optional plotting:

```python
fixed_image = imageio.imread(fixed_image_path)[:, :, 0]
moving_image = imageio.imread(moving_image_path)[:, :, 0]
transformed_moving_image = imageio.imread(result_path)

fig, ax = plt.subplots(1, 4, figsize=(20, 5))
ax[0].imshow(fixed_image, cmap='gray')
ax[0].set_title('Fixed image')
ax[1].imshow(moving_image, cmap='gray')
ax[1].set_title('Moving image')
ax[2].imshow(transformed_moving_image, cmap='gray')
ax[2].set_title('Transformed\nmoving image')

plt.show()
```
