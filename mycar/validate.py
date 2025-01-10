import os
import math
import argparse
import numpy as np
import tensorflow as tf

import donkeycar as dk
from donkeycar.parts.keras import KerasPilot, Keras3D_CNN, KerasIMU, KerasBehavioral, KerasLSTM, KerasLatent, KerasLinear
from donkeycar.parts.tub_v2 import Tub

def rmse(preds, gts):
    return math.sqrt(np.mean((np.array(preds) - np.array(gts))**2))

def load_model(kl, model_path):
    start = time.time()
    print('loading model', model_path)
    kl.load(model_path)
    print('finished loading in %s sec.' % (str(time.time() - start)) )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='mypilot.h5')
    parser.add_argument('--tub', type=str, default='val_tub')
    args = parser.parse_args()

    #When we have a model, first create an appropriate Keras part
    kl = dk.utils.get_model_by_type(model_type, cfg)

    model_reload_cb = None

    if '.h5' in model_path or '.uff' in model_path or 'tflite' in model_path or '.pkl' in model_path:
        #when we have a .h5 extension
        #load everything from the model file
        load_model(kl, model_path)

        def reload_model(filename):
            load_model(kl, filename)

        model_reload_cb = reload_model

    elif '.json' in model_path:
        #when we have a .json extension
        #load the model from there and look for a matching
        #.wts file with just weights
        load_model_json(kl, model_path)
        weights_path = model_path.replace('.json', '.weights')
        load_weights(kl, weights_path)

        def reload_weights(filename):
            weights_path = filename.replace('.json', '.weights')
            load_weights(kl, weights_path)

        model_reload_cb = reload_weights

    else:
        print("ERR>> Unknown extension type on model file!!")
        return

    # Load the validation tub
    tub = Tub(args.tub)
    records = list(tub)

    steering_preds, throttle_preds = [], []
    steering_gts, throttle_gts = [], []

    for record in records:
        img_arr = record['cam/image_array']
        st_gt = record.get('user/angle', 0.0)
        th_gt = record.get('user/throttle', 0.0)

        # Run inference
        st_pred, th_pred = kl.run(img_arr)

        steering_preds.append(st_pred)
        throttle_preds.append(th_pred)
        steering_gts.append(st_gt)
        throttle_gts.append(th_gt)

    print("Steering RMSE:", rmse(steering_preds, steering_gts))
    print("Throttle RMSE:", rmse(throttle_preds, throttle_gts))

if __name__ == '__main__':
    main()
