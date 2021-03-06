import numpy as np
import sys
from os.path import expanduser
user_home = expanduser("~")

bh_path = (user_home+'/Cosmostat/Codes/BlendHunter')
sys.path.extend([bh_path])

from blendhunter import BlendHunter

"""Predict using given pretrained weights.The function returns accuracy.()"""
def run_bh(path, value):

    w_path = user_home+'/Cosmostat/Codes/BlendHunter/pretrained_weights_pad'

    bh = BlendHunter(weights_path=w_path+'/weights{}'.format(value))
    """Only testing on the test images, no training"""
    bh.train(path + '/BlendHunterData',
         get_features=False,
         train_top=False,
         fine_tune=False)

    """Predict Results"""
    pred_top = bh.predict(path + '/BlendHunterData/test/test', weights_type='top')
    true = np.load(path + '/BlendHunterData/test/test/labels.npy')
    print("Match Top:", np.sum(pred_top == true) / true.size)
    print("Error Top", np.sum(pred_top != true) / true.size)

    return np.sum(pred_top == true) / true.size

"""Save results to dictionary"""
def get_results(paths_list=None, n_path=None, sigma_value=None):

    results_dict = dict()

    for i,j in zip(paths_list, n_path):
        acc = run_bh(i, sigma_value)

        #Save results
        results_dict.update({'Path'+str(j):{'Accuracy': acc}})

    return results_dict


"""Check the folder hierarchy"""
path_bh = user_home+'/Cosmostat/Codes/BlendHunter'
"""Paths for both padded or non padded images"""
#path_shift = path_bh + '/more_noise_ranges'
#path_shift_pad = path_bh + '/more_noise_ranges_pad'

#paths = [path_bh+'/bh_'+str(i)  for i in [3,5,7,10,12,14,16,18,20,22,24,26,28,30,32,35,37,40,42,44]]
paths_pad = [path_bh+'/bh_pad'+str(i)  for i in [3,5,7,10,12,14,16,18,20,22,24,26,28,30,32,35,37,40,42,44]]


for i in [5,14,18,26,35,40]:
    for j in ['', 1,2,3,4]:
        """Retrieve results for each set of weights"""
        results_weights = get_results(paths_list=paths_pad, n_path=[3,5,7,10,12,14,16,18,20,22,24,26,28,30,32,35,37,40,42,44], sigma_value=str(i)+str(j))

        """Save dictionary. Check the folders hierarchy"""
        np.save(user_home+'/Cosmostat/Codes/BlendHunter/bh_pad_results/acc_weights{}.npy'.format(str(i)+str(j)), results_weights)
