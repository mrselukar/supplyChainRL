import gym
from gym import error, spaces, utils
from gym.utils import seeding
import copy
import numpy as np

class SupplyChainv0(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,products = 1, low_val = 0 , high_val = 10000, lam = 3000, ep_len = 1000):
        super(SupplyChainv0, self).__init__()
        N_DISCRETE_ACTIONS = 1
        N_CHANNELS = 1 #NO OF FEATURES
        HEIGHT = 1
        WIDTH = 1
        self.action_space = spaces.Box(low=low_val, high=high_val, shape=(HEIGHT, WIDTH, N_CHANNELS))
        # Example for using image as input:
        self.observation_space = spaces.Box(low=low_val, high=high_val, shape=(HEIGHT, WIDTH, N_CHANNELS))
        
        self.QuantityInit = [lam for _ in range(products)]
        self.QuantityCurr = copy.deepcopy(self.QuantityInit)
        self.G = [3 for _ in range(products)]
        self.F = [1 for _ in range(products)]
        self.LifeCycle = [3 for _ in range(products)]
        self.LeadTime = [1 for _ in range(products)]
        self.LifeShelf = []
        
        for LC, LT in zip(self.LifeCycle,self.LeadTime):
            self.LifeShelf.append(LC - LT)
            
        self.time = 0
        self.done = False
        self.orders = [[np.random.poisson(size = ep_len, lam=lam)] for _ in range(products)]
        self.spoilageRate = [0 for _ in range(products)]
        self.costOfStorage = [math.floor(lam*1.2) for _ in range(products)]
        self.expiredProducts = [0 for _ in range(products)]
        self.shortageInDemand = [0 for _ in range(products)]
        
        
    def _get_spoilage(self):
        pass
    
    def _get_cost_of_storage(self):
        return self.QuantityCurr
    
    def _get_next_demand(self):
        retval = [np.random.poisson(size = 1, lam=lam)for _ in range(products)]
        return retval
    
    def step(self, action):
        self.time += 1
        
        
                
    
    
    def reset(self):
        self.QuantityCurr = copy.deepcopy(self.QuantityInit)
        self.time = 0
        self.done = False
        self.orders = [[np.random.poisson(size = ep_len, lam=lam)] for _ in range(products)]

        
    
    def render(self, mode='human', close=False):
        pass
    