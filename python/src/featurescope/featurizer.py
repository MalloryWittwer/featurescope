import io
import base64
import os
from pathlib import Path
from typing import Callable, Union

import numpy as np
import pandas as pd
from PIL import Image


THUMBNAIL_SIZE = int(os.getenv("THUMBNAIL_SIZE", 64))


def load_image(image_file: Union[Path, str]) -> Image.Image:
    # Read the image using Pillow
    image_path = Path(image_file)
    if not image_path.exists():
        raise FileNotFoundError(f"Image file does not exist: {image_path}")
    try:
        pil_image = Image.open(image_path)
    except Exception as e:
        raise OSError(f"Could not read image file {image_path}: {e}") from e

    return pil_image


def encode_thumbnail(pil_image: Image.Image) -> str:
    # Compute an image thumbnail
    thumbnail = pil_image.resize((THUMBNAIL_SIZE, THUMBNAIL_SIZE))

    # Encode the thumbnail and store it in the CSV
    output = io.BytesIO()
    thumbnail.save(output, format="png")
    thumbnail_data = output.getvalue()
    encoded_thumbnail = base64.b64encode(thumbnail_data).decode("utf-8")
    
    return encoded_thumbnail


class Featurizer:
    def __init__(self, func: Callable) -> None:
        self.func = func

    def featurize(
        self, pil_image: Union[Image.Image, np.ndarray], **kwargs
    ) -> pd.DataFrame:
        # Convert PIL => NumPy array
        image_arr = np.asarray(pil_image)

        # Apply the featurizer function to the image
        df = self.func(image_arr, **kwargs)

        return df

    @classmethod
    def normalize(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Apply a min-max normalization to the numeric columns of the provided DataFrame."""
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
        
        # Add the image ID
        df_normed["id"] = df_normed.index
        
        # Keep only numeric columns + thumbnail and image_file columns
        numeric_cols = df_normed.select_dtypes(include=[np.number]).columns
        df_normed_numeric = df_normed[numeric_cols].copy()
        df_normed_numeric["thumbnail"] = df_normed["thumbnail"]
        df_normed_numeric["image_file"] = df_normed["image_file"]

        return df_normed_numeric
