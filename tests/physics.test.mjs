import assert from 'node:assert/strict';
import { updatePhysics, velocities } from '../frontend/js/physics.js';

function simulate(fps, state = { FL: 100, FR: 100, RL: 100, RR: 100 }) {
    const model = {
        x: 0, z: 0, rotation: 0,
        translateX(v) { this.x += v; }, translateZ(v) { this.z += v; },
        rotateY(v) { this.rotation += v; },
    };
    state.lastReceived = performance.now();
    for (let i = 0; i < fps; i++) updatePhysics(model, [], state, 1 / fps);
    return model;
}
assert.ok(Math.abs(simulate(30).x - simulate(144).x) < 1e-10);
assert.ok(Math.abs(simulate(60).x - Math.PI / 3) < 1e-10);
assert.equal(velocities({ FL: 100, FR: -100, RL: -100, RR: 100 }).forward, 0);
assert.equal(velocities({ FL: 80, FR: -80, RL: 80, RR: -80 }).strafe, 0);
let moves = 0;
const model = { translateX() { moves++; }, translateZ() {}, rotateY() {} };
updatePhysics(model, [], { FL: 100, FR: 100, RL: 100, RR: 100, lastReceived: performance.now() - 3000 }, 1 / 60);
assert.equal(moves, 0, 'Stale telemetry must stop movement');
updatePhysics(model, [], { FL: 100, FR: 100, RL: 100, RR: 100, lastReceived: performance.now() }, 5);
assert.equal(moves, 0, 'Resuming a suspended tab must not jump');
console.log('PASS: FPS independence, units, strafe, rotation, stale data and suspended tab');
