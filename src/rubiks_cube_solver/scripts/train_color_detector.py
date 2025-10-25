import json
import logging

import joblib
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier

from rubiks_cube_solver.constants import COLOR_TO_CLASS, COLORS_PATH, MODEL_PATH
from rubiks_cube_solver.types import Color

logger = logging.getLogger(__name__)

MIN_NEIGHBORS = 1
MAX_NEIGHBORS = 10


def main():
    with open(COLORS_PATH, "r") as f:
        data: dict[str, list[list[float]]] = json.load(f)

    x, y = [], []

    for color, pixels in data.items():
        color = Color(color)
        for pixel in pixels:
            x.append(pixel)
            y.append(COLOR_TO_CLASS[color])

    x = np.vstack(x)
    y = np.vstack(y).squeeze(1)

    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=42)

    best_n = None
    best_score = -np.inf
    for n in range(MIN_NEIGHBORS, MAX_NEIGHBORS + 1):
        classifier = KNeighborsClassifier(n)
        scores = cross_val_score(classifier, x_train, y_train)
        mean_score = np.mean(scores)
        logger.debug(f"{n=}, {mean_score=}")
        if mean_score > best_score:
            best_score = mean_score
            best_n = n

    logger.info(f"Best N: {best_n}")

    classifier = KNeighborsClassifier(best_n)
    classifier.fit(x_train, y_train)

    p_train = classifier.predict(x_train)
    p_test = classifier.predict(x_test)

    train_acc = accuracy_score(y_train, p_train)
    test_acc = accuracy_score(y_test, p_test)

    logger.info(f"Final performance: {train_acc=:.2f}, {test_acc=:.2f}")

    joblib.dump(classifier, MODEL_PATH)


if __name__ == "__main__":
    main()
