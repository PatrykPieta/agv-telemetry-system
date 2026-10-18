/**
 * IDUB Neuro-Curiosity — Curiosity Visualization
 *
 * Renders Three.js overlays on top of the AGV model to visually represent
 * the Intrinsic Curiosity Module (ICM) state:
 *   - A pulsing "curiosity aura" ring around the robot (intrinsic reward indicator)
 *   - A predicted trajectory arrow (forward model prediction)
 *   - ICM error flash effect (red glow when prediction error spikes)
 *   - Exploration heat points scattered around the robot path
 */
import * as THREE from 'three';

const AURA_SEGMENTS = 64;
const TRAIL_LENGTH   = 30;   // Number of exploration footprint points

export function setupCuriosityViz(scene, agvModel) {
    // --- 1. Curiosity Aura Ring ---
    const auraGeo = new THREE.RingGeometry(0.45, 0.55, AURA_SEGMENTS);
    const auraMat = new THREE.MeshBasicMaterial({
        color: 0xffdd00,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.0,
        depthWrite: false,
    });
    const aura = new THREE.Mesh(auraGeo, auraMat);
    aura.rotation.x = -Math.PI / 2;
    aura.position.y = 0.02;
    agvModel.add(aura);

    // --- 2. Predicted trajectory arrow (ICM forward model) ---
    const arrowDir = new THREE.Vector3(1, 0, 0);
    const arrowHelper = new THREE.ArrowHelper(
        arrowDir,
        new THREE.Vector3(0, 0.3, 0),
        1.2,
        0x00c8ff,
        0.25,
        0.15
    );
    agvModel.add(arrowHelper);

    // --- 3. ICM error spike — pulsing red point light ---
    const spikeLight = new THREE.PointLight(0xff2200, 0, 2.5);
    spikeLight.position.set(0, 0.5, 0);
    agvModel.add(spikeLight);

    // --- 4. Exploration trail (footprint points in world space) ---
    const trailGeo = new THREE.BufferGeometry();
    const trailPositions = new Float32Array(TRAIL_LENGTH * 3);
    trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
    const trailMat = new THREE.PointsMaterial({
        color: 0x00ff99,
        size: 0.07,
        transparent: true,
        opacity: 0.6,
        depthWrite: false,
        sizeAttenuation: true,
    });
    const trail = new THREE.Points(trailGeo, trailMat);
    scene.add(trail);

    // --- 5. Outer curiosity ring (secondary larger ring) ---
    const outerGeo = new THREE.RingGeometry(0.8, 0.85, AURA_SEGMENTS);
    const outerMat = new THREE.MeshBasicMaterial({
        color: 0x0088ff,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.0,
        depthWrite: false,
    });
    const outerRing = new THREE.Mesh(outerGeo, outerMat);
    outerRing.rotation.x = -Math.PI / 2;
    outerRing.position.y = 0.03;
    agvModel.add(outerRing);

    return {
        aura, auraMat,
        arrowHelper,
        spikeLight,
        trail, trailGeo, trailPositions,
        outerRing, outerMat,
        trailIndex: 0,
        lastTrailTime: 0,
        phase: 0,
    };
}

export function updateCuriosityViz(viz, rlState, dt) {
    viz.phase += dt * 2.5;

    const ir = rlState.intrinsic_reward || 0;
    const icmErr = rlState.icm_prediction_error || 0;
    const gap = rlState.sim_to_real_gap || 0;

    // --- Aura pulse: opacity and scale driven by intrinsic reward ---
    const pulse = 0.5 + 0.5 * Math.sin(viz.phase * 2);
    viz.auraMat.opacity = ir * 0.6 * pulse;
    const auraScale = 1.0 + ir * 0.3 * pulse;
    viz.aura.scale.set(auraScale, auraScale, 1);

    // --- Outer ring: sim-to-real gap indicator (blue, fades as gap closes) ---
    viz.outerMat.opacity = gap * 0.5 * (0.4 + 0.6 * Math.sin(viz.phase));
    const outerScale = 1.0 + gap * 0.2;
    viz.outerRing.scale.set(outerScale, outerScale, 1);

    // --- ICM spike light: ignites on high prediction error ---
    viz.spikeLight.intensity = icmErr > 0.35 ? icmErr * 3.0 * (0.5 + 0.5 * Math.sin(viz.phase * 8)) : 0;

    // --- Arrow: direction reflects strafe vs forward tendency ---
    const len = 0.5 + ir * 1.5;
    viz.arrowHelper.setLength(len, Math.min(0.3, len * 0.2), 0.1);
    viz.arrowHelper.setColor(icmErr > 0.4 ? 0xff4444 : 0x00c8ff);
    // Arrow opacity via line material
    if (viz.arrowHelper.line) {
        viz.arrowHelper.line.material.opacity = 0.3 + ir * 0.7;
        viz.arrowHelper.line.material.transparent = true;
    }

    // --- Trail: drop a footprint every 0.3 s ---
    const now = performance.now();
    if (viz.agvModel && now - viz.lastTrailTime > 300) {
        viz.lastTrailTime = now;
    }

    // Update trail colors based on curiosity (handled via trailMat color)
    viz.trail.material.color.setHSL(0.35 - ir * 0.25, 1.0, 0.5);

    // Update exploration trail positions (world space sampling from agvModel parent)
    if (viz.trail.parent && viz.trail.parent.children) {
        // Trail positions are updated by main.js via updateTrailPoint if available
    }
}

/**
 * Call this from the animation loop to append current AGV world position to trail.
 * Pass agvModel to read its world position.
 */
export function appendTrailPoint(viz, agvModel) {
    if (!agvModel || !viz) return;
    const pos = new THREE.Vector3();
    agvModel.getWorldPosition(pos);

    const idx = viz.trailIndex % TRAIL_LENGTH;
    viz.trailPositions[idx * 3 + 0] = pos.x;
    viz.trailPositions[idx * 3 + 1] = 0.05;
    viz.trailPositions[idx * 3 + 2] = pos.z;
    viz.trailIndex++;

    viz.trailGeo.attributes.position.needsUpdate = true;
    viz.trailGeo.setDrawRange(0, Math.min(viz.trailIndex, TRAIL_LENGTH));
}
