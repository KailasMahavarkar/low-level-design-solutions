from models.tasks import Task
from models.task_execution import TaskExecution, TaskStatus
from tasks import registry
from logs import logger
from interfaces.pizzaiolo import Pizzaiolo

@registry.register()
class MakeDoughTask(Task):
    ''' Task to make the dough '''
    identifier = 'make_dough'

    def run(self, execution: TaskExecution):
        ''' Run the task '''
        pizza_name = execution.parameters['name']
        logger.info(f'Making dough for pizza {pizza_name}')

        pizzaiolo = Pizzaiolo()
        pizzaiolo.make_dough(execution.parameters['ingredients'])

        execution.status = TaskStatus.completed
        return execution

@registry.register()
class AddToppingsTask(Task):
    ''' Task to add toppings to the pizza '''
    identifier = 'add_toppings'

    def run(self, execution: TaskExecution):
        ''' Run the task '''
        pizza_name = execution.parameters['name']
        logger.info(f'Adding toppings to pizza {pizza_name}')

        pizzaiolo = Pizzaiolo()
        pizzaiolo.add_toppings(execution.parameters['toppings'])

        execution.status = TaskStatus.completed
        return execution

@registry.register()
class BakePizzaTask(Task):
    ''' Task to bake the pizza '''
    identifier = 'bake_pizza'

    def run(self, execution: TaskExecution):
        ''' Run the task '''
        pizza_name = execution.parameters['name']
        logger.info(f'Baking pizza {pizza_name}')

        pizzaiolo = Pizzaiolo()
        pizzaiolo.bake_pizza(execution.parameters['temperature'], execution.parameters['time'])

        execution.status = TaskStatus.completed
        return execution

@registry.register()
class DeliverPizzaTask(Task):
    ''' Task to deliver the pizza '''
    identifier = 'deliver_pizza'

    def run(self, execution: TaskExecution):
        ''' Run the task '''
        pizza_name = execution.parameters['name']
        delivery_address = execution.parameters['delivery_address']
        logger.info(f'Delivering pizza {pizza_name} to {delivery_address}')

        pizzaiolo = Pizzaiolo()
        pizzaiolo.deliver_pizza(delivery_address)

        execution.status = TaskStatus.completed
        return execution