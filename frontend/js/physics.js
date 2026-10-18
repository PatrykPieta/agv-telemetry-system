const AGV_GEOMETRY = {
    wheelRadius: 0.1,  
    lx: 0.4,           
    ly: 0.3            
};

// --- AGV-01: NEURO-CURIOSITY KINEMATICS & PERIMETER GEOFENCING ---

export function updatePhysics(agvModel, wheelMeshes, rpmsState, deltaSeconds) {
    if (!agvModel) return;

    const dt = Number.isFinite(deltaSeconds) && deltaSeconds > 0 ? Math.min(deltaSeconds, 0.05) : 0.016;

    // Przeliczanie RPM na prędkość liniową (m/s)
    const toMps = (rpm) => (rpm / 60) * 2 * Math.PI * AGV_GEOMETRY.wheelRadius;
    const vFL = toMps(rpmsState.FL);
    const vFR = toMps(rpmsState.FR);
    const vRL = toMps(rpmsState.RL);
    const vRR = toMps(rpmsState.RR);

    // Kinematyka Mecanum
    const forwardSpeed = (vFL + vFR + vRL + vRR) / 4;
    const strafeSpeed  = (-vFL + vFR + vRL - vRR) / 4;
    const turnSpeed    = (-vFL + vFR - vRL + vRR) / (4 * (AGV_GEOMETRY.lx + AGV_GEOMETRY.ly));

    // Translacja ramy z uwzględnieniem czasu klatki (dt) — realistyczna prędkość w skali
    agvModel.translateX(forwardSpeed * dt * 2.0); 
    agvModel.translateZ(strafeSpeed * dt * 2.0);  
    agvModel.rotateY(turnSpeed * dt * 2.0);    

    // --- INTELIGENTNA KONTROLA PERYMETRU (Geofencing) ---
    // Robot bada halę, a zbliżając się do krawędzi (promień 20m) płynnie skręca ku środkowi
    const SAFE_RADIUS = 20.0;
    const dist = Math.hypot(agvModel.position.x, agvModel.position.z);

    if (dist > SAFE_RADIUS) {
        // Obliczenie kąta powrotu do środka hali (0, 0)
        const targetAngle = Math.atan2(-agvModel.position.x, -agvModel.position.z);
        let diff = targetAngle - agvModel.rotation.y;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        // Płynny skręt ku wnętrzu hali
        agvModel.rotation.y += Math.sign(diff) * Math.min(Math.abs(diff), 2.5 * dt);

        // Ścisła granica bezpieczeństwa (nigdy nie wyjedzie poza podłogę)
        if (dist > SAFE_RADIUS + 2.5) {
            agvModel.position.x = (agvModel.position.x / dist) * (SAFE_RADIUS + 2.4);
            agvModel.position.z = (agvModel.position.z / dist) * (SAFE_RADIUS + 2.4);
        }
    }

    // Obrót rolek i felg Mecanum
    wheelMeshes.forEach(wheel => {
        wheel.rotateY(forwardSpeed * dt * 10.0);
    });
}

// --- AGV-02: BASELINE / EPSILON-GREEDY AGENT (REFERENCYJNY) ---

let baselineTimer = 0;
let baselineSpeed = 0.9;
let baselineTurn = 0.0;
let baselinePhase = 0;

export function updateBaselinePhysics(agv02Model, wheelMeshes02, deltaSeconds, agv01Model) {
    if (!agv02Model) return;

    const dt = Number.isFinite(deltaSeconds) && deltaSeconds > 0 ? Math.min(deltaSeconds, 0.05) : 0.016;
    baselineTimer += dt;

    // Co 3.5 sekundy agent podejmuje losową decyzję eksploracyjną (epsilon-greedy)
    if (baselineTimer > 3.5) {
        baselineTimer = 0;
        baselinePhase++;
        // Losowy skręt typowy dla klasycznej eksploracji
        const rand = Math.sin(baselinePhase * 1.7);
        baselineTurn = rand * 0.8;
        baselineSpeed = 0.7 + Math.abs(Math.cos(baselinePhase * 0.9)) * 0.5;
    }

    // Unikanie kolizji z AGV-01 jeśli są zbyt blisko (< 4m)
    if (agv01Model) {
        const dx = agv02Model.position.x - agv01Model.position.x;
        const dz = agv02Model.position.z - agv01Model.position.z;
        const distTo01 = Math.hypot(dx, dz);
        if (distTo01 < 4.0 && distTo01 > 0.001) {
            // Omiń wózek 01 skręcając w bok
            agv02Model.rotation.y += Math.atan2(dx, dz) * dt;
        }
    }

    // Ruch AGV-02
    agv02Model.translateX(baselineSpeed * dt);
    agv02Model.rotateY(baselineTurn * dt);

    // Kontrola perymetru dla AGV-02 (strefa bezpieczna 21m)
    const SAFE_RADIUS_02 = 21.0;
    const dist02 = Math.hypot(agv02Model.position.x, agv02Model.position.z);
    if (dist02 > SAFE_RADIUS_02) {
        const targetAngle = Math.atan2(-agv02Model.position.x, -agv02Model.position.z);
        let diff = targetAngle - agv02Model.rotation.y;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        agv02Model.rotation.y += Math.sign(diff) * Math.min(Math.abs(diff), 2.5 * dt);

        if (dist02 > SAFE_RADIUS_02 + 2.0) {
            agv02Model.position.x = (agv02Model.position.x / dist02) * (SAFE_RADIUS_02 + 1.9);
            agv02Model.position.z = (agv02Model.position.z / dist02) * (SAFE_RADIUS_02 + 1.9);
        }
    }

    // Obrót kół AGV-02
    wheelMeshes02.forEach(wheel => {
        wheel.rotateY(baselineSpeed * dt * 8.0);
    });
}