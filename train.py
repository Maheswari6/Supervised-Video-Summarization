from tensorboardX import SummaryWriter
import numpy as np
import json
import os
from tqdm import tqdm, trange
import h5py
from prettytable import PrettyTable

import eval

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Bidirectional, Dense, TimeDistributed
from tensorflow.keras.layers import Attention
from tensorflow.keras import Input, Model
from data_loader import get_loader

"""model = Sequential()
model.add(LSTM(256, input_shape = (320,1024)))
model.add(RepeatVector(320))
model.add(LSTM(256, return_sequences = True))
model.add(TimeDistributed(Dense(320, activation = 'softmax')))
model.compile(loss = 'categorical_crossentropy', optimizer = 'adam', metrics = ['accuracy'])"""

class BuildModel(object):

    def __init__(self, config = None, train_loader = None, test_dataset = None):

        self.config = config
        self.train_loader = train_loader
        self.test_dataset = test_dataset

        if not os.path.exists(self.config.score_dir):
            os.mkdir(self.config.score_dir)

        if not os.path.exists(self.config.save_dir):
            os.mkdir(self.config.save_dir)



    def train(self):

        encoder_inputs = Input(shape = (320, 1024))

        encoder_BidirectionalLSTM = Bidirectional(LSTM(128, return_sequences = True))
        encoder_out = encoder_BidirectionalLSTM(encoder_inputs)

        decoder_LSTM = LSTM(256, return_sequences = True)
        decoder_out = decoder_LSTM(encoder_out)

        attn_layer = Attention(use_scale = True)
        attn_out =  attn_layer([encoder_out, decoder_out])

        dense = TimeDistributed(Dense(1, activation = 'softmax'))
        decoder_pred = dense(attn_out)

        model = Model(inputs = encoder_inputs, outputs = decoder_pred)
        model.compile(loss = 'categorical_crossentropy', optimizer = 'adam', metrics = ['accuracy'])
        model.summary()

        self.model = model

        t = trange(self.config.n_epochs, desc = 'Epoch', ncols = 90)
        for epoch_i in t:

            model.fit_generator(generator = self.train_loader)

            ckpt_path = self.config.save_dir + '/epoch-{}.ckpt'.format(epoch_i)
            tqdm.write("Save parameters at {}".format(ckpt_path))
            model.save_weights('ckpt_path')
            self.evaluate(epoch_i)

    def evaluate(self, epoch_i):

        out_dict = {}
        eval_arr = []
        table = PrettyTable()
        table.title = 'Evaluation Result of epoch {}'.format(epoch_i)
        table.field_names = ['ID', 'Precision', 'Recall', 'F-Score']
        table.float_format = '1.5'

        with h5py.File(self.config.data_path) as data_file:
            for feature, label, index in tqdm(self.test_dataset, desc = 'Evaluate', ncols = 90, leave = False):

                pred_score = self.model.predict(feature.reshape(-1,320,1024))
                video_info = data_file['video_'+str(index)]
                pred_score, pred_selected, pred_summary = eval.select_keyshots(video_info, pred_score)
                true_summary_arr = video_info['user_summary'][:]
                eval_res = [eval.eval_metrics(pred_summary, true_summary) for true_summary in true_summary_arr]
                eval_res = np.mean(eval_res, axis = 0).tolist()

                eval_arr.append(eval_res)
                table.add_row([index] + eval_res)

                out_dict[str(index)] = {
                'pred_score' : pred_score,
                'pred_selected' : pred_selected,
                'pred_summary' : pred_summary
                }

        score_save_path = self.config.score_dir + '/epoch-{}.json'.format(epoch_i)
        with open(score_save_path,'w') as f:
            tqdm.write('Save score at {}'.format(str(score_save_path)))
            json.dump(out_dict,f)
        eval_mean = np.mean(eval_arr, axis = 0).tolist()
        table.add_row(['mean'] + eval_mean)
        tqdm.write(str(table))

if __name__ == '__main__':
    from config import Config
    from data_loader import get_loader
    train_config = Config()
    train_loader, test_dataset = get_loader(train_config.data_path, batch_size = train_config.batch_size)
    builder = BuildModel(train_config, train_loader, test_dataset)
    builder.train()
