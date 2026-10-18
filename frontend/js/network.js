import * as THREE from 'three';

/**
 * IDUB Neuro-Curiosity Showcase — WebSocket network module.
 *
 * Extends the base AGV telemetry handler to also parse and distribute
 * rl_agent fields (intrinsic_reward, ICM error, jerk, etc.) from the
 * IDUB synthetic emulator. Backwards-compatible with the original emulator.
 */
export function setupWebSocket(agvModel, obstacleMeshes, state, rlState) {
    let socket, retryTimer, closed = false, backoff = 500, lastLidar = 0;
    let config = { agv_id: 'AGV-01', stale_ms: 3000 };
    let lastTimestamp = 0, session = null, sequence = -1;
    let alertUntil = 0;

    const status = (text, color) => {
        const el = document.getElementById('status');
        if (el) { el.textContent = text; el.style.color = color; }
    };

    const reset = () => {
        Object.assign(state, { FL: 0, FR: 0, RL: 0, RR: 0, lastReceived: 0 });
        for (const id of ['ui-rpm', 'ui-volt']) {
            const el = document.getElementById(id);
            if (el) el.textContent = '—';
        }
        obstacleMeshes.forEach(mesh => mesh.visible = false);
    };

    // Robust against Docker/WSL2 clock skew: accepts data if timestamp is valid and advancing
    const fresh = data =>
        Number.isFinite(data.timestamp) &&
        (Math.abs(Date.now() - data.timestamp * 1000) <= 120000 || !lastTimestamp || data.timestamp >= lastTimestamp);

    function connect() {
        if (closed) return;
        socket = new WebSocket(
            `${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/ws`
        );

        socket.onopen = () => {
            backoff = 500;
            status('Połączono — oczekiwanie na dane', '#ffcc66');
        };

        socket.onmessage = event => {
            let data;
            try {
                data = JSON.parse(event.data);
                data = data.payload ?? data;
            } catch {
                return;
            }

            if (!data || data.agv_id !== config.agv_id || !fresh(data)) return;

            // Alert messages from Spark
            if (data.ALERT_MSG) {
                alertUntil = performance.now() + 3000;
                const el = document.getElementById('ui-alert');
                if (el) el.textContent = '⚠️ ' + data.ALERT_MSG;
                return;
            }

            // --- Standard telemetry (motor RPM + power) ---
            if (data.telemetry?.motors) {
                const m = data.telemetry.motors;
                const speeds = [
                    m.front_left?.speed_rpm,
                    m.front_right?.speed_rpm,
                    m.rear_left?.speed_rpm,
                    m.rear_right?.speed_rpm,
                ];
                const volts = data.telemetry.power_supply?.bus_voltage_V;
                if (!speeds.every(Number.isFinite) || !Number.isFinite(volts)) return;

                if (data.session_id && data.session_id === session && data.sequence <= sequence) return;

                session = data.session_id;
                sequence = data.sequence;
                lastTimestamp = data.timestamp;

                [state.FL, state.FR, state.RL, state.RR] = speeds;
                state.lastReceived = performance.now();

                const rpmEl = document.getElementById('ui-rpm');
                if (rpmEl) rpmEl.textContent = speeds[0].toFixed(1);
                const voltEl = document.getElementById('ui-volt');
                if (voltEl) voltEl.textContent = volts.toFixed(2);

                const isIdub = data.scenario === 'neuro_curiosity' || Boolean(data.rl_agent);
                status(
                    isIdub ? '🟢 ONLINE — Neuro-Curiosity aktywne' : 'ONLINE — aktualna telemetria',
                    '#66ff99'
                );
            }

            // --- IDUB RL agent telemetry ---
            if (data.rl_agent && rlState) {
                const rl = data.rl_agent;
                if (Number.isFinite(rl.intrinsic_reward))     rlState.intrinsic_reward     = rl.intrinsic_reward;
                if (Number.isFinite(rl.extrinsic_reward))     rlState.extrinsic_reward     = rl.extrinsic_reward;
                if (Number.isFinite(rl.total_reward))         rlState.total_reward         = rl.total_reward;
                if (Number.isFinite(rl.icm_prediction_error)) rlState.icm_prediction_error = rl.icm_prediction_error;
                if (Number.isFinite(rl.policy_entropy))       rlState.policy_entropy       = rl.policy_entropy;
                if (Number.isFinite(rl.jerk_mps3))            rlState.jerk_mps3            = rl.jerk_mps3;
                if (Number.isFinite(rl.sim_to_real_gap))      rlState.sim_to_real_gap      = rl.sim_to_real_gap;
                if (Number.isFinite(rl.training_step))        rlState.training_step        = rl.training_step;
                if (rl.algorithm)  rlState.algorithm  = rl.algorithm;
                if (rl.policy)     rlState.policy     = rl.policy;

                const algEl = document.getElementById('hud-algorithm');
                if (algEl) algEl.textContent = rl.algorithm || '—';
                const polEl = document.getElementById('hud-policy');
                if (polEl) polEl.textContent = rl.policy || '—';
                const modeEl = document.getElementById('hud-mode');
                if (modeEl) modeEl.textContent = rl.mode || '—';
                const platEl = document.getElementById('hud-platform');
                if (platEl) platEl.textContent = rl.platform || '—';
            }

            // --- LiDAR obstacles ---
            if (Array.isArray(data.obstacles)) {
                obstacleMeshes.forEach(mesh => mesh.visible = false);
                agvModel.updateMatrixWorld(true);
                const origin = new THREE.Vector3();
                const rotation = new THREE.Quaternion();
                agvModel.getWorldPosition(origin);
                agvModel.getWorldQuaternion(rotation);

                data.obstacles.slice(0, obstacleMeshes.length).forEach((obs, i) => {
                    if (
                        ![obs.center_x_m, obs.center_y_m, obs.size_m].every(Number.isFinite) ||
                        obs.size_m <= 0
                    ) return;
                    const cube = obstacleMeshes[i];
                    cube.position
                        .set(obs.center_x_m, 0.5, -obs.center_y_m)
                        .applyQuaternion(rotation)
                        .add(origin);
                    cube.quaternion.copy(rotation);
                    cube.scale.set(obs.size_m, 1, obs.size_m);
                    cube.visible = true;
                });
                lastLidar = performance.now();
            }
        };

        socket.onerror = () => socket.close();

        socket.onclose = () => {
            reset();
            status('Rozłączono — ponawianie połączenia', '#ff6666');
            if (!closed) {
                retryTimer = setTimeout(connect, backoff);
                backoff = Math.min(backoff * 2, 10000);
            }
        };
    }

    // Staleness watchdog
    const timer = setInterval(() => {
        if (state.lastReceived && performance.now() - state.lastReceived > 4000) {
            reset();
            status('Brak aktualnej telemetrii', '#ffcc66');
        }
        if (performance.now() - lastLidar > 4000) {
            obstacleMeshes.forEach(mesh => mesh.visible = false);
        }
        if (performance.now() > alertUntil) {
            const el = document.getElementById('ui-alert');
            if (el) el.textContent = 'Brak bieżących ostrzeżeń';
        }
    }, 250);

    fetch('/api/config')
        .then(r => { if (!r.ok) throw Error('config'); return r.json(); })
        .then(value => { config = value; connect(); })
        .catch(() => {
            console.warn('[Network] Using default config fallback');
            config = { agv_id: 'AGV-01', stale_ms: 3000 };
            connect();
        });

    window.addEventListener('beforeunload', () => {
        closed = true;
        clearInterval(timer);
        clearTimeout(retryTimer);
        socket?.close();
    }, { once: true });
}