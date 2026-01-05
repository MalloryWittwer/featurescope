import io
import base64
import os
from pathlib import Path
from typing import Callable, Union

import numpy as np
import pandas as pd
from PIL import Image


THUMBNAIL_SIZE = int(os.getenv("THUMBNAIL_SIZE", 64))


class Featurizer:
    def __init__(self, func: Callable) -> None:
        self.func = func
    
    def featurize(self, image_file: Union[str, Path], **kwargs) -> pd.DataFrame:
        # Sanitize the image file
        image_path = Path(image_file)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file does not exist: {image_path}")
        
        # Read the image into a numpy array using PIL
        try:
            pil_image = Image.open(image_file)
        except Exception as e:  
            raise OSError(f"Could not read image file {image_path}: {e}") from e
        
        image_arr = np.asarray(pil_image)
        
        # Apply the featurizer function to the image
        df = self.func(image_arr, **kwargs)
        
        # Compute an image thumbnail
        thumbnail = pil_image.resize((THUMBNAIL_SIZE, THUMBNAIL_SIZE))
        
        # Encode the thumbnail and store it in the CSV
        output = io.BytesIO()
        thumbnail.save(output, format=pil_image.format)
        thumbnail_data = output.getvalue()
        encoded_thumbnail = base64.b64encode(thumbnail_data).decode('utf-8')
        
        df["thumbnail"] = encoded_thumbnail
        
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

        return df_normed