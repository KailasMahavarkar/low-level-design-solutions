from typing import Dict
import time
from logs import logger

class Pizzaiolo():
    ''' Represents the pizzaiolo '''
    def __init__(self):
        pass

    def make_dough(self, ingredients: Dict[str, int]) -> str:
        ''' Make the dough '''
        logger.info(f'Making dough with ingredients: {ingredients}')
        time.sleep(1)
        return 'done'
    
    def add_toppings(self, toppings: list) -> str:
        ''' Add toppings to the pizza '''
        logger.info(f'Adding toppings to pizza: {toppings}')
        time.sleep(1.5)  # Adding toppings takes a bit longer
        return 'done'
    
    def bake_pizza(self, temperature: int, time_minutes: int) -> str:
        ''' Bake the pizza at specified temperature for specified time '''
        logger.info(f'Baking pizza at {temperature}°C for {time_minutes} minutes')
        # Simulate baking time (scaled down)
        time.sleep(2)
        logger.info(f'Pizza baked successfully')
        return 'done'
    
    def deliver_pizza(self, delivery_address: str) -> str:
        ''' Deliver the pizza to the specified address '''
        logger.info(f'Delivering pizza to: {delivery_address}')
        time.sleep(3)  # Delivery takes longest
        logger.info(f'Pizza successfully delivered to {delivery_address}')
        return 'done'