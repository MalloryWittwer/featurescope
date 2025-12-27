from pathlib import Path
from typing import Dict
import numpy as np
import requests
import skimage.io

BACKEND_URL = "http://localhost:8000"


class RandomFeaturizer:
    def __init__(self) -> None:
        pass
    
    def predict(self, image: np.ndarray) -> Dict:
        
        x_pos = np.random.random()
        y_pos = np.random.random()
        
        return {
            "x_pos": x_pos,
            "y_pos": y_pos,
        }


def upload(featurizer, images_dir):
    try:
        response = requests.get(BACKEND_URL)
        if response.status_code != 200:
            print(f"Backend URL {BACKEND_URL} is not available. Status code: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to {BACKEND_URL}. Exception: {e}")
        return

    for image_file in Path(images_dir).iterdir():
        image_file = str(image_file)
        print(f"Uploading {image_file}")

        image = skimage.io.imread(image_file)

        data = featurizer.predict(image)
        print(f"{data=}")
        
        with open(image_file, 'rb') as file:
            response = requests.post(f"{BACKEND_URL}/images/", files={"file": file}, data=data)

        if response.status_code == 200:
            print("Response:", response.json())
        else:
            print("Failed to upload image. Status code:", response.status_code)
            print("Response:", response.text)


if __name__=='__main__':
    featurizer = RandomFeaturizer()
    images_dir = "/home/wittwer/code/spheriscope/data/mnist_images"
    upload(featurizer, images_dir)