from tensorflow import keras
import tensorflow as tf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

def split_data(dataset):
    """ 데이터셋 나누기

    Parameters
    ----------
    dataset : 데이터셋

    Returns
    -------
    (데이터, 레이블)
    """

    total_value = []

    dataset = dataset.transpose()
    value = dataset[:-1]
    label = dataset[-1:]
    label = np.array(label.transpose())
    # label = label.reshape(-1)

    for i in range(len(value.columns)):
        v_list = list(np.array(value[i].tolist()))
        total_value.append(v_list)

    total_value = np.array(total_value)

    return total_value, label

train_xy = pd.read_csv('train_data.csv')
test_xy = pd.read_csv('test_data.csv')

x_train, y_train = split_data(train_xy)
x_test, y_test = split_data(test_xy)

model = keras.models.Sequential()
model.add(keras.layers.Dense(300, input_dim=120, activation="relu"))
model.add(keras.layers.Dense(100, activation="relu"))
model.add(keras.layers.Dense(7, activation="softmax"))

model.summary()

model.compile(loss="sparse_categorical_crossentropy",
              optimizer="sgd",
              metrics=["accuracy"])

history = model.fit(x_train, y_train, epochs=30, batch_size=1)

# pd.DataFrame(history.history).plot(figsize=(8, 5))
# plt.grid(True)
# plt.gca().set_ylim(0, 1)
# plt.show()

#모델 평가
model.evaluate(x_test, y_test)

X_new = x_test[:3]
y_proba = model.predict(X_new)
y_proba.round(2)

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open('model.tflite', 'wb') as f:
  f.write(tflite_model)