import time
from logs import logger

_pizzas_baking = {}

class AsyncOven():
    ''' Represents an oven '''
    def __init__(self):
        pass

    def bake(self, pizza_name: str, temperature: int, time_to_bake: int) -> str:
        ''' Bake the pizza '''
        if pizza_name in _pizzas_baking:
            raise Exception('Already baking')
        if len(_pizzas_baking) >= 3:
            raise Exception('Oven is full')
        _pizzas_baking[pizza_name] = {
            'temperature': temperature,
            'time_to_bake': time_to_bake,
            'start_time': time.time()
        }
        logger.info(f'Baking pizza {pizza_name} at {temperature} degrees for {time_to_bake} seconds')
        return 'done'
    
    def check(self, pizza_name: str) -> str:
        ''' Check the pizza '''
        if pizza_name not in _pizzas_baking:
            raise Exception('Pizza not baking')
        pizza = _pizzas_baking[pizza_name]
        elapsed_time = time.time() - pizza['start_time']
        if elapsed_time < pizza['time_to_bake']:
            return 'baking'
        return 'done'
    
    def remove(self, pizza_name: str) -> str:
        ''' Remove the pizza '''
        if pizza_name not in _pizzas_baking:
            raise Exception('Pizza not baking')
        del _pizzas_baking[pizza_name]
        return 'removed'