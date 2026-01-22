# Definitions

The main concepts related to the *Featurescope* are defined below.

## Image Dataset

> A local folder of images.

- The images should be in `PNG`, `JPEG` or `TIFF` format.
- They should be located in the same folder.

Example:

```
images/
├── img1.png
├── img2.png
├── ...
```

## Featurizer

> A Python function that computes features.

- The featurizer function must take an `image` NumPy array a its first input.
- The function must return a Python dictionary of numerical image features.

Example:

```python
def minmax_featurizer(image: np.ndarray) -> Dict:
    image_min = image.min()
    image_max = image.max()
    return {
        "min": image_min,
        "max": image_max
    }
```

## Labelled image

> A Numpy array of integers where the values represent object instances.

For example, the code below produces a labelled image:

```python
import skimage.data
from skimage.morphology import label

# A grayscale image with values in [0-255]
image = skimage.data.coins()

# A binary mask with values in [True, False]
binary = image > 100

# A labelled image with values [0, 1, 2... N] representing N objects
labelled = label(binary)
```

## Features DataFrame

> A Pandas DataFrame with columns representing features.

- The rows represent images or object instances on which the features are computed.
- Non-numeric features are ignored, and numeric features are normalized for visualization.
- You can include columns to identify image files, object labels, or similar.

Example:

| file_name | feature_01 | feature_02 | ... |
| -------- | ---------- | ---------- | --- |
| 00.png | 1.2 | 4 | ... |
| 01.png | 1.9 | 3 | ... |
| 02.png | 2.3 | 0 | ... |