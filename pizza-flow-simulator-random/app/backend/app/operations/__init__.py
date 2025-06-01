from .create_pizza import OperationCreatePizza
from models.operations import Operation

async def start_operation(operation: str, parameters: dict, rfa_id:str=None):
    ''' Start the operation '''
    controller = get_operation_controller(operation)
    if not controller:
        raise Exception(f'Operation {operation} not found')
    return await controller.start(parameters, rfa_id)

def get_operation_controller(operation: str):
    ''' Get the operation controller '''
    if operation == 'create_pizza':
        return OperationCreatePizza()
    return None

async def cancel_operation(operation: Operation):
    ''' Cancel the operation '''
    controller = get_operation_controller(operation.operation)
    if not controller:
        raise Exception(f'Operation {operation.uuid} not found')
    await controller.cancel(operation)

async def delete_operation(operation: Operation):
    ''' Delete the operation '''
    controller = get_operation_controller(operation.operation)
    if not controller:
        raise Exception(f'Operation {operation.uuid} not found')
    controller.delete_operation(operation)

async def schedule_next_tasks_operation(operation: Operation):
    ''' Refresh the schedule '''
    controller = get_operation_controller(operation.operation)
    if not controller:
        raise Exception(f'Operation {operation.uuid} not found')
    await controller.schedule_next_tasks(operation)

async def pause_operation(operation: Operation):
    ''' Delete the operation '''
    controller = get_operation_controller(operation.operation)
    if not controller:
        raise Exception(f'Operation {operation.uuid} not found')
    await controller.pause(operation)
