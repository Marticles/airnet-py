#!/usr/bin/env python3
import numpy as np
import pandas as pd
from tensorflow.contrib import rnn
from tensorflow.python.ops import variable_scope
from tensorflow.python.framework import dtypes
import tensorflow as tf
import copy
import os
import sys
import datetime
from sklearn.preprocessing import StandardScaler
import pymysql
pymysql.install_as_MySQLdb()

def onehot_encoder(df, col):
    temp = pd.get_dummies(df[col], prefix=col)
    df = pd.concat([df, temp], axis=1)
    del df[col], temp
    return df


site = sys.argv[1]
days = int(sys.argv[3])

conn = pymysql.connect(host='localhost', port=3306, user='root', password='root', db='airnet', charset='utf8')
sql = 'select * from ' + site + ' order by time asc'

df = pd.read_sql_query(sql, conn)
df.fillna(0, inplace=True)

del df['level'], df['time'], df['city'], df['site'], df['primarypollutant']
print(df.head(5))
df_train = df.iloc[:(-days * 24), :].copy()
df_test = df.iloc[-days * 24:, :].copy()
X_train = df_train.values.copy()
X_test = df_test.values.copy()
y_train = df_train['pm25'].values.copy().reshape(-1, 1)
y_test = df_test['pm25'].values.copy().reshape(-1, 1)

for i in range(X_train.shape[1] - 14):
    temp_mean = X_train[:, i].mean()
    temp_std = X_train[:, i].std()
    X_train[:, i] = (X_train[:, i] - temp_mean) / temp_std
    X_test[:, i] = (X_test[:, i] - temp_mean) / temp_std

scaler = StandardScaler().fit(y_train)
y_train = scaler.transform(y_train)
y_test = scaler.transform(y_test)

'''
y_mean = y_train.mean()
y_std = y_train.std()
y_train = (y_train - y_mean) / y_std
y_test = (y_test - y_mean) / y_std
'''

input_seq_len = 12
output_seq_len = 5


def R2(y_test, y_true):
    n = len(y_true)
    p = 7
    r2 = 1 - ((y_true - y_test) ** 2).sum() / ((y_true - np.mean(y_true)) ** 2).sum()
    adjusted_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)
    return abs(adjusted_r2)


def MAE(y_test, y_true):
    return np.mean(abs(y_test - y_true))


def generate_train_samples(x=X_train, y=y_train, batch_size=16, input_seq_len=input_seq_len,
                           output_seq_len=output_seq_len):
    total_start_points = len(x) - input_seq_len - output_seq_len
    start_x_idx = np.random.choice(range(total_start_points), batch_size, replace=False)

    input_batch_idxs = [list(range(i, i + input_seq_len)) for i in start_x_idx]
    input_seq = np.take(x, input_batch_idxs, axis=0)

    output_batch_idxs = [list(range(i + input_seq_len, i + input_seq_len + output_seq_len)) for i in start_x_idx]
    output_seq = np.take(y, output_batch_idxs, axis=0)

    return input_seq, output_seq  # in shape: (batch_size, time_steps, feature_dim)


def generate_test_samples(x=X_test, y=y_test, input_seq_len=input_seq_len, output_seq_len=output_seq_len):
    total_samples = x.shape[0]

    input_batch_idxs = [list(range(i, i + input_seq_len)) for i in
                        range((total_samples - input_seq_len - output_seq_len))]
    input_seq = np.take(x, input_batch_idxs, axis=0)

    output_batch_idxs = [list(range(i + input_seq_len, i + input_seq_len + output_seq_len)) for i in
                         range((total_samples - input_seq_len - output_seq_len))]
    output_seq = np.take(y, output_batch_idxs, axis=0)

    return input_seq, output_seq


x, y = generate_train_samples()
test_x, test_y = generate_test_samples()
print(x.shape, y.shape)
print(test_x.shape, test_y.shape)
learning_rate = 0.001
lambda_l2_reg = 0.003
input_seq_len = input_seq_len
output_seq_len = output_seq_len
hidden_dim = 64
input_dim = X_train.shape[1]
output_dim = y_train.shape[1]
num_stacked_layers = 4
GRADIENT_CLIPPING = 2.5


def build_graph(feed_previous=False):
    tf.reset_default_graph()

    global_step = tf.Variable(
        initial_value=0,
        name="global_step",
        trainable=False,
        collections=[tf.GraphKeys.GLOBAL_STEP, tf.GraphKeys.GLOBAL_VARIABLES])

    weights = {
        'out': tf.get_variable('Weights_out', \
                               shape=[hidden_dim, output_dim], \
                               dtype=tf.float32, \
                               initializer=tf.truncated_normal_initializer()),
    }
    biases = {
        'out': tf.get_variable('Biases_out', \
                               shape=[output_dim], \
                               dtype=tf.float32, \
                               initializer=tf.constant_initializer(0.)),
    }

    with tf.variable_scope('Seq2seq'):
        # Encoder
        enc_inp = [
            tf.placeholder(tf.float32, shape=(None, input_dim), name="inp_{}".format(t))
            for t in range(input_seq_len)
        ]

        # Decoder
        target_seq = [
            tf.placeholder(tf.float32, shape=(None, output_dim), name="y".format(t))
            for t in range(output_seq_len)
        ]
        dec_inp = [tf.zeros_like(target_seq[0], dtype=tf.float32, name="GO")] + target_seq[:-1]

        with tf.variable_scope('LSTMCell'):
            cells = []
            for i in range(num_stacked_layers):
                with tf.variable_scope('RNN_{}'.format(i)):
                    cells.append(tf.contrib.rnn.LSTMCell(hidden_dim))
            cell = tf.contrib.rnn.MultiRNNCell(cells)
            cell = tf.contrib.rnn.AttentionCellWrapper(cell, attn_length=12, state_is_tuple=True)
            cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=0.3)

        def _rnn_decoder(decoder_inputs,
                         initial_state,
                         cell,
                         loop_function=None,
                         scope=None):
            """RNN decoder for the sequence-to-sequence model.
            Args:
              decoder_inputs: A list of 2D Tensors [batch_size x input_size].
              initial_state: 2D Tensor with shape [batch_size x cell.state_size].
              cell: rnn_cell.RNNCell defining the cell function and size.
              loop_function: If not None, this function will be applied to the i-th output
                in order to generate the i+1-st input, and decoder_inputs will be ignored,
                except for the first element ("GO" symbol). This can be used for decoding,
                but also for training to emulate http://arxiv.org/abs/1506.03099.
                Signature -- loop_function(prev, i) = next
                  * prev is a 2D Tensor of shape [batch_size x output_size],
                  * i is an integer, the step number (when advanced control is needed),
                  * next is a 2D Tensor of shape [batch_size x input_size].
              scope: VariableScope for the created subgraph; defaults to "rnn_decoder".
            Returns:
              A tuple of the form (outputs, state), where:
                outputs: A list of the same length as decoder_inputs of 2D Tensors with
                  shape [batch_size x output_size] containing generated outputs.
                state: The state of each cell at the final time-step.
                  It is a 2D Tensor of shape [batch_size x cell.state_size].
                  (Note that in some cases, like basic RNN cell or GRU cell, outputs and
                   states can be the same. They are different for LSTM cells though.)
            """
            with variable_scope.variable_scope(scope or "rnn_decoder"):
                state = initial_state
                outputs = []
                prev = None
                for i, inp in enumerate(decoder_inputs):
                    if loop_function is not None and prev is not None:
                        with variable_scope.variable_scope("loop_function", reuse=True):
                            inp = loop_function(prev, i)
                    if i > 0:
                        variable_scope.get_variable_scope().reuse_variables()
                    output, state = cell(inp, state)
                    outputs.append(output)
                    if loop_function is not None:
                        prev = output
            return outputs, state

        def _basic_rnn_seq2seq(encoder_inputs,
                               decoder_inputs,
                               cell,
                               feed_previous,
                               dtype=dtypes.float32,
                               scope=None):
            """Basic RNN sequence-to-sequence model.
            This model first runs an RNN to encode encoder_inputs into a state vector,
            then runs decoder, initialized with the last encoder state, on decoder_inputs.
            Encoder and decoder use the same RNN cell type, but don't share parameters.
            Args:
              encoder_inputs: A list of 2D Tensors [batch_size x input_size].
              decoder_inputs: A list of 2D Tensors [batch_size x input_size].
              feed_previous: Boolean; if True, only the first of decoder_inputs will be
                used (the "GO" symbol), all other inputs will be generated by the previous
                decoder output using _loop_function below. If False, decoder_inputs are used
                as given (the standard decoder case).
              dtype: The dtype of the initial state of the RNN cell (default: tf.float32).
              scope: VariableScope for the created subgraph; default: "basic_rnn_seq2seq".
            Returns:
              A tuple of the form (outputs, state), where:
                outputs: A list of the same length as decoder_inputs of 2D Tensors with
                  shape [batch_size x output_size] containing the generated outputs.
                state: The state of each decoder cell in the final time-step.
                  It is a 2D Tensor of shape [batch_size x cell.state_size].
            """
            with variable_scope.variable_scope(scope or "basic_rnn_seq2seq"):
                enc_cell = copy.deepcopy(cell)
                _, enc_state = rnn.static_rnn(enc_cell, encoder_inputs, dtype=dtype)
                if feed_previous:
                    return _rnn_decoder(decoder_inputs, enc_state, cell, _loop_function)
                else:
                    return _rnn_decoder(decoder_inputs, enc_state, cell)

        def _loop_function(prev, _):
            '''Naive implementation of loop function for _rnn_decoder. Transform prev from
            dimension [batch_size x hidden_dim] to [batch_size x output_dim], which will be
            used as decoder input of next time step '''
            return tf.matmul(prev, weights['out']) + biases['out']

        dec_outputs, dec_memory = _basic_rnn_seq2seq(
            enc_inp,
            dec_inp,
            cell,
            feed_previous=feed_previous
        )

        reshaped_outputs = [tf.matmul(i, weights['out']) + biases['out'] for i in dec_outputs]


    with tf.variable_scope('Loss'):
        # L2 loss
        output_loss = 0
        for _y, _Y in zip(reshaped_outputs, target_seq):
            output_loss += (tf.reduce_mean(tf.pow(_y - _Y, 2))) ** 0.5

        # L2 regularization
        reg_loss = 0
        for tf_var in tf.trainable_variables():
            if 'Biases_' in tf_var.name or 'Weights_' in tf_var.name:
                reg_loss += tf.reduce_mean(tf.nn.l2_loss(tf_var))

        loss = output_loss + lambda_l2_reg * reg_loss

    with tf.variable_scope('Optimizer'):
        optimizer = tf.contrib.layers.optimize_loss(
            loss=loss,
            learning_rate=learning_rate,
            global_step=global_step,
            optimizer='Adam',
            clip_gradients=GRADIENT_CLIPPING)

    saver = tf.train.Saver

    return dict(
        enc_inp=enc_inp,
        target_seq=target_seq,
        train_op=optimizer,
        loss=loss,
        saver=saver,
        reshaped_outputs=reshaped_outputs,
    )


total_iteractions = 100
batch_size = 16
KEEP_RATE = 0.5
train_losses = []
val_losses = []
display_step = 50

x = np.linspace(0, 40, 130)
train_data_x = x[:110]


def train_model(train_or_not):
    if train_or_not == 'train':
        rnn_model = build_graph(feed_previous=False)
        saver = tf.train.Saver()
        init = tf.global_variables_initializer()
        with tf.Session() as sess:
            sess.run(init)
            print("Training losses: ")
            for epoch in range(total_iteractions):
                batch_input, batch_output = generate_train_samples(batch_size=batch_size)

                feed_dict = {rnn_model['enc_inp'][t]: batch_input[:, t] for t in range(input_seq_len)}
                feed_dict.update({rnn_model['target_seq'][t]: batch_output[:, t] for t in range(output_seq_len)})
                _, loss_t = sess.run([rnn_model['train_op'], rnn_model['loss']], feed_dict)

                feed_dict = {rnn_model['enc_inp'][t]: test_x[:, t, :] for t in range(input_seq_len)}  # batch prediction
                feed_dict.update(
                    {rnn_model['target_seq'][t]: np.zeros([test_x.shape[0], output_dim], dtype=np.float32) for t in
                     range(output_seq_len)})

                final_preds = sess.run(rnn_model['reshaped_outputs'], feed_dict)
                final_preds = np.concatenate(final_preds, axis=1)
                test_y_expand = np.concatenate([test_y[i].reshape(-1) for i in range(0, test_y.shape[0], 5)], axis=0)
                final_preds_expand = np.concatenate(
                    [final_preds[i].reshape(-1) for i in range(0, final_preds.shape[0], 5)], axis=0)
                # final_preds_expand = final_preds_expand*y_std + y_mean
                # test_y_expand = test_y_expand * y_std + y_mean
                if epoch % display_step == 0:
                    print('epoch:', epoch, ',loss:', loss_t)
                if epoch == total_iteractions - 1:
                    print('epoch:', epoch, ',loss:', loss_t)
                    print('MAE:', MAE(test_y_expand, final_preds_expand))

            temp_saver = rnn_model['saver']()
            save_path = temp_saver.save(sess, os.path.join('./', 'multivariate_ts_pollution_case'))
            # writer = tf.summary.FileWriter('graph/', sess.graph)
        print("Checkpoint saved at: ", save_path)
    else:
        pass


def generate_forecast():
    rnn_model = build_graph(feed_previous=True)
    init = tf.global_variables_initializer()
    with tf.Session() as sess:
        sess.run(init)
        saver = rnn_model['saver']().restore(sess, os.path.join('./', 'multivariate_ts_pollution_case'))
        feed_dict = {rnn_model['enc_inp'][t]: test_x[:, t, :] for t in range(input_seq_len)}  # batch prediction
        feed_dict.update({rnn_model['target_seq'][t]: np.zeros([test_x.shape[0], output_dim], dtype=np.float32) for t in
                          range(output_seq_len)})
        final_preds = sess.run(rnn_model['reshaped_outputs'], feed_dict)

        final_preds = [np.expand_dims(pred, 1) for pred in final_preds]
        final_preds = np.concatenate(final_preds, axis=1)
        # print("Test Real RMSE is: ", (np.mean((scaler.inverse_transform(final_preds_expand) - scaler.inverse_transform(test_y_expand))**2))**0.5)
        # print("Test Real MAE is: ",MAE(scaler.inverse_transform(final_preds_expand) ,scaler.inverse_transform(test_y_expand)))
        print("Test R2 is: ", R2(final_preds, test_y))
        print("Test RMSE is: ", (np.mean((final_preds - test_y) ** 2)) ** 0.5)
        print("Test MAE is: ", MAE(final_preds, test_y))

    final_preds_expand = np.concatenate([final_preds[i].reshape(-1) for i in range(0, final_preds.shape[0], 5)], axis=0)
    final_preds_expand = scaler.inverse_transform(final_preds_expand)
    return final_preds_expand


train_or_not = sys.argv[2]
train_model(train_or_not)
forecast_pm25 = generate_forecast().tolist()
cur = conn.cursor()
cur.execute('select time from ' + site + ' order by time desc limit 1')
last_date = cur.fetchall()
conn.close()
last_date = datetime.datetime.strptime(last_date[0][0], "%Y-%m-%d %H:%M:%S")
time = []
temp_date = last_date

for i in range(len(forecast_pm25)):
    temp_date += datetime.timedelta(hours=1)
    time.append(temp_date)
    forecast_pm25[i] = abs(round(forecast_pm25[i], 3))

forecast_df = pd.DataFrame({'forecast_pm25': forecast_pm25, 'time': time})

from sqlalchemy import create_engine

conn = create_engine('mysql+mysqldb://root:root@localhost:3306/airnet?charset=utf8')
pd.io.sql.to_sql(forecast_df, 'forecast_' + site, conn, schema='airnet', if_exists='replace', index=False)
conn.dispose()
