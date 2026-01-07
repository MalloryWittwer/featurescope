from pathlib import Path
import pandas as pd
import skimage.io
from scipy.ndimage import binary_fill_holes
from skimage.morphology import remove_small_objects
from skimage.measure import label
from skimage.measure import regionprops_table

from featurescope import apply_dataframe

image = skimage.io.imread(Path(__file__).parent / "fish.png")

binary_img = image < 200
binary_img = binary_fill_holes(binary_img)
binary_img = remove_small_objects(binary_img, max_size=500)
label_img = label(binary_img)

measurements = regionprops_table(
    label_img,
    intensity_image=image,
    properties=[
        "image_intensity",
        "area",
        "eccentricity",
        "intensity_mean",
        "solidity",
    ],
)

df = pd.DataFrame(measurements)

apply_dataframe(df, images_dir="output")