export function setupWebSocket(agvModel, obstacleMeshes, rpmsState) {
    const ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onopen = () => {
        const statusEl = document.getElementById('status');
        if (statusEl) {
            statusEl.innerText = "ONLINE";
            statusEl.className = "";
            statusEl.style.color = "#00ff00";
        }
    };

    ws.onmessage = (event) => {
        let data;
        try {
            data = JSON.parse(event.data);
        } catch (error) {
            return; // Śmieciowa paczka, ignorujemy po cichu
        }

        // ALARMY BIG DATA
        if (data.ALERT_MSG) {
            console.warn("🔥 ALARM Z SYSTEMU BIG DATA:", data.ALERT_MSG);
            const statusEl = document.getElementById('status');
            if (statusEl) {
                statusEl.innerText = "🔥 ZATARCIE KOŁA!";
                statusEl.style.color = "#ff0000";
            }
            if (agvModel) {
                agvModel.traverse(node => {
                    if (node.isMesh && (!node.name.toLowerCase().includes('koło') && !node.name.toLowerCase().includes('wheel'))) {
                        node.material.color.setHex(0xff0000);
                    }
                });
            }
            return;
        }

        // TELEMETRIA
        if (data.telemetry && data.telemetry.motors) {
            const rpmEl = document.getElementById('ui-rpm');
            const voltEl = document.getElementById('ui-volt');
            if (rpmEl) rpmEl.innerText = data.telemetry.motors.front_left.speed_rpm;
            if (voltEl) voltEl.innerText = data.telemetry.power_supply.bus_voltage_V;

            // Zapisujemy prędkości do globalnego obiektu stanu
            rpmsState.FL = data.telemetry.motors.front_left.speed_rpm;
            rpmsState.FR = data.telemetry.motors.front_right.speed_rpm;
            rpmsState.RL = data.telemetry.motors.rear_left.speed_rpm;
            rpmsState.RR = data.telemetry.motors.rear_right.speed_rpm;
        }

        // PRZESZKODY (LiDAR / DBSCAN)
        if (data.obstacles) {
            obstacleMeshes.forEach(mesh => mesh.visible = false);
            for (let i = 0; i < data.obstacles.length; i++) {
                if (i >= obstacleMeshes.length) break;

                const obs = data.obstacles[i];
                const cube = obstacleMeshes[i];

                cube.scale.set(obs.size_m, 1, obs.size_m);
                cube.position.set(obs.center_x_m, 0.5, -obs.center_y_m);

                if (obs.avg_reflectivity > 200) {
                    cube.material.color.setHex(0xffaa00);
                    cube.material.opacity = 0.9;
                } else if (obs.avg_reflectivity > 100) {
                    cube.material.color.setHex(0xaaaaaa);
                    cube.material.opacity = 0.7;
                } else {
                    cube.material.color.setHex(0x444444);
                    cube.material.opacity = 0.5;
                }
                cube.visible = true;
            }
        }
    };
}