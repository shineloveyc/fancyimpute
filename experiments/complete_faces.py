
import pylab
from sklearn.datasets import fetch_olivetti_faces
import numpy as np

from fancyimpute import (
    AutoEncoder,
    MICE,
    MatrixFactorization,
    NuclearNormMinimization,
    SimpleFill,
    IterativeSVD,
    SoftImpute,
)


def load_faces_data(
        missing_square_size=32,
        width=64,
        height=64,
        fetch_data_fn=fetch_olivetti_faces,
        random_seed=0):
    np.random.seed(random_seed)
    dataset = fetch_data_fn()
    full_faces_matrix = dataset.data.astype(np.float32)
    incomplete_faces = []
    n_faces, n_pixels = full_faces_matrix.shape
    assert n_pixels == width * height
    for i in range(n_faces):
        image = full_faces_matrix[i].reshape((height, width)).copy()
        start_x = np.random.randint(low=0, high=height - missing_square_size + 1)
        start_y = np.random.randint(low=0, high=width - missing_square_size + 1)
        image[
            start_x:start_x + missing_square_size,
            start_y:start_y + missing_square_size] = np.nan
        incomplete_faces.append(image.reshape((n_pixels,)))
    incomplete_faces_matrix = np.array(incomplete_faces, dtype=np.float32)
    return full_faces_matrix, incomplete_faces_matrix


def save_images(
        images,
        imshape=(64, 64),
        image_indices=[0, 100, 200],
        base_filename=None):
    for i in image_indices:
        fig, ax = pylab.subplots(1, 1)
        image = images[i, :].copy().reshape(imshape)
        image[np.isnan(image)] = 0
        ax.imshow(image, cmap="gray")
        if base_filename:
            filename = base_filename + "_%d" % (i) + ".png"
            fig.savefig(filename)


def compare_images(
        original,
        incomplete,
        completed,
        imshape=(64, 64),
        image_indices=[0, 100, 200, 300],
        base_filename=None):
    for i in image_indices:
        fig, (ax1, ax2, ax3) = pylab.subplots(1, 3)
        ax1.imshow(original[i].reshape(imshape), cmap="gray")
        ax2.imshow(incomplete[i].reshape(imshape), cmap="gray")
        ax3.imshow(completed[i].reshape(imshape), cmap="gray")
        if base_filename:
            filename = base_filename + "_%d" % (i) + ".png"
            fig.savefig(filename)

if __name__ == "__main__":
    original, incomplete = load_faces_data()
    save_images(original, base_filename="original")
    save_images(incomplete, base_filename="incomplete")

    # SoftImpute without rank constraints
    save_images(
        SoftImpute().complete(incomplete),
        base_filename="SoftImpute")

    for rank in [5, 50]:
        for solver_class in [IterativeSVD, SoftImpute, MatrixFactorization]:
            solver = solver_class(rank=rank)
            completed = solver.complete(incomplete)
            save_images(
                completed,
                base_filename="%s_rank%d" % (solver_class.__name__, rank))
        nn = AutoEncoder(
            hidden_layer_sizes=[1000, rank],
            hidden_activation="tanh",
            output_activation="sigmoid")
        completed_nn = nn.complete(incomplete)
        save_images(
            completed_nn,
            base_filename="nn_rank%d" % rank)

    for fill_method in ["mean", "median"]:
        filler = SimpleFill(fill_method=fill_method)
        completed_fill = filler.complete(incomplete)
        save_images(
            completed_fill,
            base_filename="simple_fill_%s" % fill_method)
