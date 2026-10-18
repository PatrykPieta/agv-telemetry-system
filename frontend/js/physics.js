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

    // Translacja ramy z uwzględnieniem czasu klatki (dt)
    agvModel.translateX(forwardSpeed * dt * 2.0); 
    agvModel.translateZ(strafeSpeed * dt * 2.0);  
    agvModel.rotateY(turnSpeed * dt * 2.0);    

    // --- INTELIGENTNA KONTROLA PERYMETRU (Geofencing) ---
    // Robot bada halę, a zbliżając się do krawędzi (promień 19m) płynnie skręca ku środkowi
    const SAFE_RADIUS = 19.0;
    const dist = Math.hypot(agvModel.position.x, agvModel.position.z);

    if (dist > SAFE_RADIUS) {
        const targetAngle = Math.atan2(-agvModel.position.x, -agvModel.position.z);
        let diff = targetAngle - agvModel.rotation.y;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        agvModel.rotation.y += Math.sign(diff) * Math.min(Math.abs(diff), 2.5 * dt);

        if (dist > SAFE_RADIUS + 2.0) {
            agvModel.position.x = (agvModel.position.x / dist) * (SAFE_RADIUS + 1.9);
            agvModel.position.z = (agvModel.position.z / dist) * (SAFE_RADIUS + 1.9);
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

export function updateBaselinePhysics(agv02Model, wheelMeshes02, deltaSeconds) {
    if (!agv02Model) return;

    const dt = Number.isFinite(deltaSeconds) && deltaSeconds > 0 ? Math.min(deltaSeconds, 0.05) : 0.016;
    baselineTimer += dt;

    // Co 3 sekundy agent podejmuje decyzję eksploracyjną
    if (baselineTimer > 3.0) {
        baselineTimer = 0;
        baselinePhase++;
        const rand = Math.sin(baselinePhase * 1.7);
        baselineTurn = rand * 0.7;
        baselineSpeed = 0.8 + Math.abs(Math.cos(baselinePhase * 0.9)) * 0.4;
    }

    // Ruch AGV-02
    agv02Model.translateX(baselineSpeed * dt);
    agv02Model.rotateY(baselineTurn * dt);

    // Kontrola perymetru dla AGV-02
    const SAFE_RADIUS_02 = 19.5;
    const dist02 = Math.hypot(agv02Model.position.x, agv02Model.position.z);
    if (dist02 > SAFE_RADIUS_02) {
        const targetAngle = Math.atan2(-agv02Model.position.x, -agv02Model.position.z);
        let diff = targetAngle - agv02Model.rotation.y;
        while (diff < -Math.PI) diff += Math.PI * 2;
        while (diff > Math.PI) diff -= Math.PI * 2;
        agv02Model.rotation.y += Math.sign(diff) * Math.min(Math.abs(diff), 2.5 * dt);

        if (dist02 > SAFE_RADIUS_02 + 1.8) {
            agv02Model.position.x = (agv02Model.position.x / dist02) * (SAFE_RADIUS_02 + 1.7);
            agv02Model.position.z = (agv02Model.position.z / dist02) * (SAFE_RADIUS_02 + 1.7);
        }
    }

    // Obrót kół AGV-02
    wheelMeshes02.forEach(wheel => {
        wheel.rotateY(baselineSpeed * dt * 8.0);
    });
}

// --- FIZYCZNA DETEKCJA I ODPYCHANIE KOLIZJI FLOTY (NIGDY SIĘ NIE PRZENIKAJĄ) ---

export function resolveFleetCollisions(agv01, agv02, dt) {
    if (!agv01 || !agv02) return;

    const dx = agv02.position.x - agv01.position.x;
    const dz = agv02.position.z - agv01.position.z;
    const dist = Math.hypot(dx, dz);

    const COLLISION_RADIUS = 3.2; // Minimalny bezpieczny promień (wózki ~2.2m x 1.8m)
    const WARNING_RADIUS = 6.5;   // Strefa wczesnego unikania

    // 1. Aktywne omijanie (przed kolizją)
    if (dist < WARNING_RADIUS && dist > 0.01) {
        const sideAngle = Math.atan2(dx, dz);
        // AGV-02 skręca w prawo
        agv02.rotation.y += Math.sin(sideAngle - agv02.rotation.y) * 2.0 * dt;
        // AGV-01 skręca w lewo
        agv01.rotation.y -= Math.sin(sideAngle - agv01.rotation.y) * 1.5 * dt;
    }

    // 2. Twarda blokada przenikania (fizyczne rozepchnięcie)
    if (dist < COLLISION_RADIUS && dist > 0.001) {
        const overlap = COLLISION_RADIUS - dist;
        const nx = dx / dist;
        const nz = dz / dist;

        agv02.position.x += nx * overlap * 0.55;
        agv02.position.z += nz * overlap * 0.55;

        agv01.position.x -= nx * overlap * 0.45;
        agv01.position.z -= nz * overlap * 0.45;
    }
}