import logging

from pulser import Pulse, QPUBackend, Register, Sequence
from pulser.backend.remote import JobParams
from qrmi.pulser.connection import PulserQRMIConnection
from qrmi.pulser.service import QRMIService

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
name, device = next(iter(avail_devices.items()))
print(f"Found device: '{name}' from the QRMI connection.")

reg = Register(
    {
        "q0": (-2.5, -2.5),
        "q1": (2.5, -2.5),
        "q2": (-2.5, 2.5),
        "q3": (2.5, 2.5),
    }
).with_automatic_layout(device)
print(device)

seq = Sequence(reg, device)
seq.declare_channel("rydberg", "rydberg_global")

pulse1 = Pulse.ConstantPulse(100, 2, 2, 0)

seq.add(pulse1, "rydberg")
seq.measure("ground-rydberg")


backend = QPUBackend(seq, qrmi_conn)
result = backend.run([JobParams(runs=500, variables=[])], wait=True)
print("results", result.results)
