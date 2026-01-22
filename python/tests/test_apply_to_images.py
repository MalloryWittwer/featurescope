"""
AI disclosure:
This test suite was generated with Claude Haiku 4.5 from a draft and detailed prompt instructions.
"""

import pytest
import tempfile
import shutil
import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image
from typing import Dict

from featurescope import Featurizer


# ============================================================================
# FIXTURES: Setup and Teardown
# ============================================================================


@pytest.fixture
def temp_images_dir():
    """Create a temporary directory for test images."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def images_dir_with_samples(temp_images_dir):
    """Create a directory with 3 sample test images."""
    for i in range(3):
        # Create simple grayscale test images with different values
        img_array = np.full((32, 32), fill_value=50 + i * 30, dtype=np.uint8)
        img = Image.fromarray(img_array, mode="L")
        img.save(Path(temp_images_dir) / f"test_{i}.png")
    return temp_images_dir


@pytest.fixture
def images_dir_with_samples_and_noise(temp_images_dir):
    """Create a directory with 3 images + non-image files."""
    # Add image files
    for i in range(3):
        img_array = np.full((32, 32), fill_value=50 + i * 30, dtype=np.uint8)
        img = Image.fromarray(img_array, mode="L")
        img.save(Path(temp_images_dir) / f"test_{i}.png")

    # Add non-image files
    Path(temp_images_dir).joinpath("readme.txt").write_text("This is not an image")
    Path(temp_images_dir).joinpath("data.csv").write_text("col1,col2\n1,2\n")

    return temp_images_dir


# ============================================================================
# FEATURIZER FUNCTIONS
# ============================================================================


def minmax_featurizer(image: np.ndarray) -> Dict:
    """Simple featurizer returning min and max."""
    return {"min": float(image.min()), "max": float(image.max())}


def mean_featurizer(image: np.ndarray) -> Dict:
    """Featurizer returning mean value."""
    return {"mean": float(image.mean())}


def param_featurizer(image: np.ndarray, threshold: int = 100) -> Dict:
    """Featurizer with an optional parameter."""
    above_threshold = (image > threshold).sum()
    return {"above_threshold": int(above_threshold)}


def mixed_type_featurizer(image: np.ndarray) -> Dict:
    """Featurizer returning both numeric and non-numeric values."""
    return {
        "numeric_val": float(image.mean()),
        "text_val": "some_text",
        "another_numeric": int(image.max()),
    }


def empty_dict_featurizer(image: np.ndarray) -> Dict:
    """Featurizer returning empty dictionary."""
    return {}


def invalid_featurizer_no_image() -> Dict:
    """Invalid: missing 'image' parameter."""
    return {"value": 0}


def invalid_featurizer_wrong_return(image: np.ndarray) -> None:
    """Invalid: returns None instead of dict."""
    return None


def invalid_featurizer_returns_list(image: np.ndarray) -> list:
    """Invalid: returns list instead of dict."""
    return [1, 2, 3]


# ============================================================================
# TESTS
# ============================================================================


def test_apply_to_images_empty_directory(temp_images_dir):
    """Test that empty directory returns None."""
    result = Featurizer.apply_to_images(
        images_dir=temp_images_dir,
        featurizer_func=minmax_featurizer,
    )
    assert result is None


def test_apply_to_images_with_valid_images(images_dir_with_samples):
    """Test that valid images are processed correctly."""
    csv_path = Featurizer.apply_to_images(
        images_dir=images_dir_with_samples,
        featurizer_func=minmax_featurizer,
    )

    assert csv_path is not None
    assert csv_path.exists()

    df = pd.read_csv(csv_path, index_col=0)
    assert len(df) == 3
    assert "min" in df.columns
    assert "max" in df.columns
    assert "thumbnail" in df.columns
    assert "image_file" in df.columns
    assert "id" in df.columns


def test_apply_to_images_ignores_non_image_files(images_dir_with_samples_and_noise):
    """Test that non-image files are ignored."""
    csv_path = Featurizer.apply_to_images(
        images_dir=images_dir_with_samples_and_noise,
        featurizer_func=minmax_featurizer,
    )

    df = pd.read_csv(csv_path, index_col=0)
    assert len(df) == 3  # Only 3 image files, not 5


def test_apply_to_images_normalization(images_dir_with_samples):
    """Test that numeric columns are normalized to [0, 1]."""
    csv_path = Featurizer.apply_to_images(
        images_dir=images_dir_with_samples,
        featurizer_func=minmax_featurizer,
    )

    df = pd.read_csv(csv_path, index_col=0)

    # Check that numeric columns are in [0, 1]
    assert (df["min"] >= 0).all() and (df["min"] <= 1).all()
    assert (df["max"] >= 0).all() and (df["max"] <= 1).all()


def test_apply_to_images_with_featurizer_params(images_dir_with_samples):
    """Test that featurizer kwargs are passed correctly."""
    csv_path = Featurizer.apply_to_images(
        images_dir=images_dir_with_samples,
        featurizer_func=param_featurizer,
        threshold=60,
    )

    df = pd.read_csv(csv_path, index_col=0)
    assert "above_threshold" in df.columns
    assert len(df) == 3


def test_apply_to_images_mixed_types_drops_non_numeric(images_dir_with_samples):
    """Test that non-numeric values are kept but not normalized."""
    csv_path = Featurizer.apply_to_images(
        images_dir=images_dir_with_samples,
        featurizer_func=mixed_type_featurizer,
    )

    df = pd.read_csv(csv_path, index_col=0)

    # Numeric columns should exist and be normalized
    assert "numeric_val" in df.columns
    assert "another_numeric" in df.columns
    assert (df["numeric_val"] >= 0).all() and (df["numeric_val"] <= 1).all()

    # Non-numeric column should exist but with original values
    assert "text_val" not in df.columns


def test_apply_to_images_empty_dict_featurizer(images_dir_with_samples):
    """Test that empty dict featurizer still creates CSV with metadata."""
    csv_path = Featurizer.apply_to_images(
        images_dir=images_dir_with_samples,
        featurizer_func=empty_dict_featurizer,
    )

    df = pd.read_csv(csv_path, index_col=0)
    assert len(df) == 3
    # Should have thumbnail, image_file, and id columns
    assert "thumbnail" in df.columns
    assert "image_file" in df.columns


def test_apply_to_images_invalid_featurizer_no_image(images_dir_with_samples):
    """Test that featurizer without 'image' parameter raises TypeError."""
    with pytest.raises(TypeError):
        Featurizer.apply_to_images(
            images_dir=images_dir_with_samples,
            featurizer_func=invalid_featurizer_no_image,
        )


def test_apply_to_images_invalid_featurizer_returns_none(images_dir_with_samples):
    """Test that featurizer returning None raises TypeError."""
    with pytest.raises(TypeError):
        Featurizer.apply_to_images(
            images_dir=images_dir_with_samples,
            featurizer_func=invalid_featurizer_wrong_return,
        )


def test_apply_to_images_invalid_featurizer_returns_list(images_dir_with_samples):
    """Test that featurizer returning non-dict raises TypeError."""
    with pytest.raises(TypeError):
        Featurizer.apply_to_images(
            images_dir=images_dir_with_samples,
            featurizer_func=invalid_featurizer_returns_list,
        )


def test_apply_to_images_csv_structure(images_dir_with_samples):
    """Test the structure of the saved CSV file."""
    csv_path = Featurizer.apply_to_images(
        images_dir=images_dir_with_samples,
        featurizer_func=minmax_featurizer,
    )

    df = pd.read_csv(csv_path, index_col=0)

    # Check required columns exist
    required_cols = {"id", "thumbnail", "image_file", "min", "max"}
    assert required_cols.issubset(set(df.columns))

    # Check no NaN values
    assert not df.isna().any().any()


def test_apply_to_images_thumbnail_encoded(images_dir_with_samples):
    """Test that thumbnails are base64 encoded strings."""
    csv_path = Featurizer.apply_to_images(
        images_dir=images_dir_with_samples,
        featurizer_func=minmax_featurizer,
    )

    df = pd.read_csv(csv_path, index_col=0)

    # Thumbnails should be non-empty strings
    assert (df["thumbnail"].str.len() > 0).all()
    # They should be valid base64 (only alphanumeric, +, /, =)
    assert all(
        all(
            c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
            for c in thumb
        )
        for thumb in df["thumbnail"]
    )


def test_apply_to_images_creates_dataset_csv(images_dir_with_samples):
    """Test that the output file is named 'features.csv'."""
    csv_path = Featurizer.apply_to_images(
        images_dir=images_dir_with_samples,
        featurizer_func=minmax_featurizer,
    )

    assert csv_path.name == "features.csv"
    assert csv_path.parent == Path(images_dir_with_samples)
