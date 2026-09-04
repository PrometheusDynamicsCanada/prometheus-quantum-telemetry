OPENQASM 3.0;
include "stdgates.inc";

qubit[13] q;
bit[13] meas;

// Layer 1: Global Superposition
h q[0]; h q[1]; h q[2]; h q[3]; h q[4]; h q[5]; h q[6]; h q[7]; h q[8]; h q[9]; h q[10]; h q[11]; h q[12];

// Layer 2: Long-Range Crossings
cx q[0], q[12];
cx q[1], q[11];
cx q[2], q[10];
cx q[3], q[9];
cx q[4], q[8];
cx q[5], q[7];

barrier q;

// Layer 3: Phase Shift
rz(pi/4) q[0]; rz(pi/4) q[1]; rz(pi/4) q[2]; rz(pi/4) q[3]; rz(pi/4) q[4]; rz(pi/4) q[5]; rz(pi/4) q[6]; rz(pi/4) q[7]; rz(pi/4) q[8]; rz(pi/4) q[9]; rz(pi/4) q[10]; rz(pi/4) q[11]; rz(pi/4) q[12];

barrier q;

// Layer 4: Shifted Crossings
cx q[0], q[6];
cx q[1], q[7];
cx q[2], q[8];
cx q[3], q[9];
cx q[4], q[10];
cx q[5], q[11];
cx q[6], q[12];

barrier q;

// Layer 5: X-Axis Rotation
rx(pi/5) q[0]; rx(pi/5) q[1]; rx(pi/5) q[2]; rx(pi/5) q[3]; rx(pi/5) q[4]; rx(pi/5) q[5]; rx(pi/5) q[6]; rx(pi/5) q[7]; rx(pi/5) q[8]; rx(pi/5) q[9]; rx(pi/5) q[10]; rx(pi/5) q[11]; rx(pi/5) q[12];

barrier q;

// Layer 6: Final Overlapping Crossings
cx q[0], q[11];
cx q[1], q[12];
cx q[2], q[9];
cx q[3], q[10];
cx q[4], q[7];
cx q[5], q[8];

barrier q;

// Telemetry Extraction
meas[0] = measure q[0]; meas[1] = measure q[1]; meas[2] = measure q[2]; meas[3] = measure q[3]; meas[4] = measure q[4]; meas[5] = measure q[5]; meas[6] = measure q[6]; meas[7] = measure q[7]; meas[8] = measure q[8]; meas[9] = measure q[9]; meas[10] = measure q[10]; meas[11] = measure q[11]; meas[12] = measure q[12];