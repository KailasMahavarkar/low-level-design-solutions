''' Registry for tasks '''

class TaskRegister():
    ''' A class to register tasks '''
    registry = {}

    def register(self):
        ''' Adds a task only for a certain operation '''
        def deco(a_class):
            self.registry[a_class.identifier] = a_class
            return a_class
        return deco

    def get_task_with_id(self, task_id: str):
        ''' Returns the task with the given ID '''
        try:
            return self.registry[task_id]
        except KeyError:
            raise NotImplementedError(f'Task with id {task_id} not found')

    def get_tasks(self):
        ''' Returns all the registered tasks '''
        return list(self.registry.keys())
