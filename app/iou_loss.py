import tensorflow as tf
from tensorflow.keras.losses import Loss

class IoULoss(Loss):
    def call(self, y_true, y_pred):
        intersection = tf.reduce_sum(tf.minimum(y_true, y_pred), axis=-1)
        union = tf.reduce_sum(tf.maximum(y_true, y_pred), axis=-1)
        iou = intersection / union
        return 1 - iou
