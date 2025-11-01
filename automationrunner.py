# Runnable worker for automation sequences to run on the threadpool
# This is separate to Worker class which is used for the API

from PySide6.QtCore import QRunnable, Slot, Signal, QObject, QThread, QThreadPool
import time
from eventbus import event_bus
from automationsequence import AutomationSequence
from automationrule import AutomationRule

class AutomationRunner (QRunnable):
    
    def __init__(self, sequence: AutomationSequence, data):
        super().__init__()
        #self.signals = RunnerSignals()
        self.sequence = sequence
        self.data = data
        self.is_active = True		# When created assume
        
    # Main run part
    @Slot()
    def run(self):
        #self.signals.progress.emit(f"Starting sequence: {self.sequence.title}")

        try:
            # Iterate through each STEP (Sequential Steps)
            for i, step in enumerate(self.sequence.steps):
                if not self.is_active:
                    break

                #self.signals.progress.emit(f"Running Step {i+1}...")
                print (f"Running step {i+1}")

                # A Step can have multiple rules to run in parallel or sequentially
                if step.execution_mode == "sequential":
                    for rule in step.rules:
                        if not self.is_active:
                            break
                        self._execute_rule(rule)

                elif step.execution_mode == "parallel":
                    # For true parallelism within a step, you'd need nested QRunnables,
                    # but for simple model control, basic threading/async might be overkill.
                    # We'll simulate parallel control calls sequentially 
                    for rule in step.rules:
                        self._execute_rule(rule, suppress_wait=True) # Don't block on waits

                    # Parallel is sequential commands not waits

                time.sleep(0.1) # Small pause between steps for visual feedback

        except Exception as e:
            #self.signals.error.emit(f"Error during execution: {e}")
            print (f"Error during execution: {e}")
        finally:
            #self.signals.progress.emit("Sequence finished or stopped.")
            #self.signals.finished.emit()
            print ("Sequence finished")

    def _execute_rule(self, rule: AutomationRule, suppress_wait=False):
        """Executes a single AutomationRule."""
        if not self.is_active: return

        ## Get the actual loco ID based on the index (0, 1, 2)
        #loco_id = self.assigned_locos[rule.loco_index] if rule.loco_index is not None else None
        
        #self.signals.progress.emit(f"Executing: {rule}")
        print (f"Executing: {rule}")

        # --- Rule Execution Logic ---
        ## Need to update all these to issue appropriate events
        if rule.rule_type == RuleType.SET_SPEED:
            #speed = rule.params['speed']
            #self.control.set_loco_speed(loco_id, speed)
            print (f"Setting speed {self.data}")

        elif rule.rule_type == RuleType.STOP_LOCO:
            print (f"Setting speed stop {self.data}")
            #self.control.stop_loco(loco_id)

        elif rule.rule_type == RuleType.SWITCH_POINT:
            #point_id = rule.params['point_id']
            #state = rule.params['state']
            #self.control.set_point_state(point_id, state)
            print (f"Setting point {self.data}")

        elif rule.rule_type == RuleType.WAIT_TIME and not suppress_wait:
            wait_s = rule.params['seconds']
            print (f"Waiting {wait_s}")
            # Blocking call in the worker thread
            time.sleep(wait_s)

        elif rule.rule_type == RuleType.WAIT_FOR_SENSOR and not suppress_wait:
            #sensor_id = rule.params['sensor_id']
            # NOTE: This requires integration with your sensor system.
            # E.g., a polling loop or waiting for a signal from your control system.
            #self.signals.progress.emit(f"Waiting for sensor {sensor_id}...")
            print (f"Waiting for sensor {sensor_id}...")
            
            # Placeholder: In a real system, you'd register to receive a sensor event.
            # For simplicity in this example, we'll wait for 5 seconds as a mockup.
            time.sleep(5) 
            # Real implementation: self.control.wait_for_sensor_hit(sensor_id) 

        # Add more rule execution logic here...
        # ------------------------------------

    # Set is_active to False to stop the sequence
    def stop(self):
        self.is_active = False