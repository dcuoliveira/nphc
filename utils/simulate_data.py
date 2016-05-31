import numpy as np

# ## Major key for exp kernel:
# ### Since hMax=40 encodes the support, we ensure \beta is not too small for estimation
# Criterion on exp kernel gives us $\beta_{\min}$ such that $$\exp(-\mbox{hMax} \times \beta_\min) = 10^{-4}$$

def args2params(mode, symmetric):

    hMax = 40
    from math import log
    beta_min = log(1000) / hMax

    if 'd10_sym' in mode:
        d = 10
        mu = 0.0001 * np.ones(d)
        Alpha = np.zeros((d,d))
        Beta = np.zeros((d,d))
        Alpha[:d/2,:d/2] += 1.
        Alpha[d/2:,d/2:] += 1.
        Beta[:d/2,:d/2] += 1000*beta_min
        Beta[d/2:,d/2:] += 10*beta_min
        if symmetric == 2:
            Alpha[6:8,:3] += 3.
            Beta[6:8,:3] += 100*beta_min
        Alpha = .5*(Alpha+Alpha.T)
        Gamma = .5*Alpha
        Beta = .5*(Beta + Beta.T)
        Alpha /= 12

    elif mode == 'd10_nonsym_1':
        d = 10
        mu = 0.0001 * np.ones(d)
        Alpha = np.zeros((d,d))
        Beta = np.zeros((d,d))
        for i in range(5):
            for j in range(5):
                if i <= j:
                    Alpha[i][j] = 1.
                    Beta[i][j] = 1000*beta_min
        for i in range(5,10):
            for j in range(5,10):
                if i >= j:
                    Alpha[i][j] = 1.
                    Beta[i][j] = 10*beta_min
        Gamma = Alpha.copy()
        Alpha /= 6

    elif mode == 'd10_nonsym_2':
        d = 10
        mu = 0.0001 * np.ones(d)
        Alpha = np.zeros((d,d))
        Gamma = np.zeros((d,d))
        for i in range(5):
            for j in range(5):
                if i <= j:
                    Alpha[i][j] = 1.
                    Gamma[i][j] = 1000*beta_min
        for i in range(5,10):
            for j in range(5,10):
                if i >= j:
                    Alpha[i][j] = 1.
                    Gamma[i][j] = 10*beta_min
        Gamma *= .1
        Beta = Alpha.copy()
        Alpha /= 6

    elif 'd100_sym' in mode:
        d = 100
        mu = 0.0001 * np.ones(d)
        Alpha = np.zeros((d,d))
        Beta = np.zeros((d,d))
        Alpha[:d/2,:d/2] += 1.
        Alpha[d/2:,d/2:] += 1.
        Beta[:d/2,:d/2] += 1000*beta_min
        Beta[d/2:,d/2:] += 10*beta_min
        if symmetric == 2:
            Alpha[60:70,10:20] += 3.
            Beta[60:70,10:20] += 100*beta_min
        Alpha = .5*(Alpha+Alpha.T)
        Beta = .5*(Beta + Beta.T)
        Gamma = .5*Alpha
        Alpha /= 120

    elif mode == 'd100_nonsym_1':
        d = 100
        mu = 0.0001 * np.ones(d)
        Alpha = np.zeros((d,d))
        Beta = np.zeros((d,d))
        for i in range(50):
            for j in range(50):
                if i <= j:
                    Alpha[i][j] = 1.
                    Beta[i][j] = 10*beta_min
        for i in range(51,80):
            for j in range(51,80):
                if i >= j:
                    Alpha[i][j] = 1.
                    Beta[i][j] = 100.*beta_min
        for i in range(81,100):
            for j in range(81,100):
                if i <= j:
                    Alpha[i][j] = 1.
                    Beta[i][j] = 1000.*beta_min
        Gamma = Alpha.copy()
        Alpha /= 40

    elif mode == 'd100_nonsym_2':
        d = 100
        mu = 0.0001 * np.ones(d)
        Alpha = np.zeros((d,d))
        Gamma = np.zeros((d,d))
        for i in range(50):
            for j in range(50):
                if i <= j:
                    Alpha[i][j] = 1.
                    Gamma[i][j] = 10*beta_min
        for i in range(51,80):
            for j in range(51,80):
                if i >= j:
                    Alpha[i][j] = 1.
                    Gamma[i][j] = 100.*beta_min
        for i in range(81,100):
            for j in range(81,100):
                if i <= j:
                    Alpha[i][j] = 1.
                    Gamma[i][j] = 1000.*beta_min
        Gamma *= .1
        Beta = Alpha.copy()
        Alpha /= 40

    return mu, Alpha, Beta, Gamma


def params2kernels(kernel, Alpha, Beta, Gamma):

    import mlpp.pp.hawkes as hk
    from mlpp.base.utils import TimeFunction

    if kernel == 'exp':
        kernels = [[hk.HawkesKernelExp(a, b) for (a, b) in zip(a_list, b_list)] for (a_list, b_list) in zip(Alpha, Beta)]

    elif kernel == 'plaw':
        def kernel_plaw(alpha,beta,gamma,support=-1):
            """
            Alternative definition.
            phi(t) = alpha * beta / (1 + beta t) ** (1 + gamma)
            """
            if beta > 0:
                return hk.HawkesKernelPowerLaw(alpha/(beta**gamma),1./beta,1.+gamma,support)
            else:
                return hk.HawkesKernelPowerLaw(0.,1.,1.,support)
        kernels = [[kernel_plaw(a*g, b, g, -1) for (a, b, g) in zip(a_list, b_list, g_list)] for (a_list, b_list, g_list) in zip(Alpha, Beta, Gamma)]

    elif kernel == 'rect':
        def kernel_rect(alpha, beta, gamma):
            if beta > 0:
                T = np.array([0, gamma, gamma + 1./beta ], dtype=float)
                Y = np.array([0, alpha*beta,0], dtype=float)
                tf = TimeFunction([T, Y], inter_mode=TimeFunction.InterConstRight,dt=0.0001)
                return hk.HawkesKernelTimeFunc(tf)
            else:
                T = np.array([0, 1, 1.5 ], dtype=float)
                Y = np.array([0, 0, 0], dtype=float)
                tf = TimeFunction([T, Y], inter_mode=TimeFunction.InterConstRight)
                return hk.HawkesKernelTimeFunc(tf)
        kernels = [[kernel_rect(a, b, g) for (a, b, g) in zip(a_list, b_list, g_list)] for (a_list, b_list, g_list) in zip(Alpha, Beta, Gamma)]

    return kernels


def simulate_and_compute_cumul(mu, kernels, Alpha, T, hM=20):
    import mlpp.pp.hawkes as hk
    h = hk.Hawkes(kernels=kernels, mus=list(mu))
    h.simulate(T)
    # use the class Cumulants
    from cumulants import Cumulants
    N = h.get_full_process()
    cumul = Cumulants(N,hMax=hM)
    # compute everything
    from scipy.linalg import inv
    d = Alpha.shape[0]
    R_true = inv(np.eye(d)-Alpha)
    cumul.set_R_true(R_true)
    cumul.set_all()

    from metrics import rel_err
    print("rel_err on C = ", rel_err(cumul.C_th,cumul.C))
    print("rel_err on K_c = ", rel_err(cumul.K_c_th,cumul.K_c))

    return cumul


def save(cumul, Alpha, Beta, Gamma, kernel, mode, T, with_params=True, without_N=False, suffix=''):

    from math import log10
    import gzip, pickle
    name = kernel + '_' + mode + '_log10T' + str(int(log10(T)))

    # Create folders if they don't exist yet
    dir_name = '../datasets/' + kernel
    import os
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    if with_params and without_N:
        tmp = cumul.N.copy()
        cumul.N = None
        data = (cumul,Alpha,Beta,Gamma)
        f = gzip.open(dir_name + '/' + name + '_with_params_without_N' + suffix + '.pkl.gz','wb')
        pickle.dump(data, f, protocol=2)
        f.close()
        cumul.N = tmp

    elif with_params and not without_N:
        data = (cumul,Alpha,Beta,Gamma)
        f = gzip.open(dir_name + '/' + name + '_with_params' + suffix + '.pkl.gz','wb')
        pickle.dump(data, f, protocol=2)
        f.close()

    elif not with_params and without_N:
        tmp = cumul.N.copy()
        cumul.N = None
        f = gzip.open(dir_name + '/' + name + '_without_N' + suffix + '.pkl.gz','wb')
        pickle.dump(cumul, f, protocol=2)
        f.close()
        cumul.N = tmp

    elif not with_params and not without_N:
        f = gzip.open(dir_name + '/' + name + suffix + '.pkl.gz','wb')
        pickle.dump(cumul, f, protocol=2)
        f.close()


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-k",help="Choose a kernel among: 'exp', 'rect' or 'plaw'.",type=str,choices=['exp','rect','plaw'])
    parser.add_argument("-d",help="Choose the dimension of the process: 10 or 100.",type=int,choices=[10,100])
    parser.add_argument("-s",help="Simulate either from a symmetric (2), more complex symmetric (3), nonsymmetric 1 (0) or nonsymmetric 2 (1) kernel matrix.",type=int,choices=[0,1,2,3])
    parser.add_argument("-t",help="log_10 of the length of the simulation ie '3' gives T=1000",type=int,choices=[3,4,5,6,7,8,9,10])
    args = parser.parse_args()


    ## Parse arguments

    if args.k is None:
        kernel = 'exp'
    else:
        kernel = args.k

    if args.d is None:
        d = 10
    else:
        d = args.d

    if args.s is None:
        symmetric = 1
    else:
        symmetric = args.s

    if args.t is None:
        T = 1e5
    else:
        T = 10**args.t

    if symmetric == 0:
        mode = 'd' + str(d) + '_nonsym_1'
    elif symmetric == 1:
        mode = 'd' + str(d) + '_nonsym_2'
    elif symmetric == 2:
        mode = 'd' + str(d) + '_sym'
    elif symmetric == 3:
        mode = 'd' + str(d) + '_sym_hard'

    mu, Alpha, Beta, Gamma = args2params(mode, symmetric)

    kernels = params2kernels(kernel, Alpha, Beta, Gamma)

    cumul = simulate_and_compute_cumul(mu, kernels, Alpha, T, 20)

    save(cumul, Alpha, Beta, Gamma, kernel, mode, T)
