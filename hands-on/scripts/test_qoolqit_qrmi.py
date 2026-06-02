import logging
import time

from qoolqit import DataGraph, Device, Drive, QuantumProgram, Register
from qoolqit.embedding import SpringLayoutEmbedder
from qoolqit.execution import QPU, JobStatus
from qoolqit.waveforms import Constant, Interpolated, Ramp
from qrmi.pulser.connection import PulserQRMIConnection

logging.basicConfig(
    level=logging.DEBUG,  # or INFO
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger()

# PulserQRMIConnection() is going to get the QRMI configuration from env variables.
qrmi_conn = PulserQRMIConnection()

# Generate Pulser device
avail_devices = qrmi_conn.fetch_available_devices()
name, pulser_device = next(iter(avail_devices.items()))
print(f"Found device: '{name}' from the QRMI connection.")

# Register


graph = DataGraph.random_er(n=5, p=0.3, seed=3)
embedded_graph = SpringLayoutEmbedder().embed(graph)
register = Register.from_graph(embedded_graph)

# Waveforms and Drives

# Interpolated waveform: smooth curve through specified values
omega_wf = Interpolated(duration=10, values=[0, 1, 0])

# Constant waveform
delta_wf = Constant(duration=10, value=-2)

# Ramp waveform
delta_wf = Ramp(duration=10, initial_value=-2, final_value=2)

# Combine into a Drive
drive = Drive(amplitude=omega_wf, detuning=delta_wf)

# QuantumProgram


program = QuantumProgram(register=register, drive=drive)

# Compilation

device = Device(pulser_device=pulser_device)
program.compile_to(device)

# Execution


backend = QPU(connection=qrmi_conn, num_shots=100)
job = backend.run(program)
# job = emulator.run(program)
while job.get_status() != JobStatus.DONE:
    time.sleep(1)

results = job.results()
print("Results:", results)
