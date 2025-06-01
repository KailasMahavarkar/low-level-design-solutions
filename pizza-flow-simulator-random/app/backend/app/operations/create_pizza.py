from .base_class import OperationBase
from models.operations import Operation, OperationStatus
from models.tasks import Task
from controllers.events import EventsController
from logs import logger
from ws import ws

class OperationCreatePizza(OperationBase):
    ''' Controller for the create of a pizza '''
    identifier = 'create_pizza'
    all_tasks = ['make_dough', 'add_toppings', 'bake_pizza', 'deliver_pizza']
    
    def __init__(self, op_uuid: str = None):
        super().__init__(op_uuid)

    async def start(self, parameters: dict, rfa_id: str = None) -> Operation:
        ''' Start the operation '''
        logger.info(f"Starting create pizza operation with parameters: {parameters}")
        
        # Create the operation
        operation = Operation(
            operation=self.identifier,
            parameters=parameters,
            status=OperationStatus.pending,
            rfa_id=str(rfa_id) if rfa_id else None
        )
        self.save_operation(operation)
        await EventsController.create_event('system', "started_pizza_creation", {'region': parameters['region'], 'status': OperationStatus.pending, 'tier': parameters['tier'], 'operation_id': operation.uuid})
        
        # Get the region from parameters
        region = parameters.get('region', 'eu-west-3')  # Default to eu-west-3 if not specified
        
        # Create tasks for the pizza making process
        # 1. Make dough task
        dough_task = Task(
            operation_id=operation.uuid,
            task_id=1,
            region=region,
            status=OperationStatus.pending,
            task='make_dough',
            parameters={
                'name': parameters['name'],
                'ingredients': self.get_ingredients_for_tier(parameters['tier'])
            }
        )
        await self.save_task(dough_task)
        
        # 2. Add toppings task
        toppings_task = Task(
            operation_id=operation.uuid,
            task_id=2,
            region=region,
            status=OperationStatus.pending,
            task='add_toppings',
            parameters={
                'name': parameters['name'],
                'toppings': self.get_toppings_for_tier(parameters['tier'])
            }
        )
        await self.save_task(toppings_task)
        
        # 3. Bake pizza task
        bake_task = Task(
            operation_id=operation.uuid,
            task_id=3,
            region=region,
            status=OperationStatus.pending,
            task='bake_pizza',
            parameters={
                'name': parameters['name'],
                'temperature': 350,  # Temperature in Celsius
                'time': 12  # Time in minutes
            }
        )
        await self.save_task(bake_task)
        
        # 4. Deliver pizza task
        deliver_task = Task(
            operation_id=operation.uuid,
            task_id=4,
            region=region,
            status=OperationStatus.pending,
            task='deliver_pizza',
            parameters={
                'name': parameters['name'],
                'delivery_address': parameters.get('delivery_address', 'Customer Address')
            }
        )
        await self.save_task(deliver_task)

        # Notify the customer via WebSocket
        try:
            await ws.emit('pizza_update', {'operation_id': operation.uuid, 'status': 'order_accepted'})
        except Exception as e:
            logger.error(f"Error sending WebSocket update: {e}")
        return operation
    
    def get_ingredients_for_tier(self, tier: str) -> dict:
        """Get ingredients based on the pizza tier"""
        ingredients = {
            'flour': 500,  # grams
            'water': 300,  # ml
            'yeast': 10,   # grams
            'salt': 10,    # grams
            'olive_oil': 15  # ml
        }
        
        # Premium pizzas get extra ingredients
        if tier == 'premium':
            ingredients['special_flour'] = 100
        
        return ingredients
    
    def get_toppings_for_tier(self, tier: str) -> list:
        """Get toppings based on the pizza tier"""
        # Base toppings for all pizzas
        toppings = ['tomato_sauce', 'mozzarella']
        
        # Add toppings based on tier
        if tier == 'standard':
            toppings.extend(['basil'])
        elif tier == 'premium':
            toppings.extend(['basil', 'parmesan', 'truffle_oil'])
        
        return toppings
        
    def dependencies_for(self, task_id: str):
        '''
        Get the dependencies for a task.
        Given a task name, return the name of the tasks that need to be completed before it can start
        ie {'task1': ['task2', 'task3']} -> Task1 has to be executed after task2 and task3
        '''
        deps = {
            'add_toppings': ['make_dough'],     # Can only add toppings after making dough
            'bake_pizza': ['add_toppings'],     # Can only bake after adding toppings
            'deliver_pizza': ['bake_pizza']     # Can only deliver after baking
        }
        return deps.get(task_id, [])
        
    async def on_all_task_completed(self, operation: Operation) -> None:
        ''' All tasks completed for this pizza operation '''
        logger.info(f'All tasks completed for pizza operation {operation.uuid}')
        # Send a final notification that the pizza has been delivered
        try:
            await ws.emit('pizza_update', {
                'operation_id': operation.uuid, 
                'status': 'completed',
                'message': f"Your {operation.parameters.get('name', 'pizza')} pizza has been delivered!"
            })
        except Exception as e:
            logger.error(f"Error sending WebSocket update: {e}")
        return