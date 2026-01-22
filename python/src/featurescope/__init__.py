from ._version import version as __version__

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from .featurizer import (
    apply_from_images_df,
    apply_from_label_image_df,
    apply_to_images,
    apply_to_label_image,
)
