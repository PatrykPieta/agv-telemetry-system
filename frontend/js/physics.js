export const AGV_GEOMETRY = { wheelRadius: 0.1, lx: 0.4, ly: 0.3 };

export function velocities(rpms) {
    const toMps = rpm => rpm * Math.PI * AGV_GEOMETRY.wheelRadius / 30;
    const [fl, fr, rl, rr] = ['FL', 'FR', 'RL', 'RR'].map(key => toMps(rpms[key]));
    return {
        forward: (fl + fr + rl + rr) / 4,
        strafe: (-fl + fr + rl - rr) / 4,
        turn: (-fl + fr - rl + rr) / (4 * (AGV_GEOMETRY.lx + AGV_GEOMETRY.ly)),
    };
}

export function updatePhysics(agvModel, wheelMeshes, state, deltaSeconds) {
    if (!agvModel || !Number.isFinite(deltaSeconds) || deltaSeconds <= 0) return;
    if (!['FL', 'FR', 'RL', 'RR'].every(key => Number.isFinite(state[key]))) return;
    // Pause on stale telemetry or after a suspended browser tab; no catch-up jump.
    if (!state.lastReceived || performance.now() - state.lastReceived > 2000 || deltaSeconds > 0.25) return;
    const speed = velocities(state);
    agvModel.translateX(speed.forward * deltaSeconds);
    agvModel.translateZ(speed.strafe * deltaSeconds);
    agvModel.rotateY(speed.turn * deltaSeconds);
    for (const wheel of wheelMeshes) {
        const name = wheel.name.toLowerCase();
        const key = [['FL', 'front_left'], ['FR', 'front_right'], ['RL', 'rear_left'], ['RR', 'rear_right']]
            .find(([short, full]) => name.includes(short.toLowerCase()) || name.includes(full))?.[0];
        if (key) wheel.rotateY(state[key] * Math.PI / 30 * deltaSeconds);
    }
}
