import * as THREE from 'three';

export function setupWebSocket(agvModel, obstacleMeshes, state) {
    let socket, retryTimer, closed = false, backoff = 500, lastLidar = 0;
    let config = { agv_id: 'AGV-01', stale_ms: 2000 };
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
    const fresh = data => Number.isFinite(data.timestamp) &&
        Math.abs(Date.now() - data.timestamp * 1000) <= config.stale_ms;
    function connect() {
        if (closed) return;
        socket = new WebSocket(`${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/ws`);
        socket.onopen = () => {
            backoff = 500;
            status('Połączono — oczekiwanie na dane', '#ffcc66');
        };
        socket.onmessage = event => {
            let data;
            try { data = JSON.parse(event.data); data = data.payload ?? data; }
            catch { return; }
            if (!data || data.agv_id !== config.agv_id || !fresh(data)) return;
            if (data.ALERT_MSG) {
                alertUntil = performance.now() + 3000;
                const el = document.getElementById('ui-alert');
                if (el) el.textContent = data.ALERT_MSG;
                return;
            }
            if (data.telemetry?.motors) {
                const m = data.telemetry.motors;
                const speeds = [m.front_left?.speed_rpm, m.front_right?.speed_rpm,
                    m.rear_left?.speed_rpm, m.rear_right?.speed_rpm];
                const volts = data.telemetry.power_supply?.bus_voltage_V;
                if (!speeds.every(Number.isFinite) || !Number.isFinite(volts)) return;
                if (data.timestamp < lastTimestamp) return;
                if (data.session_id && data.session_id === session && data.sequence <= sequence) return;
                session = data.session_id;
                sequence = data.sequence;
                lastTimestamp = data.timestamp;
                [state.FL, state.FR, state.RL, state.RR] = speeds;
                state.lastReceived = performance.now();
                document.getElementById('ui-rpm').textContent = speeds[0].toFixed(1);
                document.getElementById('ui-volt').textContent = volts.toFixed(2);
                status('ONLINE — aktualna telemetria', '#66ff99');
            }
            if (Array.isArray(data.obstacles)) {
                obstacleMeshes.forEach(mesh => mesh.visible = false);
                agvModel.updateMatrixWorld(true);
                const origin = new THREE.Vector3();
                const rotation = new THREE.Quaternion();
                agvModel.getWorldPosition(origin);
                agvModel.getWorldQuaternion(rotation);
                data.obstacles.slice(0, obstacleMeshes.length).forEach((obs, i) => {
                    if (![obs.center_x_m, obs.center_y_m, obs.size_m].every(Number.isFinite) || obs.size_m <= 0) return;
                    const cube = obstacleMeshes[i];
                    // Sensor: X forward, Y left. Scene: X forward, Z right.
                    // Ignore visual model scale: sensor measurements are already in metres.
                    cube.position.set(obs.center_x_m, 0.5, -obs.center_y_m).applyQuaternion(rotation).add(origin);
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
    const timer = setInterval(() => {
        if (state.lastReceived && performance.now() - state.lastReceived > config.stale_ms) {
            reset();
            status('Brak aktualnej telemetrii', '#ffcc66');
        }
        if (performance.now() - lastLidar > config.stale_ms) obstacleMeshes.forEach(mesh => mesh.visible = false);
        if (performance.now() > alertUntil) {
            const el = document.getElementById('ui-alert');
            if (el) el.textContent = 'Brak bieżących ostrzeżeń';
        }
    }, 250);
    fetch('/api/config').then(r => { if (!r.ok) throw Error('config'); return r.json(); })
        .then(value => { config = value; connect(); })
        .catch(() => { status('Nie udało się pobrać konfiguracji. Odśwież stronę.', '#ff6666'); });
    window.addEventListener('beforeunload', () => {
        closed = true; clearInterval(timer); clearTimeout(retryTimer); socket?.close();
    }, { once: true });
}
