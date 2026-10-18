/**
 * IDUB Neuro-Curiosity — Curiosity Visualization
 *
 * Renders Three.js overlays around the 2.2m AGV model to visually represent
 * the Intrinsic Curiosity Module (ICM) state:
 *   - A pulsing "curiosity aura" ring on the floor (intrinsic reward indicator)
 *   - A predicted trajectory arrow (forward model prediction)
 *   - ICM error flash effect (red glow when prediction error spikes)
 *   - Exploration trail points scattered along the robot path
 */
import * as THREE from 'three';

const AURA_SEGMENTS = 64;
const TRAIL_LENGTH = 60;

export function setupCuriosityViz(scene, agvModel) {
    // 1. Curiosity Aura Ring (floor level, around robot footprint ~1.8m x 2.2m)
    const auraGeo = new THREE.RingGeometry(1.25, 1.45, AURA_SEGMENTS);
    const auraMat = new THREE.MeshBasicMaterial({
        color: 0xffcc00,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.7,
        depthWrite: false,
    });
    const aura = new THREE.Mesh(auraGeo, auraMat);
    aura.rotation.x = -Math.PI / 2;
    aura.position.y = 0.02;
    agvModel.add(aura);

    // 2. Outer Sim-to-Real ripple ring
    const outerGeo = new THREE.RingGeometry(1.7, 1.85, AURA_SEGMENTS);
    const outerMat = new THREE.MeshBasicMaterial({
        color: 0x0099ff,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.5,
        depthWrite: false,
    });
    const outerRing = new THREE.Mesh(outerGeo, outerMat);
    outerRing.rotation.x = -Math.PI / 2;
    outerRing.position.y = 0.025;
    agvModel.add(outerRing);

    // 3. Predicted trajectory arrow (forward model prediction)
    const arrowDir = new THREE.Vector3(1, 0, 0);
    const arrowHelper = new THREE.ArrowHelper(
        arrowDir,
        new THREE.Vector3(0, 0.4, 0),
        1.6,
        0x00d4ff,
        0.35,
        0.18
    );
    agvModel.add(arrowHelper);

    // 4. ICM error spike PointLight (lights up red on unexpected obstacle)
    const spikeLight = new THREE.PointLight(0xff3300, 0, 5.0);
    spikeLight.position.set(0, 0.7, 0);
    agvModel.add(spikeLight);

    // 5. Exploration trail (persistent footprint points in world space)
    const trailGeo = new THREE.BufferGeometry();
    const trailPositions = new Float32Array(TRAIL_LENGTH * 3);
    trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
    const trailMat = new THREE.PointsMaterial({
        color: 0x00ffaa,
        size: 0.12,
        transparent: true,
        opacity: 0.7,
        depthWrite: false,
        sizeAttenuation: true,
    });
    const trail = new THREE.Points(trailGeo, trailMat);
    scene.add(trail);

    return {
        aura, auraMat,
        outerRing, outerMat,
        arrowHelper,
        spikeLight,
        trail, trailGeo, trailPositions,
        trailIndex: 0,
        lastTrailTime: 0,
        phase: 0,
    };
}

export function updateCuriosityViz(viz, rlState, dt) {
    if (!viz) return;
    viz.phase += dt * 3.0;

    const ir = rlState.intrinsic_reward || 0;
    const icmErr = rlState.icm_prediction_error || 0;
    const gap = rlState.sim_to_real_gap || 0;

    // Aura pulse: scale and opacity modulated by intrinsic curiosity reward
    const pulse = 0.6 + 0.4 * Math.sin(viz.phase * 2);
    viz.auraMat.opacity = Math.max(0.15, ir * 0.8 * pulse);
    const auraScale = 1.0 + ir * 0.25 * pulse;
    viz.aura.scale.set(auraScale, auraScale, 1);

    // Outer ring: sim-to-real gap ripple
    viz.outerMat.opacity = Math.max(0.1, gap * 0.6 * (0.5 + 0.5 * Math.sin(viz.phase * 1.5)));
    const outerScale = 1.0 + gap * 0.2;
    viz.outerRing.scale.set(outerScale, outerScale, 1);

    // ICM error spike light
    if (icmErr > 0.35) {
        viz.spikeLight.intensity = icmErr * 4.0 * (0.6 + 0.4 * Math.sin(viz.phase * 6));
    } else {
        viz.spikeLight.intensity = 0;
    }

    // Direction arrow: changes color to orange/red on high prediction error
    const len = 1.0 + ir * 1.2;
    viz.arrowHelper.setLength(len, Math.min(0.4, len * 0.25), 0.18);
    viz.arrowHelper.setColor(icmErr > 0.4 ? 0xff4422 : 0x00d4ff);
}

export function appendTrailPoint(viz, agvModel) {
    if (!agvModel || !viz) return;
    const now = performance.now();
    if (now - viz.lastTrailTime < 250) return; // drop point every 250ms
    viz.lastTrailTime = now;

    const pos = new THREE.Vector3();
    agvModel.getWorldPosition(pos);

    const idx = (viz.trailIndex % TRAIL_LENGTH) * 3;
    viz.trailPositions[idx + 0] = pos.x;
    viz.trailPositions[idx + 1] = 0.05;
    viz.trailPositions[idx + 2] = pos.z;
    viz.trailIndex++;

    viz.trailGeo.attributes.position.needsUpdate = true;
    viz.trailGeo.setDrawRange(0, Math.min(viz.trailIndex, TRAIL_LENGTH));
}
