import gym
from gym import error, spaces, utils
from gym.utils import seeding
import copy
import numpy as np
from WholeSeller import WholeSeller
import math

class SupplyChainv0(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,products = 1, low_val = 0 , high_val = 10000, lam = 3000, ep_len = 1000):
        super(SupplyChainv0, self).__init__()
        N_DISCRETE_ACTIONS = 1
        N_CHANNELS = 1 #NO OF FEATURES
        HEIGHT = 1
        WIDTH = 1
        self.products = products
        self.action_space = spaces.Box(low=low_val, high=high_val, shape=(HEIGHT, WIDTH, N_CHANNELS), dtype= np.float32)
        # Example for using image as input:
        self.observation_space = spaces.Box(low=low_val, high=high_val, shape=(HEIGHT, WIDTH, N_CHANNELS), dtype= np.float32)
        
        self.QuantityInit = [lam for _ in range(products)]
        self.QuantityCurr = copy.deepcopy(self.QuantityInit)
        
        """
        Multiplying by random numbers [1, 5] and then taking floors should work but make sure the seed is set everytime
        (To keep consistency make sure to genereate the random numbers First)
        For G, F, LifeCycle and LeadTime
        """
        
        ## G[i] is the spoilage cost of a product
        self.G = [3 for _ in range(products)]
        
        ## F[i] is the shortage cost of a product[i]
        self.F = [1 for _ in range(products)]
        
        ## LifeCycle[i] is the total time for which product is good 
        self.LifeCycle = [3 for _ in range(products)]
        
        ## Leadtime[i] is the time it takes for the product to reach the retailer once the order is placed 
        self.LeadTime = [1 for _ in range(products)]
        
        ## LifeShelf[i] is the time for which a new shipment of product is good before it needs to be thrown out
        self.LifeShelf = []
        
        ## ProductLifeDB stores the expired date of the product 
        ## productLifeDB[i][j] tells us how many (Quantity) of product[i] are going to expire in j days time 
        ## E.G productLifeDB[i][0] tells the quantity of product[i] that will be thrown out today
        self.productLifeDB = []
        
        for LC, LT in zip(self.LifeCycle,self.LeadTime):
            self.LifeShelf.append(LC - LT)
            self.productLifeDB.append([0 for _ in range(LC - LT)])
            
        self.time = 0
        for i in range(products):
            self.productLifeDB[i][(self.time + self.LifeShelf[i]-1)%(self.LifeShelf[i])] = self.QuantityCurr[i]
            
        
        self.wholeSeller = WholeSeller(no_products = products, lead_times = self.LeadTime , life_cycles = self.LifeCycle, lambd_a = lam)
        self.done = False
        self.orders = [[np.random.poisson(size = ep_len, lam=lam)] for _ in range(products)]
        self.spoilageRate = [0 for _ in range(products)]
        self.costOfStorage = [math.floor(lam*1.2) for _ in range(products)]
        self.expiredProducts = [0 for _ in range(products)]
        self.shortageInDemand = [0 for _ in range(products)]
        

    ##--------------------------------------------------------------------------------------------------------------------------------------------
    
    
    def _get_spoilage(self):
        retval = []
        for i in range(self.products):
            retval.append((1.2*self.expiredProducts[i] + 0.3*self.shortageInDemand[i]) / (self.QuantityCurr[i]+1))
        return retval 
    
    
    ##--------------------------------------------------------------------------------------------------------------------------------------------
    
    
    def _get_cost_of_storage(self):
        return self.QuantityCurr
    
    
    ##--------------------------------------------------------------------------------------------------------------------------------------------
    
    
    def _get_next_demand(self):
        retval = [np.random.poisson(size = 1, lam=lam)for _ in range(products)]
        return retval
    
    
    ##--------------------------------------------------------------------------------------------------------------------------------------------
    
       
    def step(self, action):
        delivery = self.wholeSeller.deliver(self.time)
        for i in range(no_products):
            self.QuantityCurr[i] += delivery[i]
            self.productLifeDB[i][(self.time + self.LifeShelf[i])%(self.LifeShelf[i]+1)] += delivery[i]
            
        
        self.costOfStorage = self._get_cost_of_storage();
        D  =  []
        for i in range(self.products):
            D.append(self.orders[i][self.time])
            if self.QuantityCurr[i] - D[i] >= 0:
                #Demand Met
                self.QuantityCurr[i] -= D[i]
                self.shortageInDemand[i] = 0
            else:
                self.shortageInDemand[i] = D[i] - self.QuantityCurr[i]
                self.QuantityCurr[i] = 0
                
        #Calculatin Expired Goods
        for i in range(self.products):
            surplus = self.productLifeDB[i][(self.time + self.LifeShelf[i])%(self.LifeShelf[i]+1)]
            if surplus > 0:
                self.expiredProducts[i] = surplus 
                self.QuantityCurr[i] -= surplus
                self.productLifeDB[i][(self.time + self.LifeShelf[i])%(self.LifeShelf[i]+1)] = delivery[i]
            else:
                self.expiredProducts[i] = 0
            
        self.spoilageRate = self._get_spoilage()    
        self.wholeSeller.step()
        self.time += 1
        """
        Logic to handle aging of goods
        """
        self.wholeSeller.orderIn(action)  
        if self.time > self.ep_len:
            self.done = True
            
        info = [self._get_spoilage, self._get_cost_of_storage]
        
        #return observation, reward, done, info
        return self._get_state(), self._get_reward(), self.done, info
        
    ##--------------------------------------------------------------------------------------------------------------------------------------------            
    
    
    def reset(self):
        self.QuantityCurr = copy.deepcopy(self.QuantityInit)
        self.time = 0
        self.done = False
        self.orders = [[np.random.poisson(size = ep_len, lam=lam)] for _ in range(products)]
        
        
        self.productLifeDB = []
        
        for LC, LT in zip(self.LifeCycle,self.LeadTime):
            self.productLifeDB.append([0 for _ in range(LC - LT)])
            
        for i in range(self.products):
            self.productLifeDB[i][(self.time + self.LifeShelf[i]-1)%(self.LifeShelf[i])] = self.QuantityCurr[i]
            
        
        self.wholeSeller.reset()

        self.spoilageRate = [0 for _ in range(self.products)]
        self.costOfStorage = [math.floor(lam*1.2) for _ in range(self.products)]
        self.expiredProducts = [0 for _ in range(self.products)]
        self.shortageInDemand = [0 for _ in range(self.products)]
        
        return self._get_state()
    
    
    ##--------------------------------------------------------------------------------------------------------------------------------------------
    
    
    def _get_state(self):
        return self.QuantityCurr
    
    ##--------------------------------------------------------------------------------------------------------------------------------------------
    
    def _get_reward(self):
        retval = 0
        for i in range(self.products):
            retval += self.G[i]*self.expiredProducts[i] + self.F[i]*self.shortageInDemand[i]            
        return retval
    
    def render(self, mode='human', close=False):
        pass
    





