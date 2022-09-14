import numpy as np
import pandas as pd
import random
import sys
from scipy.stats import norm
from scipy.stats import multivariate_normal
import warnings
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
import matplotlib.pyplot as plt

class corr_mat_generator:
    def __init__(self, annotation, combination, output_file):
        #TODO: Please config the path here
        self.input_annotation = annotation
        self.input_combination = combination
        self.output_path = output_file

    def compute_likelihood(dat, x1_ind, x2_ind, mu_1, mu_2, sigma_1, sigma_2, rho, thresh):
        bvn_mean = np.array([mu_1, mu_2])
        bvn_cov = np.array([[sigma_1 ** 2, sigma_1 * sigma_2 * rho], [sigma_1 * sigma_2 * rho, sigma_2 ** 2]])
        # print(bvn_cov)
        bvn_cov = np.array(
            [[params[2] ** 2, params[2] * params[3] * params[4]], [params[2] * params[3] * params[4], params[3] ** 2]])
        X = np.concatenate((dat.iloc[:, x1_ind].values.reshape(len(dat.iloc[:, x1_ind].values), 1),
                            dat.iloc[:, x2_ind].values.reshape(len(dat.iloc[:, x2_ind].values), 1)), axis=1)
        X_C = np.concatenate((np.maximum(dat.iloc[:, x1_ind].values, thresh[x1_ind - 1]).reshape(
            len(dat.iloc[:, x1_ind].values), 1), np.maximum(dat.iloc[:, x2_ind].values, thresh[x2_ind - 1]).reshape(
            len(dat.iloc[:, x1_ind].values), 1)), axis=1)

        A = np.prod(multivariate_normal.pdf(X, bvn_mean, bvn_cov) ** (
                    (dat.iloc[:, x1_ind].values != 0) * (dat.iloc[:, x2_ind].values != 0)))
        B = np.prod(norm.pdf(X[:, 0], loc=mu_1, scale=sigma_1) ** (
                    (dat.iloc[:, x1_ind].values != 0) * (1 - (dat.iloc[:, x2_ind].values != 0)))) * np.prod(
            norm.cdf(X_C[:, 1],
                     loc=(mu_2 + sigma_2 / sigma_1 * dat.iloc[:, x1_ind] * rho - sigma_2 / sigma_1 * mu_1 * rho),
                     scale=(sigma_2 * np.sqrt(1 - rho ** 2))) ** (
                        (dat.iloc[:, x1_ind].values != 0) * (1 - (dat.iloc[:, x2_ind].values != 0))))
        C = np.prod(norm.pdf(X[:, 1], loc=mu_2, scale=sigma_2) ** (
                    (dat.iloc[:, x2_ind].values != 0) * (1 - (dat.iloc[:, x1_ind].values != 0)))) * np.prod(
            norm.cdf(X_C[:, 0],
                     loc=(mu_1 + sigma_1 / sigma_2 * dat.iloc[:, x2_ind] * rho - sigma_1 / sigma_2 * mu_2 * rho),
                     scale=(sigma_1 * np.sqrt(1 - rho ** 2))) ** (
                        (dat.iloc[:, x2_ind].values != 0) * (1 - (dat.iloc[:, x1_ind].values != 0))))
        D = np.amin((np.prod(multivariate_normal.cdf(X_C, bvn_mean, bvn_cov) ** (
                    (1 - (dat.iloc[:, x1_ind].values != 0)) * (1 - (dat.iloc[:, x2_ind].values != 0)))), 0.00001),
                    axis=0)

        a = A
        b = B
        c = C
        d = D

        # print(bvn_cov)

        log_lkli = np.log(a * b * c * d)

        return log_lkli

    def cal_corr_mat(self):
        #TODO: Please check the input file name here
        dat = pd.read_csv(self.input_combination, sep='\t')
        dat.iloc[:, 1:] = np.log(dat.iloc[:, 1:])

        # Automatically
        thresh = np.amin(dat.iloc[:, 1:], axis=0)
        # Manually
        # thresh = np.array([])

        dat = dat.fillna(0)

        # Placeholder matrix for correlations
        corr_mat = pd.DataFrame(np.zeros([dat.iloc[:, 1:].shape[1], dat.iloc[:, 1:].shape[1]]),
                                index=dat.iloc[:, 1:].columns, columns=dat.iloc[:, 1:].columns)
        corr_mat2 = pd.DataFrame(np.empty([dat.iloc[:, 1:].shape[1], dat.iloc[:, 1:].shape[1]]),
                                 index=dat.iloc[:, 1:].columns, columns=dat.iloc[:, 1:].columns)

        # matrix of common counts
        df = pd.read_excel(xls, self.input_annotation, engine = 'openpyxl')
        df.iloc[:, 1:] = np.log(df.iloc[:, 1:])
        M = (df.iloc[:, 1:].notna()).astype(float)
        common_counts = M.T.dot(M)
        common_corrs = df.iloc[:, 1:].corr()
        corr_mat = df.iloc[:, 1:].corr()
        # removing the diagonal
        np.fill_diagonal(common_counts.values, 0)
        np.fill_diagonal(common_corrs.values, 0)
        np.fill_diagonal(corr_mat.values, 0)

        max_iters = 10000
        lr = 0.00001
        iters = 0
        h = 0.0001


        for z in range(1):
            for f in range(dat.iloc[:, 1:].shape[1]):
                for k in range(dat.iloc[:, 1:].shape[1]):
                    if f < k:
                        x1_ind = f + 1
                        x2_ind = k + 1

                        mu_1_init = np.mean(
                            dat.iloc[(dat.index[(dat.iloc[:, x1_ind] > 0) == True].tolist()), x1_ind].values)
                        mu_2_init = np.mean(
                            dat.iloc[(dat.index[(dat.iloc[:, x2_ind] > 0) == True].tolist()), x2_ind].values)
                        sigma_1_init = np.std(
                            dat.iloc[(dat.index[(dat.iloc[:, x1_ind] > 0) == True].tolist()), x1_ind].values)
                        sigma_2_init = np.std(
                            dat.iloc[(dat.index[(dat.iloc[:, x2_ind] > 0) == True].tolist()), x2_ind].values)
                        rho_init = corr_mat.iloc[f, k]

                        params = np.array([mu_1_init, mu_2_init, sigma_1_init, sigma_2_init, rho_init])
                        params_grad = np.ones([5, ])

                        try:
                            L_trend = [-compute_likelihood(dat, x1_ind, x2_ind, (params[0]), (params[1]), (params[2]),
                                                           (params[3]), (params[4]), thresh)]
                        except:
                            continue

                        while iters < max_iters and params[4] != 1 and params[4] != -1:
                            try:
                                L2 = -compute_likelihood(dat, x1_ind, x2_ind, (params[0] + h), (params[1]), (params[2]),
                                                         (params[3]), (params[4]), thresh)
                                L1 = -compute_likelihood(dat, x1_ind, x2_ind, (params[0]), (params[1]), (params[2]),
                                                         (params[3]), (params[4]), thresh)

                                prev_lklh = L1

                                if np.isnan((L2 - L1) / h):
                                    params_grad[0] = 0
                                    pass
                                else:
                                    params_grad[0] = (L2 - L1) / h

                                L2 = -compute_likelihood(dat, x1_ind, x2_ind, (params[0]), (params[1] + h), (params[2]),
                                                         (params[3]), (params[4]), thresh)
                                L1 = -compute_likelihood(dat, x1_ind, x2_ind, (params[0]), (params[1]), (params[2]),
                                                         (params[3]), (params[4]), thresh)

                                if np.isnan((L2 - L1) / h):
                                    params_grad[1] = 0
                                    pass
                                else:
                                    params_grad[1] = (L2 - L1) / h

                                L2 = -compute_likelihood(dat, x1_ind, x2_ind, (params[0]), (params[1]), (params[2] + h),
                                                         (params[3]), (params[4]), thresh)
                                L1 = -compute_likelihood(dat, x1_ind, x2_ind, (params[0]), (params[1]), (params[2]),
                                                         (params[3]), (params[4]), thresh)

                                if np.isnan((L2 - L1) / h):
                                    params_grad[2] = 0
                                    pass
                                else:
                                    params_grad[2] = (L2 - L1) / h

                                L2 = -compute_likelihood(dat, x1_ind, x2_ind, (params[0]), (params[1]), (params[2]),
                                                         (params[3] + h), (params[4]), thresh)
                                L1 = -compute_likelihood(dat, x1_ind, x2_ind, (params[0]), (params[1]), (params[2]),
                                                         (params[3]), (params[4]), thresh)

                                if np.isnan((L2 - L1) / h):
                                    params_grad[3] = 0
                                    pass
                                else:
                                    params_grad[3] = (L2 - L1) / h

                                L2 = -compute_likelihood(dat, x1_ind, x2_ind, (params[0]), (params[1]), (params[2]),
                                                         (params[3]), (params[4] + h), thresh)
                                L1 = -compute_likelihood(dat, x1_ind, x2_ind, (params[0]), (params[1]), (params[2]),
                                                         (params[3]), (params[4]), thresh)

                                if np.isnan((L2 - L1) / h):
                                    params_grad[4] = 0
                                    pass
                                else:
                                    params_grad[4] = (L2 - L1) / h

                                params += -lr * params_grad
                                params[0] = np.amax([params[0], np.mean(dat.iloc[:, x1_ind].values)])
                                params[1] = np.amax([params[1], np.mean(dat.iloc[:, x2_ind].values)])
                                params[2] = np.amax([params[2], np.std(dat.iloc[:, x1_ind].values)])
                                params[3] = np.amax([params[3], np.std(dat.iloc[:, x2_ind].values)])
                                params[4] = np.amin([np.amax([params[4], -1]), 1])

                                curr_lklh = -compute_likelihood(dat, x1_ind, x2_ind, (params[0]), (params[1]),
                                                                (params[2]), (params[3]), (params[4]), thresh)

                                L_trend.append(curr_lklh)

                                previous_step_size = curr_lklh - prev_lklh

                                iters = iters + 1  # iteration count

                                if L_trend[iters] < L_trend[iters - 1]:
                                    params_opt = params

                            except ValueError:
                                continue

                        # Updating correlation matrix
                        corr_mat.iloc[x1_ind, x2_ind] = corr_mat.iloc[x2_ind, x1_ind] = params_opt[4]

        for f in range(dat.iloc[:, 1:].shape[1]):
            for k in range(dat.iloc[:, 1:].shape[1]):
                if f < k:
                    x1_ind = f + 1
                    x2_ind = k + 1

                    # VC bounds
                    bound_on = [dat.iloc[:, 1:].columns[f], dat.iloc[:, 1:].columns[k]]

                    non_match = [bound_on[0], bound_on[1]]
                    LB = np.zeros([])
                    UB = np.zeros([])
                    K_vec = np.zeros([])
                    for common in dat.iloc[:, 1:].columns:
                        if common in bound_on:
                            pass
                        else:
                            K_vec = np.append(K_vec, np.amin(
                                (common_counts.loc[common, bound_on[0]], common_counts.loc[common, bound_on[1]]),
                                axis=0))
                            ##
                            c = np.sqrt(1 - (corr_mat.loc[bound_on[0], common]) ** 2) * np.sqrt(
                                1 - (corr_mat.loc[bound_on[1], common]) ** 2)

                            lower_bound = np.amax(
                                (corr_mat.loc[bound_on[0], common] * corr_mat.loc[bound_on[1], common] - c, -0.99),
                                axis=0)

                            LB = np.append(LB, lower_bound)

                            upper_bound = np.amin(
                                (corr_mat.loc[bound_on[0], common] * corr_mat.loc[bound_on[1], common] + c, 0.99),
                                axis=0)

                            UB = np.append(UB, upper_bound)

                    # print(LB)
                    # print(UB)
                    # print(K_vec)

                    LB = np.nan_to_num(LB, nan=0)
                    UB = np.nan_to_num(UB, nan=0)
                    K_vec = np.nan_to_num(K_vec, nan=0)

                    K_vec_mod = np.nansum(K_vec, axis=0)

                    LB = LB / K_vec_mod
                    UB = UB / K_vec_mod
                    LB.reshape(LB.shape[0], 1)
                    LB_mod = np.dot(K_vec, LB.reshape(LB.shape[0], 1))
                    UB_mod = np.dot(K_vec, UB.reshape(UB.shape[0], 1))
                    # bounds
                    Lower_bnd = np.nansum(LB_mod, axis=0)
                    # print("Lower bound: " + str(Lower_bnd))
                    Upper_bnd = np.nansum(UB_mod, axis=0)
                    # print("Upper bound: " + str(Upper_bnd))
                    # Updating correlations matrix
                    corr_status_L = (corr_mat.loc[bound_on[0], bound_on[1]] < Lower_bnd)
                    if corr_status_L == True:
                        corr_mat.loc[bound_on[0], bound_on[1]] = corr_mat.loc[bound_on[1], bound_on[0]] = Lower_bnd

                    corr_status_U = (corr_mat.loc[bound_on[0], bound_on[1]] > Upper_bnd)
                    if corr_status_U == True:
                        corr_mat.loc[bound_on[0], bound_on[1]] = corr_mat.loc[bound_on[1], bound_on[0]] = Upper_bnd

                    if np.isnan(corr_mat.loc[bound_on[0], bound_on[1]]) == True:
                        corr_mat2.loc[bound_on[0], bound_on[1]] = corr_mat2.loc[bound_on[1], bound_on[0]] = (
                                    "{" + str(Lower_bnd) + ',' + str(Upper_bnd) + "}")
                    else:
                        corr_mat2.loc[bound_on[0], bound_on[1]] = corr_mat2.loc[bound_on[1], bound_on[0]] = ''

        n = corr_mat2.astype(str)
        n = n.fillna('')
        m = corr_mat.astype(str)
        m = m.replace('nan', '', regex=True)
        corr_mat_final = m + n
        np.fill_diagonal(corr_mat_final.values, 1)

        corr_mat_final.to_csv(self.output_path + "final_corr_output.csv")


if __name__=="__main__":
    corr_mat_gen = corr_mat_generator(sys.argv[1], sys.argv[2], sys.argv[3])
    corr_mat_gen.cal_corr_mat()
