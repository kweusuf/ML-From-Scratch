from __future__ import print_function
from sklearn import datasets
import sys
import os
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Import helper functions
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + "/../utils")
from data_manipulation import train_test_split, categorical_to_binary, normalize, binary_to_categorical
from data_operation import accuracy_score
sys.path.insert(0, dir_path + "/../unsupervised_learning/")
from principal_component_analysis import PCA


# Activation function
def sigmoid(x):
    return 1 / (1 + np.exp(-x))


# Gradient of activation function
def sigmoid_gradient(x):
    return sigmoid(x) * (1 - sigmoid(x))


class MultilayerPerceptron():
    def __init__(self, n_hidden, n_iterations=3000, learning_rate=0.01, plot_errors=False):
        self.n_hidden = n_hidden    # Number of hidden neurons
        self.W = None               # Hidden layer weights
        self.V = None               # Output layer weights
        self.biasW = None           # Hidden layer bias
        self.biasV = None           # Output layer bias
        self.n_iterations = 3000
        self.learning_rate = learning_rate
        self.plot_errors = plot_errors

    def fit(self, X, y):
        # Convert the nominal y values to binary
        y = categorical_to_binary(y)

        n_samples, n_features = np.shape(X)
        n_outputs = np.shape(y)[1]

        # Initial weights between [-1/sqrt(N), 1/sqrt(N)]
        a = -1 / math.sqrt(n_features)
        b = -a
        self.W = (b - a) * np.random.random((n_features, self.n_hidden)) + a
        self.biasW = (b - a) * np.random.random((1, self.n_hidden)) + a
        self.V = (b - a) * np.random.random((self.n_hidden, n_outputs)) + a
        self.biasV = (b - a) * np.random.random((1, n_outputs)) + a

        errors = []
        for i in range(self.n_iterations):
            # Calculate hidden layer
            hidden_input = X.dot(self.W) + self.biasW
            # Calculate output of hidden neurons
            hidden_output = sigmoid(hidden_input)

            # Calculate output layer
            output_layer_input = hidden_output.dot(self.V) + self.biasV
            output_layer_pred = sigmoid(output_layer_input)

            # Calculate the error
            error = y - output_layer_pred
            mse = np.mean(np.power(error, 2))
            errors.append(mse)

            # Calculate loss gradients:
            # Gradient of squared loss w.r.t each parameter
            v_gradient = -2 * (y - output_layer_pred) * \
                sigmoid_gradient(output_layer_input)
            biasV_gradient = v_gradient
            w_gradient = v_gradient.dot(
                self.V.T) * sigmoid_gradient(hidden_input)
            biasW_gradient = w_gradient

            # Update weights
            # Move against the gradient to minimize loss
            self.V -= self.learning_rate * hidden_output.T.dot(v_gradient)
            self.biasV -= self.learning_rate * np.ones((1, n_samples)).dot(biasV_gradient)
            self.W -= self.learning_rate * X.T.dot(w_gradient)
            self.biasW -= self.learning_rate * np.ones((1, n_samples)).dot(biasW_gradient)

        # Plot the training error
        if self.plot_errors:
            plt.plot(range(self.n_iterations), errors)
            plt.title("Training Error Plot")
            plt.ylabel('Training Error')
            plt.xlabel('Iterations')
            plt.show()

    # Use the trained model to predict labels of X
    def predict(self, X):
        # Calculate the output of the hidden neurons
        hidden_output = sigmoid(np.dot(X, self.W) + self.biasW)
        # Set the class labels to the highest valued outputs
        y_pred = np.argmax(sigmoid(np.dot(hidden_output, self.V) + self.biasV), axis=1)

        return y_pred


def main():
    data = datasets.load_digits()
    X = normalize(data.data)
    y = data.target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, seed=1)

    # MLP
    clf = MultilayerPerceptron(n_hidden=10,
        n_iterations=4000,
        learning_rate=0.01, 
        plot_errors=True)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    print ("Accuracy:", accuracy)

    # Reduce dimension to two using PCA and plot the results
    pca = PCA()
    pca.plot_in_2d(X_test, y_pred, title="Multilayer Perceptron", accuracy=accuracy)


if __name__ == "__main__":
    main()
