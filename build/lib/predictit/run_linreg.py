import numpy as np
from scipy import optimize as sco
import pickle
import statsmodels.api as sm
from statsmodels.tools.tools import add_constant


def load_object(file_name):
    """load the pickled object"""
    with open(file_name, 'rb') as f:
        return pickle.load(f)


def view_data(data_path):
    data = load_object(data_path)
    prices = data['prices']
    names = data['features']['names']
    features = data['features']['values']
    print(prices.shape)
    print(names)
    print(features.shape)
    return prices, features


class Strategy():
    
    def __init__(self):
        """
        :NUM_STOCKS: number of assets in universe
        :TIMESTEPS: current tick of time steps we have just finished. Defaults to 756
        :relevant_factors: list of indices of the factors to use in model. 
        :generated_factors: list of indices to calculate the moment of. 
        
        """
        self.prices, self.features = view_data('./C3_train.pkl')
        self.NUM_STOCKS = self.features.shape[1]
        self.TIMESTEPS = self.features.shape[0]
        
        self.daily_rf_rate = np.log(1.025)/252
        self.log_ret = list(np.diff(np.log(self.prices), axis=0) - self.daily_rf_rate)[1:]
        print("log_ret")
        print(np.array(self.log_ret).shape)
        self.relevant_factors = np.array([4])
        self.generated_factors = np.array([4])
        
        assert set(self.generated_factors).issubset(set(self.relevant_factors))

        # Update price data and values as arrays for fast append.
        self.price_values = list(self.prices[2:])
        self.values = self.features[:,:,self.relevant_factors]
        
        self.init_factors()
        
        
    def init_factors(self):
        """
        Calculates the historical moments of all factors in generated_factors.
        
        :return: numpy array of factors with one missing dimension
        """
        
        print("Existing Factor Size:")
        print(self.values[1:].shape)
        print("Additional Moment Factor Size:")
        print(np.diff(self.features[:,:,self.generated_factors], axis=0).shape)
        
        # Appends the two calculated factor arrays
        self.values = np.concatenate((self.values[1:], 
                                      np.diff(self.features[:,:,self.generated_factors], 
                                              axis=0)), 
                                      axis=2)
        print("Final Factor Size:")
        print(self.values.shape)
    
    
    def run_regression(self, regression: 'statsmodels.RegressionModel', 
                       response, predictors, **kwargs):
        """
        Runs a target regression on the returns dataset. 
        
        :regression: regression model to be used
        :response: numpy array of response values
        :predictors: numpy array of predictor values
        
        :ret: list of statsmodels.Results
        """
        models = []
        for i in np.arange(self.NUM_STOCKS):
            model = regression(response[i::self.NUM_STOCKS], 
                               predictors[i::self.NUM_STOCKS], 
                               kwargs).fit()
            models.append(model)
        return models
    
    
    def delta_func(self, factor, past_factors, **kwargs):
        """
        This function serves as a simple differencing from the 
        current factor and the most latest past factor. 
        
        First-order moment
        
        :factor: (NUM_STOCKS x 1) array of values
        :past_factors: (TIMESTEPS x NUM_STOCKS)
        """
    
        return np.subtract(factor, past_factors[-1, :].flatten())
    
        
    def update_factor(self, fac_idx, factor, func):
        """
        Updates the factor from its previous factors using the provided function. 
        
        Ex: used to derive RSI deltas
        
        :fac_idx: idx in data of desired factor
        :factor: (NUM_STOCKS x 1) array of values
        :func: function to apply on the factor array. 
        """
        print(self.values[:, :, list(self.generated_factors).index(fac_idx)].shape)
        update = func(factor, self.values[:, :, list(self.generated_factors).index(fac_idx)])
        return update
    
        
    def handle_update(self, inx, price, factors):
        """
        This function has two functionalities: 
        
        1. Update the price return for last period to use for regression.
        2. Calculate an Estimate based on the new factors
        
        Args:
            inx: zero-based inx in days
            price: [num_assets, ]
            factors: [num_assets, num_factors]
        Return:
            allocation: [num_assets, ]
        """
        # Update Price if it isn't the first iteration
        if inx != 0:
            log_ret = np.log(np.divide((price), self.price_values[-1])) - self.daily_rf_rate
            self.log_ret.append(log_ret)
            self.price_values.append(price)
        
         
        # Update Factors

            
        # Calculate new Estimation
        
        response = np.array(self.log_ret).flatten()
        constants = np.ones((self.values.shape[0], self.values.shape[1], 1))
        predictors = np.concatenate([self.values, constants], axis=2)
        predictors = predictors.reshape((predictors.shape[0]*predictors.shape[1], predictors.shape[2]))
        print("Constants shape")
        print(constants.shape)
        print(predictors.shape)
        print(response.shape)
        models = self.run_regression(sm.OLS, response, predictors)
        # Gather Betas
        mat_beta = np.array([x.params[:-1] for x in models])
        # Gather Residual
        vec_resid = np.array([x.resid for x in models])
        # Calculate Residual covariance
        mat_resid_cov = np.cov(vec_resid)
        # Calculate variance from diagonal
        vec_vol = np.diagonal(mat_resid_cov)
        # Calculate factor covariance estimate
        reshape_value_dim = self.values.shape[0]*self.values.shape[1],self.values.shape[2]
        mat_cov_factor = np.cov(self.values.reshape(reshape_value_dim).T)
        # Compose the covariance estimate
        mat_cov_est = np.matmul(np.matmul(mat_beta, mat_cov_factor), mat_beta.T)
        

        # Calculated expected log returns
        
        # Update RSI Moment Factor
        vec_fac_update = np.array([factors[:, 4], self.update_factor(4, factors[:, 4], self.delta_func)]).T
        print(self.values.shape)
        print(vec_fac_update.shape)
        print("%s%s" % (self.values.shape, vec_fac_update.shape))
        self.values = np.concatenate([self.values, np.expand_dims(vec_fac_update, axis=0)], axis=0)    
        
        vec_fac_update_constants = np.ones((1, self.NUM_STOCKS))
        print(vec_fac_update_constants.T.shape)
        print(vec_fac_update.shape)
        print("hhhh")
        vec_fac_update = np.concatenate([vec_fac_update.T, vec_fac_update_constants], axis=0)
        
        
        mat_beta_c = np.array([x.params for x in models])
        print(mat_beta_c.shape)
        mean_returns = np.einsum('ij,ji->i', mat_beta_c, vec_fac_update)
        print(mean_returns.shape)
        print("45234435") 
        
        portfolio = np.matmul(np.linalg.inv(mat_cov_est), mean_returns)
        print(portfolio.shape)
        return portfolio
        
#         self.values = np.concatenate(self.values, factors
        
#         print(mat_cov_estimate.shape)
        
        
        
        # Add factir array on DONT FORGET####
                                     
                                     
                                     
                                     
#         print(self.run_regression(sm.OLS, [1, 2, 3, 8, 5], [1, 2, 3, 4, 5], ))
        
        
        
#         print(past_prices.shape)
#         print(past_features.shape)
        
#         return np.load('./portfolio.npy')

        # 1,2,3...n porfolio
#         return np.arange(price.shape[0]).astype(float)
        
        # All ones portfolio
#         return np.ones(price.shape[0]).astype(float)

        # Random Uniform Portfolio
        return np.random.rand(price.shape[0])

        # Random Uniform Portfolio
#         return self.portfolios[inx-1].flatten() if inx != 0 else np.ones(680)
        