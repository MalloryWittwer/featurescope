# 🫧 Spheriscope: A Toolbox for Visualizing Images on a Spherical Latent Space

https://github.com/user-attachments/assets/dee8edab-370e-46ea-97dc-73640a689e3a

**Spheriscope** is a web application designed to explore image datasets projected onto a spherical geometry using autoencoders. Images that are visually similar are positioned close to each other, while dissimilar images are farther apart.

## Components

This project consists of three main components:

- [spherical-autoencoder](./spherical-autoencoder/): A package for training autoencoders with spherical latent spaces.
- [spheriscope-backend](./spheriscope-backend/): The backend application built with [FastAPI](https://fastapi.tiangolo.com/) and [SQLite](https://www.sqlite.org/).
- [spheriscope](./): The frontend application built with [React](https://react.dev/).

## Usage

To use *Spheriscope*, clone the repository and navigate into the project directory:

```sh
git clone -b spheriscope https://github.com/MalloryWittwer/featurescope.git
cd featurescope
```

### Step 1: Prepare an Image Dataset

To get started, you need a **dataset of images**. You can use a subset of the [MNIST](https://search.brave.com/search?q=mnist&source=desktop) dataset as an example.

Ensure that:

- The images can be resized to **64x64 pixels** without losing significant visual quality. The autoencoder operates at this image size. If the images are not already this size, they will be resized internally by the autoencoder.
- The images are **grayscale** with pixel values between 0 and 255. If the images are in RGB, they will be converted to grayscale.

Save your images in PNG, JPG, or TIF format in a dataset folder. For example:

```
images/
├── img1.png
├── img2.png
├── ...
```

### Step 2: Train a Spherical Autoencoder

Follow the [instructions](./spherical-autoencoder/README.md) to install the [spherical-autoencoder](./spherical-autoencoder/) Python package. Then, run the training script:

```sh
spheriscope train <images_dir> <model_output_dir> --epochs 1000 --batch_size 32
```

This will save a model file `encoder.keras` in the specified output directory.

### Step 3: Install and Run *Spheriscope*

**Option 1: With Docker**

To install and run *Spheriscope* using [Docker Compose](https://docs.docker.com/compose/), run:

```sh
docker compose up
```

This will:

- Install and run the [spheriscope-backend](./spheriscope-backend/) on http://localhost:8000.
- Install and run the frontend application on http://localhost:3000.

**Option 2: Without Docker**

To install the app without Docker, first install the Python packages listed in [requirements.txt](./spheriscope-backend/requirements.txt). Then, start the backend server on http://localhost:8000 using:

```sh
uvicorn main:app --port 8000
```

Next, install the frontend application from the root of the project using `npm install`, and start the app on http://localhost:3000 with:

```sh
npm start
```

### Step 4: Load Your Dataset and Visualize It

Once *Spheriscope* is running, use the upload script to project all images from the dataset onto the autoencoder's spherical latent space and load them into the app's SQLite database:

```sh
spheriscope upload <images_dir> <model_output_dir>
```

After the command completes, reload the page at http://localhost:3000. You should see the projected image dataset 🎉.

To stop the application, run:

```sh
docker compose down
```

