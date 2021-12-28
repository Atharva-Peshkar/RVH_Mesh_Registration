"""
If code works:
    Author: Bharat
else:
    Author: Anonymous
"""
import pickle as pkl

import torch
import numpy as np


def get_prior(model_root, gender='male', precomputed=False, device="cuda:0"):
    if precomputed:
        prior = Prior(sm=None)
        return prior['Generic']
    else:
        from lib.smpl.wrapper_naive import SMPLNaiveWrapper

        if gender == 'neutral':
            dp_prior = SMPLNaiveWrapper(model_root, gender='male')
        else:
            dp_prior = SMPLNaiveWrapper(model_root, gender=gender)

        prior = Prior(dp_prior.get_smpl(), device=device)
        return prior['Generic']


class ThMahalanobis(object):
    def __init__(self, mean, prec, prefix, device="cuda:0"):
        self.mean = torch.tensor(mean.astype('float32'), requires_grad=False).unsqueeze(axis=0).to(device)
        self.prec = torch.tensor(prec.astype('float32'), requires_grad=False).to(device)
        self.prefix = prefix

    def __call__(self, pose, prior_weight=1.):
        '''
        :param pose: Batch x pose_dims
        :return: weighted L2 distance of the N pose parameters, where N = 72 - prefix for SMPL model
        '''
        # return (pose[:, self.prefix:] - self.mean)*self.prec
        temp = pose[:, self.prefix:] - self.mean
        temp2 = torch.matmul(temp, self.prec) * prior_weight
        return (temp2 * temp2).sum(dim=1)
        

class Prior(object):
    def __init__(self, sm, prefix=3, device="cuda:0"):
        self.prefix = prefix
        self.device = device
        if sm is not None:
            # Compute mean and variance based on the provided poses
            self.pose_subjects = sm.pose_subjects
            # if 'CAESAR' in name or 'Tpose' in name or 'ReachUp' in name]
            all_samples = [p[prefix:] for qsub in self.pose_subjects
                           for name, p in zip(qsub['pose_fnames'], qsub['pose_parms'])]
            self.priors = {'Generic': self.create_prior_from_samples(all_samples)}
        else:
            # Load pre-computed mean and variance
            dat = pkl.load(open('assets/pose_prior.pkl', 'rb'))
            self.priors = {'Generic': ThMahalanobis(dat['mean'],
                                                    dat['precision'],
                                                    self.prefix, self.device)}

    def create_prior_from_samples(self, samples):
        from sklearn.covariance import GraphicalLassoCV

        model = GraphicalLassoCV()
        model.fit(np.asarray(samples))
        return ThMahalanobis(np.asarray(samples).mean(axis=0),
                             np.linalg.cholesky(model.precision_),
                             self.prefix, self.device)

    def __getitem__(self, pid):
        if pid not in self.priors:
            samples = [p[self.prefix:] for qsub in self.pose_subjects
                       for name, p in zip(qsub['pose_fnames'], qsub['pose_parms'])
                       if pid in name.lower()]
            self.priors[pid] = self.priors['Generic'] if len(samples) < 3 \
                               else self.create_prior_from_samples(samples)

        return self.priors[pid]