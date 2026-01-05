# 🫧 FeatureScope: Image Feature Visualization

[![DOI](https://zenodo.org/badge/465379841.svg)](https://doi.org/10.5281/zenodo.18154793)

https://github.com/user-attachments/assets/d14add7f-7124-4bd7-b960-313e480738c3
> 👆🏼 Jellyfish dataset from [Kaggle](https://www.kaggle.com/datasets/anshtanwar/jellyfish-types); features extracted with [DinoV2](https://github.com/facebookresearch/dinov2) and projected using PCA. You can [download](https://github.com/MalloryWittwer/featurescope/releases) this example and try it yourself!

The **FeatureScope** helps you understand how numerical features are distributed in an image dataset.

- Choose which features to plot in X and Y in the 2D interactive plane.
- Explore the data interactively by zooming in an out and viewing images.

Image features can be any numerical values associated with images, such as measurements, embedding values, or numerical outputs from image analysis algorithms.

All data remains local. The images are only uploaded to your web browser's internal storage.

> [!NOTE]
> Looking for the initial project, *Spheriscope*? You can find it on the [spheriscope](https://github.com/MalloryWittwer/spheriscope/tree/spheriscope) branch. However, we're not planning to develop this project further at the moment as we think the *featurescope* is applicable more broadly and easier to use.

## Installation

You can install the `featurescope` Python package using `pip`:

```sh
pip install featurescope
```

or clone this repository and install the development version:

```sh
git clone https://github.com/MalloryWittwer/featurescope.git
cd featurescope
pip install -e python
```

## Usage

### Image Dataset

- Your images should be in `PNG`, `JPEG` or `TIFF` format.
- They should be located in the same folder.

For example:

```
images/
├── img1.png
├── img2.png
├── ...
```

### Featurizer

You should define a **featurizer** function in Python. This function will be applied to all images in the dataset in order to extract the features.

**Constraints**

- The featurizer function must take an `image` NumPy array a its first input.
- The function must return a Python dictionary of numerical image features. 

For example:

```python
def minmax_featurizer(image: np.ndarray) -> Dict:
    image_min = image.max()
    image_max = image.max()
    return {
        "min": image_min,
        "max": image_max
    }
```

### Computing Features

Use `apply_featurizer` to compute the features for all images in your dataset. The results are aggregated and saved as a CSV file named `dataset.csv` in the images folder.

```python
from featurescope import apply_featurizer

apply_featurizer(minmax_featurizer, images_dir="/path/to/images")
```

Running `apply_featurizer` will loop over all image files in `images_dir` to load the images and compute the features. At the end of the process, the results are saved as `dataset.csv`:

```
images/
├── img1.png
├── img2.png
├── ...
├── dataset.csv  <- Contains the computed features
```

### Visualization

With your `dataset.csv` in the images folder, you can now drag and drop this folder into the front-end app for visualization.

- In a web browser, navigate to https://mallorywittwer.github.io/featurescope/.
- Load the folder containing the images and the `dataset.csv` file by dropping it into the drag-and-drop area.

That's it! You should now be able to browse and visualize your images and features. 🎉

### Does the data remain local?

Yes! Your images **remain local** (they are *not* uploaded to a remote server) even if you access the front-end app via a public URL. Your images and features are simply uploaded to your web browser's internal storage. If you reload the page, everything should be cleaned up and reset!

## License

This software is distributed under the terms of the [BSD-3](http://opensource.org/licenses/BSD-3-Clause) license.

## Issues

If you encounter any problems, please file an issue along with a detailed description.
