import numpy as np


def weighted_accuracy(y_true, y_pred, alpha=2):
    """
    Calculate the Weighted Accuracy metric.

    Weighted Accuracy measures the prediction accuracy while penalizing underestimation
    more than overestimation of task durations.

    Formula:
        Weighted Accuracy = 100% * (1 - sum(W_i * |T_pred,i - T_actual,i|) / sum(T_actual,i))

    Where:
        - T_pred,i: predicted duration for task i
        - T_actual,i: actual duration for task i
        - W_i: weight of the error:
            - W_i = alpha if T_pred,i < T_actual,i
            - W_i = 1 if T_pred,i >= T_actual,i
        - N: total number of tasks

    :param y_true: array-like, actual target values (T_actual)
    :param y_pred: array-like, predicted target values (T_pred)
    :param alpha: float, penalty factor for underestimation (default = 2)
    :return: float, weighted accuracy in percentage
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # Compute weights
    weights = np.where(y_pred < y_true, alpha, 1)

    # Compute absolute errors
    errors = np.abs(y_pred - y_true)

    # Weighted sum of errors
    weighted_errors = weights * errors

    # Total actual values
    total_actual = np.sum(y_true)

    # Ensure total_actual is not zero to avoid division by zero
    if total_actual == 0:
        raise ValueError("The sum of actual values (y_true) must not be zero.")

    # Calculate weighted accuracy
    weighted_acc = 1 - np.sum(weighted_errors) / total_actual

    return weighted_acc
