import os
from pathlib import Path
from typing import Union
import pandas as pd
from PIL import Image

from featurescope.featurizer import Featurizer, encode_thumbnail

THUMBNAIL_SIZE = int(os.getenv("THUMBNAIL_SIZE", 64))


def apply_dataframe(df: pd.DataFrame, images_dir: Union[Path, str]):
    """
    Docstring for apply_from_dataframe

    :param df: Description
    :type df: pd.DataFrame
    :param images_dir: Description
    :type images_dir: Union[Path, str]
    """
    # Sanitize the dataframe
    if not "image_intensity" in df.columns:
        raise (RuntimeError("Column 'image_intensity' not found in DataFrame."))

    # Create the output images folder
    images_path = Path(images_dir)
    if not images_path.exists():
        os.mkdir(images_path)
        print(f"Created: {images_path}")

    # Save the 'image_intensity' entries in the images folder
    image_files = []
    encoded_thumbnails = []
    for idx, row in df.iterrows():
        image = row["image_intensity"]
        out_file = images_path / f"{idx:03d}.png"
        pil_image = Image.fromarray(image)
        pil_image.save(out_file)
        encoded_thumbnail = encode_thumbnail(pil_image)
        encoded_thumbnails.append(encoded_thumbnail)
        image_files.append(out_file)

    # Add an encoded thumbnail and image_path to the dataframe.
    df["thumbnail"] = encoded_thumbnails
    df["image_file"] = image_files

    # Normalize the DataFrame
    df_normed = Featurizer.normalize(df)

    # Save the dataframe as CSV
    csv_path = images_path / "dataset.csv"
    df_normed.to_csv(csv_path)
    print(f"Saved {csv_path}")
