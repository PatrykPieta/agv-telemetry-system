const AGV_GEOMETRY = {
    wheelRadius: 0.1,  
    lx: 0.4,           
    ly: 0.3            
};

export function updatePhysics(agvModel, wheelMeshes, rpmsState) {
    if (!agvModel) return;

    // Przeliczanie RPM na prędkość liniową (m/s)
    const toMps = (rpm) => (rpm / 60) * 2 * Math.PI * AGV_GEOMETRY.wheelRadius;
    const vFL = toMps(rpmsState.FL);
    const vFR = toMps(rpmsState.FR);
    const vRL = toMps(rpmsState.RL);
    const vRR = toMps(rpmsState.RR);

    // Kinematyka Mecanum
    let forwardSpeed = (vFL + vFR + vRL + vRR) / 4;
    let strafeSpeed  = (-vFL + vFR + vRL - vRR) / 4;
    let turnSpeed    = (-vFL + vFR - vRL + vRR) / (4 * (AGV_GEOMETRY.lx + AGV_GEOMETRY.ly));

    // Translacja ramy
    agvModel.translateX(forwardSpeed * 0.1); 
    agvModel.translateZ(strafeSpeed * 0.1);  
    agvModel.rotateY(turnSpeed * 0.05);    
    
    // --- DODAJ TEN FRAGMENT POD RUCHEM ---
    const LIMIT = 45; // Hala ma 100x100, więc 45 to bezpieczna granica przed krawędzią
    
    if (Math.abs(agvModel.position.x) > LIMIT) {
        agvModel.position.x = LIMIT * Math.sign(agvModel.position.x);
    }
    if (Math.abs(agvModel.position.z) > LIMIT) {
        agvModel.position.z = LIMIT * Math.sign(agvModel.position.z);
    }
    // -------------------------------------

    // Obrót wizualny samych kół
    wheelMeshes.forEach(wheel => {
        const name = wheel.name.toLowerCase();
        let rotationVelocity = forwardSpeed * 0.05; 
        
        if (name.includes('fl') || name.includes('front_left')) rotationVelocity = vFL;
        if (name.includes('fr') || name.includes('front_right')) rotationVelocity = vFR;
        if (name.includes('rl') || name.includes('rear_left')) rotationVelocity = vRL;
        if (name.includes('rr') || name.includes('rear_right')) rotationVelocity = vRR;
        
        wheel.rotateY(rotationVelocity * 0.5); 
    });
}