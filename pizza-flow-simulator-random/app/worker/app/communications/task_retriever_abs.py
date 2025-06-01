''' Abstract class to retrieve tasks '''
from abc import ABC
from models.tasks import Task
from typing import List

class TaskRetrieverProvider(ABC):
    ''' Abstract class to retrieve tasks '''
    def get_tasks(self) -> List[Task]:
        ''' Get tasks from the provider '''
        raise NotImplemented()
