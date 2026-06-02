import logging

import torch
from qrmi.pulser.connection import PulserQRMIConnection
from qrmi.pulser.service import QRMIService
from qubosolver import QUBOInstance
from qubosolver.config import QPU, Device, SolverConfig
from qubosolver.solver import QuboSolver

logging.basicConfig(
    level=logging.DEBUG,  # or INFO
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger()

# Create QRMI
service = QRMIService()
resources = service.resources()
if len(resources) == 0:
    print("No quantum resource is available.")


# Randomly select QR
qrmi = resources[0]

qrmi_conn = PulserQRMIConnection(qrmi)
# Generate Pulser device
avail_devices = qrmi_conn.fetch_available_devices()
name, pulser_device = next(iter(avail_devices.items()))
print(f"Found device: '{name}' from the QRMI connection.")


# define QUBO
Q = torch.tensor([[-0.2, 0, 1.0], [0, 0, 1.5], [1.0, 1.5, 0]])
instance = QUBOInstance(coefficients=Q)

device = Device(pulser_device=pulser_device)
config = SolverConfig(
    use_quantum=True, device=device, backend=QPU(connection=qrmi_conn, num_shots=1000)
)

# Run the solver
solver = QuboSolver(instance, config)
solutions = solver.solve()

# Display results
print(solutions)
