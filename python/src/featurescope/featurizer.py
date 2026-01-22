import io
import base64
import os
from pathlib import Path
from typing import Callable, List, Optional, Union

import numpy as np
import pandas as pd
from PIL import Image, ImageOps
from tqdm import tqdm
from skimage.measure import regionprops_table


THUMBNAIL_SIZE = int(os.getenv("THUMBNAIL_SIZE", 64))

VALID_IMAGE_FORMATS = ["tif", "tiff", "png", "jpeg", "jpg"]


def _load_image(image_file: Union[Path, str]) -> Image.Image:
    """Load an image using Pillow."""
    image_path = Path(image_file)
    if not image_path.exists():
        raise FileNotFoundError(f"Image file does not exist: {image_path}")
    try:
        pil_image = Image.open(image_path)
    except Exception as e:
        raise OSError(f"Could not read image file {image_path}: {e}") from e

    return pil_image


def _letterbox_resize(pil_image: Image.Image) -> Image.Image:
    """Resize a PIL image to a square thumbnail in letterbox style (with black margins)."""
    pil_image = pil_image.convert("RGB")
    thumbnail = ImageOps.pad(
        pil_image,
        size=(THUMBNAIL_SIZE, THUMBNAIL_SIZE),
        method=Image.Resampling.LANCZOS,
        color=(0, 0, 0),
        centering=(0.5, 0.5),
    )

    return thumbnail


def _encode_thumbnail(pil_image: Image.Image) -> str:
    """Compute an image thumbnail (preserve aspect ratio) and encode it to bytes for saving in a dataframe."""
    thumbnail = _letterbox_resize(pil_image)
    # Encode the thumbnail and store it in the CSV
    output = io.BytesIO()
    thumbnail.save(output, format="png")
    thumbnail_data = output.getvalue()
    encoded_thumbnail = base64.b64encode(thumbnail_data).decode("utf-8")

    return encoded_thumbnail


def _normalize_numeric_columns(
    df: pd.DataFrame, margin_rel: float = 0.2
) -> pd.DataFrame:
    """Rescale the values of the numeric columns of a DataFrame to the relative range at which they should be displayed in fraction of the width or height of the canvas.
    We use a min-max normalization and reduce the range of output values by a small margin. The effective output range is given by [margin_rel/2, 1-margin_rel/2].
    The output range determines how spread out data points are along the width/height of the canvas in the web app.
    """
    df_normed = df.copy()

    # Select only numeric columns to normalize
    numeric_cols = df_normed.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0:
        return df_normed

    mins = df_normed[numeric_cols].min()
    maxs = df_normed[numeric_cols].max()
    ranges = maxs - mins

    # to avoid division by zero:
    ranges = ranges.replace(0, 1)

    df_normed[numeric_cols] = (df_normed[numeric_cols] - mins) / ranges

    # Extra relative "margin"
    df_normed[numeric_cols] = df_normed[numeric_cols] * (1 - margin_rel)
    df_normed[numeric_cols] = df_normed[numeric_cols] + (margin_rel / 2)

    # Add the image ID
    df_normed["id"] = df_normed.index

    # Keep only numeric columns + thumbnail and image_file columns
    numeric_cols = df_normed.select_dtypes(include=[np.number]).columns
    df_normed_numeric = df_normed[numeric_cols].copy()
    df_normed_numeric["thumbnail"] = df_normed["thumbnail"]
    df_normed_numeric["image_file"] = df_normed["image_file"]

    return df_normed_numeric


def _save_csv(df: pd.DataFrame, images_path: Path) -> Path:
    """Save the features dataframe as a CSV file."""
    csv_path = images_path / "features.csv"
    df.to_csv(csv_path)
    print(f"✅ Saved: {csv_path.resolve()}")
    return csv_path


def _setup_images_path(
    images_dir: Union[Path, str],
    ensure_empty: bool = False,
    ensure_exists: bool = False,
) -> Path:
    images_path = Path(images_dir)
    if not images_path.exists():
        if ensure_exists:
            raise RuntimeError(f"Images directory does not exist: {images_path}")
        os.mkdir(images_path)
        print(f"ℹ️ Created: {images_path}")
    if ensure_empty:
        existing_image_files = []
        for ext in VALID_IMAGE_FORMATS:
            existing_image_files.extend(images_path.glob(f"*.{ext}"))
        if len(existing_image_files) > 0:
            raise RuntimeError(f"Images directory is not empty! ({images_path}).")
    return images_path


def _get_image_files(images_path: Path) -> List[Path]:
    image_files = []
    for ext in VALID_IMAGE_FORMATS:
        image_files.extend(images_path.glob(f"*.{ext}"))
    return image_files


def apply_to_images(
    images_dir: Union[Path, str],
    featurizer_func: Callable,
    **featurizer_kwargs,
) -> Optional[Path]:
    """
    Use this method if you have defined your own featurizer function and want to apply it to all images in a folder. This function will load the images, run the featurizer, and save the results as a features.csv.
    
    The featurizer function must have the following signature:
        1. It must take an `image` NumPy array as input (and possibly other arguments). The image array should be readable from a file by Pillow's Image.open function.
        2. It must return a Python dictionary of numeric image features for the image.

    Example featurizer function:
    ============================

    def minmax_featurizer(image: np.ndarray) -> Dict:
        image_mean = np.mean(image)
        image_max = image.max()
        return {
            "mean": image_mean,
            "max": image_max
        }

    Parameters
    ==========
    - images_dir: A path to a directory of 2D images (the images must be readable by Pillow's Image.open function).
    - featurizer_func: Featurizer function to apply to each image in images_dir.
    - **featurizer_kwargs: Extra keyword arguments to pass to the featurizer function, apart from "image".

    Returns
    ==========
    - The path to the saved CSV file.
    """
    images_path = _setup_images_path(images_dir)

    image_files = _get_image_files(images_path)
    if len(image_files) == 0:
        print(f"⚠️ No images files in this directory: {images_path}.")
        return

    # Run the featurizer on all image files
    df = pd.DataFrame({"image_file": image_files})
    records = []
    for image_file in tqdm(
        image_files, total=len(image_files), desc="Applying featurizer"
    ):
        pil_image = _load_image(image_file)
        image_arr = np.asarray(pil_image)
        measurements = featurizer_func(image_arr, **featurizer_kwargs)
        measurements["thumbnail"] = _encode_thumbnail(pil_image)
        records.append(measurements)

    for key in list(records[0].keys()):
        df[key] = [record[key] for record in records]

    # Normalize and save dataframe
    df_normed = _normalize_numeric_columns(df)
    return _save_csv(df_normed, images_path)

def apply_to_label_image(
    images_dir: Union[Path, str],
    label_image: np.ndarray,
    image: Optional[np.ndarray] = None,
    properties: Optional[List[str]] = None,
    featurizer_func: Optional[Callable] = None,
    **featurizer_kwargs,
) -> Path:
    """
    Use this method if you have a labelled array and a featurizer function to apply to the segmented objects. The featurizer can be applied either to the binary mask or to the intensity image under the mask of each object.
    
    Parameters
    ==========
    - images_dir: A path to an empty directory where to save the results.
    - label_image: A labelled segmentation mask as a NumPy array.
    - image: An intensity image. If None, the label_image will be used.
    - properties: A list of regionprops properties to compute on each `image_intensity` object.
    - featurizer_func: Featurizer function to apply to each `image_intensity` object.
    - **featurizer_kwargs: Extra keyword arguments to pass to the featurizer function, apart from `image`.

    Returns
    ==========
    - The path to the saved CSV file.
    """
    images_path = _setup_images_path(images_dir, ensure_empty=True)

    # Make sure `label` and `image_intensity` are among the properties
    if properties is None:
        properties_ = ["label", "image_intensity"]
    else:
        properties_ = properties
        if "label" not in properties:
            properties_.append("label")
        if "image_intensity" not in properties:
            properties_.append("image_intensity")

    image_ = (label_image > 0).astype(np.uint8) * 255 if image is None else image

    # Compute regionprops
    df = pd.DataFrame(
        regionprops_table(
            label_image,
            intensity_image=image_,
            properties=properties_,
        )
    )

    # Apply the featurizer function
    records = []
    for idx, image_roi in enumerate(df["image_intensity"].values):
        pil_image = Image.fromarray(image_roi)
        image_arr = np.asarray(pil_image)
        image_file = images_path / f"{idx:03d}.png"
        pil_image.save(image_file)
        measurements = {}
        if featurizer_func:
            measurements = measurements | featurizer_func(
                image_arr, **featurizer_kwargs
            )
        measurements["thumbnail"] = _encode_thumbnail(pil_image)
        measurements["image_file"] = image_file
        records.append(measurements)

    for key in list(records[0].keys()):
        df[key] = [record[key] for record in records]

    # Normalize and save dataframe
    df_normed = _normalize_numeric_columns(df)
    return _save_csv(df_normed, images_path)

def apply_from_images_df(
    df: pd.DataFrame,
    images_dir: Union[Path, str],
    filename_column: Optional[str] = None,
    image_column: Optional[str] = None,
) -> Path:
    """
    Use this method if you have already computed a features dataframe corresponding to images and want to use the Featurescope to visualize these features.
    
    The rows in your dataframe must be matched with images, either via `filename_column` or via `image_column`.

    Parameters
    ==========
    - df: a Pandas DataFrame containing features.
    - images_dir: A path to either
        1. When using `filename_column`, an folder of images with file names matching those in the DataFrame.
        2. When using `image_column`, an empty folder where to save the results.
    - filename_column: A column of file names corresponding to the images in `images_dir`.
    - image_column: A column of NumPy arrays representing the images.

    Returns
    ==========
    - The path to the saved CSV file.
    """
    images_path = _setup_images_path(images_dir)

    image_files = _get_image_files(images_path)

    if len(image_files) > 0:
        print(
            "ℹ️ `images_dir` is not empty. We assume it contains images to be matched with `filename_column`."
        )
        if filename_column:
            if image_column:
                print(
                    "⚠️ The provided `image_column` will be ignored because a `filename_column` was passed."
                )
            image_paths = []
            for file_name in df[filename_column].values:
                file_path = images_path / file_name
                if not file_path in image_files:
                    raise RuntimeError(
                        f"{file_path.name} is not in the images directory ({images_path})."
                    )
                image_paths.append(file_path)
            df["image_file"] = image_paths
            pil_images: List[Image.Image] = [_load_image(f) for f in image_paths]
        else:
            raise RuntimeError(
                f"A `filename_column` is needed to match image files in the images directory ({images_path})"
            )
    else:
        print(
            "ℹ️ `images_dir` is empty. The images contained in `image_column` will be saved in it."
        )
        if image_column is None:
            raise RuntimeError(
                f"A `image_column` containing NumPy arrays is needed to save these images in the output directory ({images_path})."
            )
        if filename_column:
            print(
                "⚠️ The provided `filename_column` will be ignored because an `image_column` was passed."
            )

        n_files = len(df[image_column].values)
        df["image_file"] = [
            str((images_path / f"{idx:03d}.png").resolve())
            for idx in range(n_files)
        ]
        pil_images: List[Image.Image] = [
            Image.fromarray(arr) for arr in df[image_column].values
        ]
        for pil_image, image_file in zip(pil_images, df["image_file"].values):
            pil_image.save(image_file)

    # We now have image_path values
    df["thumbnail"] = [_encode_thumbnail(pil_image) for pil_image in pil_images]
    df_normed = _normalize_numeric_columns(df)
    return _save_csv(df_normed, images_path)

def apply_from_label_image_df(
    df: pd.DataFrame,
    images_dir: Union[Path, str],
    label_image: np.ndarray,
    image: Optional[np.ndarray] = None,
) -> Path:
    """
    Use this method if you have already computed a features DataFrame corresponding to objects in a labelled image and want to visualize these features with the Featurescope.
    
    The rows in your DataFrame must be matched with label values in the labelled array via a label column.
    
    Parameters
    ==========
    - df: a Pandas DataFrame containing features.
    - images_dir: A path to an empty directory where to save the results.
    - label_image: A labelled segmentation mask as a NumPy array.
    - image: An intensity image as a NumPy array. If passed, the cropped image regions around the segmented objects will be used for visualization If None, a binary mask of the segmented objects in label_image will be used.

    Returns
    ==========
    - The path to the saved CSV file.
    """
    images_path = _setup_images_path(images_dir, ensure_empty=True)

    # Make sure df has a `label` column that matches the labels in label_image
    # Make sure `label` and `image_intensity` are among the properties
    if "label" not in df.columns:
        raise RuntimeError("DataFrame should have a `label` column.")
    else:
        uniques = np.unique(label_image)
        uniques = uniques[uniques != 0].tolist()
        label_values: np.ndarray = df["label"].values
        uniques_df = np.unique(label_values)
        uniques_df = uniques_df[uniques_df != 0].tolist()
        if len(uniques) != len(uniques_df):
            raise RuntimeError(
                "Labels in dataframe don't match labels in `label_image`."
            )
        for v in df["label"].values:
            if v not in uniques:
                raise RuntimeError(
                    "Labels in dataframe don't match labels in `label_image`."
                )

    # Add `image_intensity` if it's not already there
    if "image_intensity" not in df.columns:
        image_ = (
            (label_image > 0).astype(np.uint8) * 255 if image is None else image
        )
        df_ = pd.DataFrame(
            regionprops_table(
                label_image,
                intensity_image=image_,
                properties=["label", "image_intensity"],
            )
        )
        df = df.merge(df_, on="label")

    # Save the images, compute thumbnails
    image_files = []
    encoded_thumbnails = []
    for idx, image_intensity in enumerate(df["image_intensity"].values):
        pil_image = Image.fromarray(image_intensity)
        image_file = images_path / f"{idx:03d}.png"
        pil_image.save(image_file)
        encoded_thumbnails.append(_encode_thumbnail(pil_image))
        image_files.append(image_file)
    # Add an encoded thumbnail and image_path to the dataframe.
    df["thumbnail"] = encoded_thumbnails
    df["image_file"] = image_files

    # Normalize and save dataframe
    df_normed = _normalize_numeric_columns(df)
    return _save_csv(df_normed, images_path)
