import os
import time
from pydantic import BaseModel

class State:
    """
    Represents the base state from which all states will inherit.
    This class defines the interface for interacting with the state machine.
    """
    def __init__(self, name):
        self.name = name

    def on_event(self, event=None, timeout=None):
        """
        Handle events that are delegated by the StateMachine.
        
        :param event: The event to process
        :return: The next state
        """
        raise NotImplementedError

    def __repr__(self):
        return self.name
    
    def __str__(self):
        return 'state'
    

class NoTruck(State):
    """
    The state representing the condition where no truck is detected and no delivery.
    """
    def __init__(self):
        super().__init__("NoTruck")

    def on_event(self, event, timeout=None):
        """
        Handle the 'truck' event to transition to the Truck state.
        
        :param event: The event to process
        :return: The next state
        """
        if event == 'Truck':
            return Truck()
        return self
    
    def __str__(self):
        return 'NoTruck'
    

class Truck(State):
    """
    The state representing the condition where no truck is detected and no delivery.
    """
    def __init__(self):
        super().__init__("Truck")

    def on_event(self, event, timeout=None):
        """
        Handle the 'no truck' event to transition to the NoTruck state.
        
        :param event: The event to process
        :return: The next state
        """
        if event == 'NoTruck':
            return NoTruck()
        return self
    
    def __str__(self):
        return 'Truck'
    
class StateMachine:
    def __init__(self):
        self.state = NoTruck()
        self.lock_file = 'delivery_status.lock'
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)

    def on_event(self, event=None, timeout=None):
        if not self.acquire_lock(self.lock_file):
            return self
        
        self.state = self.state.on_event(event, timeout)
        self.release_lock(self.lock_file)

        return self

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.state)

    def acquire_lock(self, lock_file):
        if os.path.exists(lock_file):
            print('Lock file, another process is running')
            return False

        else:
            with open(lock_file, "w") as f:
                f.write('Locked.')
            
            print('Lock acquired')
            return True
    
    def release_lock(self, lock_file):
        """Release the lock by deleting the lock file."""
        if os.path.exists(lock_file):
            os.remove(lock_file)
            print("Lock released.")
        else:
            print("Lock file does not exist.")
