from pathlib import Path
from typing import Callable, Union

import pandas as pd
from tqdm import tqdm

from .featurizer import Featurizer


VALID_IMAGE_FORMATS = ["tif", "tiff", "png", "jpeg", "jpg"]


def apply_featurizer(
    featurizer_func: Callable, images_dir: Union[Path, str], **featurizer_kwargs
) -> Path:
    """
    Apply a featurizer function to all images in a specified directory. Save the results as a CSV file in the image directory.
    
    The featurizer function must have the following signature:
        1. It must take an `image` NumPy array as input (and possibly other arguments). The image array should be readable from a file by Pillow's Image.open function.
        2. It must return a Python dictionary of numeric image features for the image.
        
    Example featurizer function:
    ============================
    
    def simple_featurizer(image: np.ndarray) -> Dict:
        image_mean = np.mean(image)
        image_max = image.max()
        return {
            "mean": image_mean,
            "max": image_max
        }

    Parameters
    ==========
    - featurizer_func: Featurizer function to apply to each image in images_dir.
    - images_dir: A path to a directory of 2D images (the images must be readable by Pillow's Image.open function).
    - **featurizer_kwargs: Extra keyword arguments to pass to the featurizer function, apart from "image".
    """
    # Make a featurizer out of the function
    featurizer = Featurizer(featurizer_func)

    # List image files in the folder
    images_path = Path(images_dir)
    image_files = list(images_path.iterdir())
    
    # Filter image files:
    valid_image_files = []
    valid_formats = []
    other_files = []
    invalid_formats = []
    for f in image_files:
        extension = f.name.split(".")[-1]
        if extension in VALID_IMAGE_FORMATS:
            valid_image_files.append(f)
            if extension not in valid_formats:
                valid_formats.append(extension)
        else:
            other_files.append(f)
            if extension not in invalid_formats:
                invalid_formats.append(extension)
    
    n_valid_files = len(valid_image_files)
    if n_valid_files == 0:
        print("No valid image files found in this folder.")
        return
    
    print(f"{n_valid_files} valid image files found ({valid_formats}).")
    print(f"{len(other_files)} other files found ({invalid_formats}).")

    # Run the featurizer on all image files
    df = pd.DataFrame({"image_file": valid_image_files})
    records = []
    for image_file in tqdm(
        valid_image_files, total=len(valid_image_files), desc="Applying featurizer"
    ):
        records.append(featurizer.featurize(image_file, **featurizer_kwargs))
    
    for key in list(records[0].keys()):
        df[key] = [record[key] for record in records]
    
    # Normalize the DataFrame
    df_normed = Featurizer.normalize(df)

    # Add the image ID
    df_normed["id"] = df_normed.index

    # Save the dataframe as CSV
    csv_path = images_path / "dataset.csv"
    df_normed.to_csv(csv_path)
    print(f"Saved {csv_path}")
    
    return csv_path
