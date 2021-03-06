# -*- coding:utf-8 -*-

# ==============================================================================
# tensorflow卷积神经网络。
# ==============================================================================
from util.tensorflow_util import TensorFlowUtil
from tensorflow_basic.base_dnn_tf import *


class BasicCNN(BaseDNN):
    """
    简单的卷积神经网络结构。
    """
    def __init__(self, input_dim, output_dim):
        """
        初始化网络数据。
        :param input_dim:
        :param output_dim:
        """
        # 网络结构参数
        self.x_input = None
        self.y_label = None
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.learning_rate = None
        self.keep_prob = None
        self.global_step = tf.Variable(0)
        self.w_conv1 = None
        self.b_conv1 = None
        self.w_conv2 = None
        self.b_conv2 = None
        self.w_full1 = None
        self.b_full1 = None
        self.w_full2 = None
        self.b_full2 = None

        # 训练需要的超参数
        self.learning_rate_init = 1e-3
        self.training_epochs = 20
        self.dropout = 0.5
        self.batch_size = 1000
        self.display_steps = 1
        self.save_steps = 1

        # 预测优化函数
        self.y_predict = None
        self.y_output = None
        self.loss = None
        self.accuracy = None
        self.optimizer = None

        # sess会话
        self.sess = None

        # 初始化器
        self.initializer = None
        self.merged_summary_op = None

        # 目录初始化
        self.tf_logs_path = os.path.join(com_config.TF_MODEL_LOGS_DIR, "BasicCNN")
        self.checkpoints_path = os.path.join(com_config.TF_MODEL_CHECKPOINT_DIR, "BasicCNN")

        # 变量和参数初始化
        self.init_network()

    @staticmethod
    def name():
        """
        网络结构名称。
        :return:
        """
        return "Basic Convolutional Neural Network(BasicCNN)"

    def init_network(self):
        """
        初始化网络结构信息。
        :return:
        """
        self.placeholders()
        self.variables()
        self.inference()
        self.loss_function()
        self.evaluate_function()
        self.summary()
        self.solver()
        # 初始化变量的操作应该放在最后
        self.init_variables()

    def placeholders(self):
        """
        使用到的占位符。
        :return:
        """
        self.x_input = tf.placeholder(tf.float32, [None, self.input_dim], name="x_input")
        self.y_label = tf.placeholder(tf.float32, [None, self.output_dim], name="y_label")
        self.keep_prob = tf.placeholder(tf.float32, name="dropout")

    def variables(self):
        """
        使用到的变量。
        :return:
        """
        self.global_step = tf.Variable(0)
        self.w_conv1 = TensorFlowUtil.weight_variable([5, 5, 1, 32])
        self.b_conv1 = TensorFlowUtil.bias_variable([32])
        self.w_conv2 = TensorFlowUtil.weight_variable([5, 5, 32, 64])
        self.b_conv2 = TensorFlowUtil.bias_variable([64])
        self.w_full1 = TensorFlowUtil.weight_variable([7 * 7 * 64, 1024])
        self.b_full1 = TensorFlowUtil.bias_variable([1024])
        self.w_full2 = TensorFlowUtil.weight_variable([1024, self.output_dim])
        self.b_full2 = TensorFlowUtil.bias_variable([self.output_dim])

    def inference(self):
        """
        网络结构生成。
        :return:
        """
        # 将x_input变成一个4d向量，其第2、第3维对应图片的宽、高，最后一维代表图片的颜色通道数
        x_images = tf.reshape(self.x_input, [-1, 28, 28, 1])

        layer1_conv = TensorFlowUtil.conv2d(x_images, self.w_conv1, self.b_conv1)
        layer1_relu = TensorFlowUtil.relu(layer1_conv)
        layer1_maxpool = TensorFlowUtil.maxpool2d(layer1_relu)

        layer2_conv = TensorFlowUtil.conv2d(layer1_maxpool, self.w_conv2, self.b_conv2)
        layer2_relu = TensorFlowUtil.relu(layer2_conv)
        layer2_maxpool = TensorFlowUtil.maxpool2d(layer2_relu)

        layer3_flatten = tf.reshape(layer2_maxpool, [-1, self.w_full1.get_shape().as_list()[0]])
        layer3_full = tf.add(tf.matmul(layer3_flatten, self.w_full1), self.b_full1)
        layer3_relu = TensorFlowUtil.relu(layer3_full)
        layer3_dropout = tf.nn.dropout(layer3_relu, self.keep_prob)

        self.y_output = tf.add(tf.matmul(layer3_dropout, self.w_full2), self.b_full2)
        self.y_predict = tf.nn.softmax(self.y_output)

    def loss_function(self):
        """
        损失函数设置。
        :return:
        """
        # 1. 计算softmax交叉熵
        softmax_cross_entropy = tf.nn.softmax_cross_entropy_with_logits_v2(labels=self.y_label, logits=self.y_output)
        self.loss = tf.reduce_mean(tf.reduce_sum(softmax_cross_entropy))

    def evaluate_function(self):
        """
        评价函数设置。
        :return:
        """
        correct_prediction = tf.equal(tf.argmax(self.y_predict, 1), tf.argmax(self.y_label, 1))
        self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    def solver(self):
        """
        求解器。
        :return:
        """
        # 计算学习率
        self.learning_rate = tf.train.exponential_decay(self.learning_rate_init, self.global_step,
                                                        decay_steps=1000, decay_rate=0.5,
                                                        staircase=True)
        # 1. Gradient Descent
        # self.optimizer = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(self.loss)
        # 2. Adam
        self.optimizer = tf.train.AdamOptimizer(self.learning_rate).minimize(self.loss)

    def summary(self):
        """
        summary 网络结构运行状况概要。
        :return:
        """
        tf.summary.scalar("loss", self.loss)
        self.merged_summary_op = tf.summary.merge_all()

    def train_mnist(self):
        """
        训练mnist数据
        :return:
        """
        with tf.Session() as sess:
            self.sess = sess
            # 执行初始化
            sess.run(self.initializer)
            # summary writer
            summary_writer = tf.summary.FileWriter(self.tf_logs_path,
                                                   graph=tf.get_default_graph())
            # saver
            saver = tf.train.Saver()

            # 训练数据
            for epoch in range(self.training_epochs):
                avg_cost = 0.
                total_batch = int(mnist.train.num_examples / self.batch_size)
                # 循环运行所有批次数据
                for i_batch in range(total_batch):
                    batch_xs, batch_ys = mnist.train.next_batch(self.batch_size)

                    # 执行优化、损失函数、准确率
                    _, cost_value, accuracy_value, summary = \
                        sess.run([self.optimizer, self.loss, self.accuracy, self.merged_summary_op],
                                 feed_dict={self.x_input: batch_xs,
                                            self.y_label: batch_ys,
                                            self.keep_prob: self.dropout})

                    # 在summary_writer中记录相应的训练过程
                    summary_writer.add_summary(summary, epoch * total_batch + i_batch)
                    # 计算平均损失
                    avg_cost += cost_value / total_batch

                    common_logger.info("Epoch: {0:0>4}_{1:0>4} cost={2:.9f} accuracy={3:.9f}"
                                       .format((epoch + 1), i_batch, cost_value, accuracy_value))

                # 记录每轮迭代的中间结果
                if (epoch + 1) % self.display_steps == 0:
                    common_logger.info("Epoch: {0:0>4} cost={1:.9f}".format((epoch + 1), avg_cost))
                if (epoch + 1) % self.save_steps == 0:
                    saver.save(sess, self.checkpoints_path, global_step=(epoch + 1))

            # 记录训练的最终结果
            saver.save(sess, self.checkpoints_path, global_step=(self.training_epochs + 1))
            common_logger.info("Optimization Finished!")

            # 测试模型，计算测试数据的准确率
            test_accuracy = self.accuracy.eval(
                {self.x_input: mnist.test.images, self.y_label: mnist.test.labels, self.keep_prob: 1.0})

            common_logger.info("Test Accuracy:{0}".format(test_accuracy))


def cnn_model():
    """
    CNN模型。
    :return:
    """
    # 超参数
    learning_rate_init = 1e-3
    dropout = 0.5
    batch_size = 1000
    max_iters = 1000

    # 参数和占位符
    x_input = tf.placeholder(tf.float32, [None, n_input], name="x_input")
    y_label = tf.placeholder(tf.float32, [None, n_classes], name="y_label")
    keep_prob = tf.placeholder(tf.float32, name="dropout")

    global_step = tf.Variable(0)
    w_conv1 = TensorFlowUtil.weight_variable([5, 5, 1, 32])
    b_conv1 = TensorFlowUtil.bias_variable([32])
    w_conv2 = TensorFlowUtil.weight_variable([5, 5, 32, 64])
    b_conv2 = TensorFlowUtil.bias_variable([64])
    w_full1 = TensorFlowUtil.weight_variable([7 * 7 * 64, 1024])
    b_full1 = TensorFlowUtil.bias_variable([1024])
    w_full2 = TensorFlowUtil.weight_variable([1024, n_classes])
    b_full2 = TensorFlowUtil.bias_variable([n_classes])

    # 构建网络
    # 将x_input变成一个4d向量，其第2、第3维对应图片的宽、高，最后一维代表图片的颜色通道数
    x_images = tf.reshape(x_input, [-1, 28, 28, 1])

    layer1_conv = TensorFlowUtil.conv2d(x_images, w_conv1, b_conv1)
    layer1_relu = TensorFlowUtil.relu(layer1_conv)
    layer1_maxpool = TensorFlowUtil.maxpool2d(layer1_relu)

    layer2_conv = TensorFlowUtil.conv2d(layer1_maxpool, w_conv2, b_conv2)
    layer2_relu = TensorFlowUtil.relu(layer2_conv)
    layer2_maxpool = TensorFlowUtil.maxpool2d(layer2_relu)

    layer3_flatten = tf.reshape(layer2_maxpool, [-1, w_full1.get_shape().as_list()[0]])
    layer3_full = tf.add(tf.matmul(layer3_flatten, w_full1), b_full1)
    layer3_relu = TensorFlowUtil.relu(layer3_full)
    layer3_dropout = tf.nn.dropout(layer3_relu, keep_prob)

    y_output = tf.add(tf.matmul(layer3_dropout, w_full2), b_full2)
    y_predict = tf.nn.softmax(y_output)

    # 损失函数和准确率
    cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=y_output, labels=y_label))
    correct_prediction = tf.equal(tf.argmax(y_predict, 1), tf.argmax(y_label, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    # 优化函数
    learning_rate = tf.train.exponential_decay(learning_rate_init, global_step,
                                               decay_steps=1000, decay_rate=0.8,
                                               staircase=True)
    train_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(cross_entropy)

    # 执行训练
    sess = tf.InteractiveSession()
    tf.global_variables_initializer().run()
    for index in range(max_iters):
        # 批量执行
        batch_xs, batch_ys = mnist.train.next_batch(batch_size)
        _, cost_value, accuracy_value = sess.run([train_step, cross_entropy, accuracy],
                                                 feed_dict={x_input: batch_xs, y_label: batch_ys, keep_prob: dropout})
        common_logger.info("Epoch: {0:0>4} cost={1:.9f} accuracy={2:.9f}"
                           .format((index + 1), cost_value, accuracy_value))

    # 训练数据的准确率
    train_accuracy = sess.run(accuracy, feed_dict={x_input: mnist.train.images,
                                                   y_label: mnist.train.labels,
                                                   keep_prob: 1.0})
    common_logger.info("Train Accuracy:{0:.9f}".format(train_accuracy))

    # 测试数据的准确率
    test_accuracy = sess.run(accuracy, feed_dict={x_input: mnist.test.images,
                                                  y_label: mnist.test.labels,
                                                  keep_prob: 1.0})
    common_logger.info("Test Accuracy:{0:.9f}".format(test_accuracy))


if __name__ == "__main__":
    basicCNN = BasicCNN(n_input, n_classes)
    basicCNN.train_mnist()
    # cnn_model()
    pass

