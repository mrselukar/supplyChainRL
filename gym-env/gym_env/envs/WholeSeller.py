import numpy as np

class WholeSeller():
    
    def __init__(self, no_products, lead_times, life_cycles, lambd_a):
        self.no_products = no_products 
        self.lead_times = lead_times
        self.life_cycles = life_cycles
        self.lam = lambd_a
        
        self.order_history = []
        for i in range(self.no_products):
            order_h = [ self.lam for _ in range(self.lead_times[i])] 
            self.order_history.append(order_h)
        
        self.time = 0
        
    def orderIn(self, order_qty):
        for i in range(self.no_products):
            self.order_history[i][self.time%self.lead_times] = order_qty
            
            
    def step(self):
        time += 1
    
    def reset(self):
        self.time = 0
        del self.order_history
        self.order_history = []
        for i in ragne(self.no_products):
            order_h = [ self.lam for _ in range(self.lead_times[i])] 
            self.order_history.append(order_h)
        
        
    def deliver(self, time):
        if time != self.time:
            raise Exception('Time of Wholeseller is not the same as of retailer : {} != {}'.format(self.time , time))
            
        retval = []
        for i in range(self.no_products):
            retval.append(self.order_history[i][self.time%self.lead_times])
            self.order_history[i][self.time%self.lead_times] = 0
            
        return retval
            
            
        
        
    