
import nn


class PerceptronModel(object):
    def __init__(self, dimensions):
        """
        Initialize a new Perceptron instance.

        A perceptron classifies data points as either belonging to a particular
        class (+1) or not (-1). `dimensions` is the dimensionality of the data.
        For example, dimensions=2 would mean that the perceptron must classify
        2D points.
        """
        self.w = nn.Parameter(1, dimensions)

    def get_weights(self):
        """
        Return a Parameter instance with the current weights of the perceptron.
        """
        return self.w

    def run(self, x):
        """
        Calculates the score assigned by the perceptron to a data point x.

        Inputs:
            x: a node with shape (1 x dimensions)
        Returns: a node containing a single number (the score)
        """
        return nn.DotProduct(x, self.w)

    def get_prediction(self, x):
        """
        Calculates the predicted class for a single data point `x`.

        Returns: 1 or -1
        """
        dot = self.run(x)
        if nn.as_scalar(dot) >= 0.0:
            return 1
        else:
            return -1

    def train(self, dataset):
        """
        Train the perceptron until convergence.
        """
        count = 1
        while count != 0:
            count = 0
            for data in dataset.iterate_once(1):
                if self.get_prediction(data[0]) == -1 and nn.as_scalar(data[1]) == 1:
                    count += 1
                    nn.Parameter.update(self.w, data[0], 1)
                elif self.get_prediction(data[0]) == 1 and nn.as_scalar(data[1]) == -1:
                    count += 1
                    nn.Parameter.update(self.w, data[0], -1)


class RegressionModel(object):
    """
    A neural network model for approximating a function that maps from real
    numbers to real numbers. The network should be sufficiently large to be able
    to approximate sin(x) on the interval [-2pi, 2pi] to reasonable precision.
    """
    def __init__(self):
        # Initialize your model parameters here
        self.w_1 = nn.Parameter(1, 400)
        self.b_1 = nn.Parameter(1, 400)

        self.w_2 = nn.Parameter(400, 1)
        self.b_2 = nn.Parameter(1, 1)

        self.batch_size = 0
        self.alpha = -0.01

    def run(self, x):
        """
        Runs the model for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 1)
        Returns:
            A node with shape (batch_size x 1) containing predicted y-values
        """
        if self.batch_size == 0:
            self.batch_size = x.data.shape[0]

        first_bias = nn.ReLU(nn.AddBias(nn.Linear(x, self.w_1), self.b_1))

        return nn.AddBias(nn.Linear(first_bias, self.w_2), self.b_2)

    def get_loss(self, x, y):
        """
        Computes the loss for a batch of examples.

        Inputs:
            x: a node with shape (batch_size x 1)
            y: a node with shape (batch_size x 1), containing the true y-values
                to be used for training
        Returns: a loss node
        """
        return nn.SquareLoss(self.run(x), y)

    def train(self, dataset):
        """
        Trains the model.
        """
        while True:
            losses = 0
            for x,y in dataset.iterate_once(self.batch_size):
                loss = self.get_loss(x, y)
                losses += nn.as_scalar(loss)
                origin = [self.w_1, self.b_1, self.w_2, self.b_2]
                gradient = nn.gradients(loss, origin)
                for i in range(len(origin)):
                    origin[i].update(gradient[i], self.alpha)
            if losses / dataset.x.shape[0] < 0.02:
                break


class DigitClassificationModel(object):
    """
    A model for handwritten digit classification using the MNIST dataset.

    Each handwritten digit is a 28x28 pixel grayscale image, which is flattened
    into a 784-dimensional vector for the purposes of this model. Each entry in
    the vector is a floating point number between 0 and 1.

    The goal is to sort each digit into one of 10 classes (number 0 through 9).

    (See RegressionModel for more information about the APIs of different
    methods here. We recommend that you implement the RegressionModel before
    working on this part of the project.)
    """
    def __init__(self):
        # Initialize your model parameters here
        # w_1 is first layer weight of neurons 1-784 in input layer to neurons 1-100 in hidden layer
        self.w_1 = nn.Parameter(784, 100)
        self.b_1 = nn.Parameter(1, 100)

        # w_2 is second layer neurons 1-100 in hidden layer to neurons 1-10 in output layer
        self.w_2 = nn.Parameter(100, 10)
        self.b_2 = nn.Parameter(1, 10)

        self.batch_size = 5

        # alpha or learning rate
        self.alpha = -0.01

    def run(self, x):
        """
        Runs the model for a batch of examples.

        Your model should predict a node with shape (batch_size x 10),
        containing scores. Higher scores correspond to greater probability of
        the image belonging to a particular class.

        Inputs:
            x: a node with shape (batch_size x 784)
        Output:
            A node with shape (batch_size x 10) containing predicted scores
                (also called logits)
        """
        first_bias = nn.ReLU(nn.AddBias(nn.Linear(x, self.w_1), self.b_1))

        return nn.AddBias(nn.Linear(first_bias, self.w_2), self.b_2)

    def get_loss(self, x, y):
        """
        Computes the loss for a batch of examples.

        The correct labels `y` are represented as a node with shape
        (batch_size x 10). Each row is a one-hot vector encoding the correct
        digit class (0-9).

        Inputs:
            x: a node with shape (batch_size x 784)
            y: a node with shape (batch_size x 10)
        Returns: a loss node
        """
        return nn.SoftmaxLoss(self.run(x), y)

    def train(self, dataset):
        """
        Trains the model.
        """
        while True:
            for x, y in dataset.iterate_once(self.batch_size):
                loss = self.get_loss(x, y)
                origin = [self.w_1, self.b_1, self.w_2, self.b_2]
                gradient = nn.gradients(loss, origin)
                for i in range(len(origin)):
                    origin[i].update(gradient[i], self.alpha)
            if dataset.get_validation_accuracy() >= 0.975:
                break


class LanguageIDModel(object):
    """
    A model for language identification at a single-word granularity.

    (See RegressionModel for more information about the APIs of different
    methods here. We recommend that you implement the RegressionModel before
    working on this part of the project.)
    """
    def __init__(self):
        # Our dataset contains words from five different languages, and the
        # combined alphabets of the five languages contain a total of 47 unique
        # characters.
        # You can refer to self.num_chars or len(self.languages) in your code
        self.num_chars = 47
        self.languages = ["English", "Spanish", "Finnish", "Dutch", "Polish"]

        # Initialize your model parameters here
        self.batch_size = 0
        self.alpha = -0.01
        self.w_1 = nn.Parameter(self.num_chars, 100)
        self.w_2 = nn.Parameter(100, 100)
        self.w_3 = nn.Parameter(100, len(self.languages))

    def run(self, xs):
        """
        Runs the model for a batch of examples.

        Although words have different lengths, our data processing guarantees
        that within a single batch, all words will be of the same length (L).

        Here `xs` will be a list of length L. Each element of `xs` will be a
        node with shape (batch_size x self.num_chars), where every row in the
        array is a one-hot vector encoding of a character. For example, if we
        have a batch of 8 three-letter words where the last word is "cat", then
        xs[1] will be a node that contains a 1 at position (7, 0). Here the
        index 7 reflects the fact that "cat" is the last word in the batch, and
        the index 0 reflects the fact that the letter "a" is the inital (0th)
        letter of our combined alphabet for this task.

        Your model should use a Recurrent Neural Network to summarize the list
        `xs` into a single node of shape (batch_size x hidden_size), for your
        choice of hidden_size. It should then calculate a node of shape
        (batch_size x 5) containing scores, where higher scores correspond to
        greater probability of the word originating from a particular language.

        Inputs:
            xs: a list with L elements (one per character), where each element
                is a node with shape (batch_size x self.num_chars)
        Returns:
            A node with shape (batch_size x 5) containing predicted scores
                (also called logits)
        """
        if self.batch_size == 0:
            self.batch_size = xs[0].data.shape[0]

        f = nn.ReLU(nn.Linear(xs[0], self.w_1))

        for i in range(len(xs)):
            if i == 0:
                continue
            else:
                f = nn.ReLU(nn.Add(nn.Linear(xs[i], self.w_1), nn.Linear(f, self.w_2)))

        return nn.Linear(f, self.w_3)

    def get_loss(self, xs, y):
        """
        Computes the loss for a batch of examples.

        The correct labels `y` are represented as a node with shape
        (batch_size x 5). Each row is a one-hot vector encoding the correct
        language.

        Inputs:
            xs: a list with L elements (one per character), where each element
                is a node with shape (batch_size x self.num_chars)
            y: a node with shape (batch_size x 5)
        Returns: a loss node
        """
        return nn.SoftmaxLoss(self.run(xs), y)

    def train(self, dataset):
        """
        Trains the model.
        """
        while True:
            for x, y in dataset.iterate_once(self.batch_size):
                loss = self.get_loss(x, y)
                origin = [self.w_1, self.w_2, self.w_3]
                gradient = nn.gradients(loss, origin)
                for i in range(len(origin)):
                    origin[i].update(gradient[i], self.alpha)
            if dataset.get_validation_accuracy() >= 0.83:
                break
