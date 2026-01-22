# 🫧 Featurescope: Image Feature Visualization

[![DOI](https://zenodo.org/badge/465379841.svg)](https://doi.org/10.5281/zenodo.18154793)

https://github.com/user-attachments/assets/d14add7f-7124-4bd7-b960-313e480738c3
> 👆🏼 Jellyfish dataset from [Kaggle](https://www.kaggle.com/datasets/anshtanwar/jellyfish-types); features extracted with [DinoV2](https://github.com/facebookresearch/dinov2) and projected using PCA. You can [download](https://github.com/MalloryWittwer/featurescope/releases) this example and try it yourself!

The **Featurescope** is a browser-based viewer that helps you understand how numerical features are distributed in a dataset of images.

- Upload images and features to [your browser's internal storage].
- Choose which features to plot in X and Y in the 2D canvas.
- Explore the data by zooming in an out and moving the canvas.

Image features can be measurements, embedding values, or other numerical outputs from image analysis algorithms.

> [!NOTE]
> Looking for the initial project, *Spheriscope*? You can find it on the [spheriscope](https://github.com/MalloryWittwer/spheriscope/tree/spheriscope) branch. However, we're not planning to develop this project further at the moment.

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

To open your images in the *Featurescope* viewer, you need to have formatted your dataset in a way that the viewer can understand. This involves saving the images in a local folder with the corresponding features in a file named `features.csv`.

### Overview

Saving images and features is done in Python via the *Featurizer* class, which you can import from `featurescope`:

```python
from featurescope import Featurizer
```

`Featurizer` provides four distinct methods to address different use cases. The method to use depends on whether are computing features on separate **images in a dataset** or on **objects in a labelled image**, and whether you want to **apply a featurizer function** or have **already computed a features dataframe**.


> To understand what we mean by an **image dataset**, a **featurizer** function, a **labelled image** or a **features dataframe**, see [Definitions]().

Identify which of the four method matches your use case:

| Features relate to **images in a dataset**: |  |
| -------- | ---------- |
| `Featurizer.apply_to_images()` | Apply a **featurizer** to all images in a **dataset** and save the results for visualization ([➡️ docs](#apply_to_images)). |
| `Featurizer.apply_from_images_df()` | Save a **features dataframe** matching images in a **dataset** for visualization ([➡️ docs](#apply_from_images_df)). |

| Features relate to **objects in a labelled image**: |  |
| -------- | ---------- |
| `Featurizer.apply_to_label_image()` | Apply a **featurizer** to objects in a **labelled image** and save the results for visualization ([➡️ docs](#apply_to_label_image)). |
| `Featurizer.apply_from_label_image_df()` | Save a **features dataframe** matching objects in a **labelled image** for visualization ([➡️ docs](#apply_from_label_image_df)). |

These methods are documented in more detail in [Featurizer methods]().

Applying any of the `Featurizer` methods will produce a local **folder containing image files** as well as a **CSV file** named `features.csv` containing the computed features.

```sh
images/
├── img1.png
├── img2.png
├── ...
├── features.csv  <- Contains the computed features
```

<!-- With that in hand, you can drag and drop this folder into the front-end application for visualization. -->

### Visualization

Once your images and `features.csv` are saved, you can visualize these data in the web application.

- In a web browser, navigate to https://mallorywittwer.github.io/featurescope/.
- Load the folder containing the images and the `features.csv` file by dropping it into the dedicated area.

That's it! You should be able to browse and visualize your images and features. 🎉

## Featurizer methods

### `apply_to_images`

Use this method if you have defined your own **featurizer** function in Python and want to apply it to all images in a folder. `apply_to_images` will load the images, run the featurizer, and save the results as a `features.csv`. 

**Example**

You have:

```sh
images/
├── img1.png
├── img2.png
├── ...
```

Then, do:

```python
from featurescope import Featurizer

# Define your featurizer
def minmax_featurizer(image: np.ndarray) -> Dict:
    image_min = image.min()
    image_max = image.max()
    return {
        "min": image_min,
        "max": image_max
    }

images_dir = "./images"  # Folder with images

# Apply the featurizer to all images in images_dir
csv_path = Featurizer.apply_to_images(images_dir, minmax_featurizer)

print(csv_path)  # CSV got saved in the images folder (./images/features.csv)
```

Result:

```sh
images/
├── img1.png
├── img2.png
├── ...
├── features.csv  <- Contains the computed features
```

### `apply_from_images_df`

Use this method if **you have already computed a features dataframe corresponding to images** and want to use the Featurescope to visualize these features.

The rows in your dataframe must be matched with images. We distinguish two situations here:

1. Match dataframe rows with image files via `filename_column`

You can pass a value for `filename_column` to specify a column in your dataframe that identifies images file names. The image files specified in `filename_column` must be found in `images_dir`.

**Example**

You have this `df`:

| image_file | feature_01 | feature_02 | ... |
| -------- | ---------- | ---------- | --- |
| 00.png | 1.2 | 4 | ... |
| 01.png | 1.9 | 3 | ... |
| 02.png | 2.3 | 0 | ... |

Then, do:

```python
from featurescope import Featurizer

df = (...)  # A features DataFrame with a column `image_file` containing image file names
images_dir = "./images"  # A folder containing these image files

csv_path = Featurizer.apply_from_images_df(df, images_dir, filename_column="image_file")
```

2. Store the image arrays in an `image_column`

You can pass a value for `image_column` to indicate that your images are stored as numpy arrays in the dataframe. In this case, `images_dir` refers to an **empty folder** where these images will be saved in PNG format.

**Example**

You have this `df`:

| image | feature_01 | feature_02 | ... |
| -------- | ---------- | ---------- | --- |
| np.ndarray([[0, 1, 2..]]) | 1.2 | 4 | ... |
| np.ndarray([[0, 1, 2..]]) | 1.9 | 3 | ... |
| np.ndarray([[0, 1, 2..]]) | 2.3 | 0 | ... |

Then, do:

```python
from featurescope import Featurizer

df = (...)  # A features DataFrame with a column `image` containing images as numpy arrays
images_dir = "./images"  # An empty folder where to save the images

csv_path = Featurizer.apply_from_images_df(df, images_dir, image_column="image")
```

In both cases, you should end up with a local folder containing the images and a `features.csv` file that you can use for visualization.

### `apply_to_label_image`

Use this method if you have a **labelled array** and a **featurizer function** to apply to the segmented objects. The featurizer can be applied either to the binary mask or to the intensity image under the mask of each object.

For convenience, `apply_to_label_image` can directly compute `properties` from scikit-images's [regionprops](https://scikit-image.org/docs/0.25.x/api/skimage.measure.html#skimage.measure.regionprops) function instead of (or in addition to) applying a custom-defined featurizer function.

**Example 1**: compute the *area* and *eccentricity* features from `regionprops`:

```python
from featurescope import Featurizer

label_image = (...) # A labelled array
images_dir = "./images"  # An empty folder where to save the results

csv_path = Featurizer.apply_to_label_image(
    images_dir, 
    label_image, 
    properties=["area", "eccentricity"],
)
```

**Example 2** with an *intensity image* and a *featurizer function*:

```python
from featurescope import Featurizer

def minmax_featurizer(image) -> Dict:
    (...)

label_image = (...) # A labelled array
images = (...) # An intensity image corresponding to the labelled array
images_dir = "./images"  # An empty folder where to save the results

csv_path = Featurizer.apply_to_label_image(
    images_dir, 
    label_image, 
    image=image,
    featurizer_funct=minmax_featurizer,
)
```

Both of these examples will save the computed features and images (crops around segmented objects) in the specified folder, which can be used for visualization with the Featurescope viewer.

### `apply_from_label_image_df`

Use this method if **you have already computed a features dataframe corresponding to objects in a labelled image** and want to visualize these features with the Featurescope.

The rows in your dataframe must be matched with label values in the labelled array via a `label` column.

If you pass an intensity image via the `image` parameter, the cropped regions of this image around the segmented objects will be used for visualization. Otherwise, a binary mask of the segmented objects in `label_image` will be used instead.

**Example**

You have this `df`:

| label | feature_01 | feature_02 | ... |
| -------- | ---------- | ---------- | --- |
| 1 | 1.2 | 4 | ... |
| 2 | 1.9 | 3 | ... |
| 3 | 2.3 | 0 | ... |

Then, do:

```python
from featurescope import Featurizer

df = (...)  # A features DataFrame with a column `label` identifying object labels
images_dir = "./images"  # An empty folder where to save the results
label_image = (...)  # A labelled array
image = (...)  # An intensity image

csv_path = Featurizer.apply_from_label_image_df(df, images_dir, label_image, image)
```

Running this code will save the image crops and a `features.csv` file in the specified folder, so you can use this folder for visualization with the Featurescope viewer.

## FAQ

### Does the data remain local?

Yes! Your images **remain local** (they are *not* uploaded to a remote server) even if you access the front-end app via a public URL. Your images and features are simply uploaded to your web browser's internal storage. If you reload the page, everything will be cleaned up and reset!

## License

This software is distributed under the terms of the [BSD-3](http://opensource.org/licenses/BSD-3-Clause) license.

## Issues

If you encounter any problems, please file an issue along with a detailed description.
