# FeatureScope (Python package)

This package provides a function `apply_featurizer` to compute custom features on images contained in a folder, so that these images and features can be visualized with the featurescope.

**Example**

We have a local folder of images:

```
/mnist
   01.png
   02.png
   ...
```

and a featurizer function in Python:

```python
def mnist_featurizer(image: np.ndarray) -> Dict:
    return {
        "mean": np.mean(image),
        "max": np.max(image),
        "min": np.min(image),
    }
```

then, we can use:

```python
from featurescope import apply_featurizer

apply_featurizer(mnist_featurizer, images_dir="./mnist")
```

Running `apply_featurizer` will load, and apply the featurizer function to all images in the folder, and save a CSV file `dataset.csv` in that same folder.

```
/mnist
   01.png
   02.png
   ...
   dataset.csv  <- Contains the computed image features!
```

With the features computed and stored, the folder `/mnist` can be dropped in the [featurescope app](https://mallorywittwer.github.io/featurescope/) in a web browser for visualization.

## Installation

From PyPi:

```bash
pip install featurescope
```