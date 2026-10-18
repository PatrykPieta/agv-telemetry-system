import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { AGVLoader } from './loader.js';

import { setupEnvironment } from './environment.js';
import { setupGUI } from './gui.js';
import { updatePhysics } from './physics.js';
import { setupWebSocket } from './network.js';
import { setupCuriosityViz, updateCuriosityViz } from './curiosity_viz.js';

const container = document.getElementById('scene-container');
let scene, camera, renderer, controls;
let previousFrameTime = null;
let followCamera = true;
let agvModel;
let wheelMeshes = [];
let obstacleMeshes = [];
const MAX_OBSTACLES = 20;

// --- GLOBALNY STAN APLIKACJI ---
const rpmsState = { FL: 0, FR: 0, RL: 0, RR: 0 };
const rlState = {
    intrinsic_reward: 0,
    extrinsic_reward: 0,
    total_reward: 0,
    icm_prediction_error: 0,
    policy_entropy: 0,
    jerk_mps3: 0,
    sim_to_real_gap: 0,
    training_step: 0,
    algorithm: 'PPO+ICM',
    policy: 'NeuroC_v1',
};

let materialChassis;

// Zmienne wydajnościowe
let lastFpsTime = performance.now();
let framesThisSecond = 0;
let currentFPS = 0;

// Curiosity viz objects (populated after model loads)
let curiosityViz = null;

function init() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.05, 500);
    camera.position.set(3, 2, 5);

    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;

    const envLights = setupEnvironment(scene);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.zoomSpeed = 0.5;
    controls.maxDistance = 80;
    controls.minDistance = 0.5;
    controls.maxPolarAngle = Math.PI / 2 - 0.02;

    setupCameraToggle();
    setupObstaclePool();

    const agvLoader = new AGVLoader(scene);
    agvLoader.loadModel('assets/models/AGV_SIM_F.glb')
        .then(model => {
            agvModel = model;
            window.agvModel = model;

            // Apply industrial PBR materials
            materialChassis = new THREE.MeshStandardMaterial({
                color: 0x1a2a3a,       // Dark industrial blue-grey
                metalness: 0.7,
                roughness: 0.3,
            });
            const materialWheel = new THREE.MeshStandardMaterial({
                color: 0x222222,
                metalness: 0.4,
                roughness: 0.6,
            });
            const materialRoller = new THREE.MeshStandardMaterial({
                color: 0x333333,
                metalness: 0.2,
                roughness: 0.8,
            });
            const materialAccent = new THREE.MeshStandardMaterial({
                color: 0x005fa3,       // AGH blue accent
                metalness: 0.5,
                roughness: 0.4,
                emissive: new THREE.Color(0x001a30),
                emissiveIntensity: 0.3,
            });

            agvModel.traverse(node => {
                if (!node.isMesh) return;
                node.castShadow = true;
                node.receiveShadow = true;
                const n = node.name;
                if (/Roller_/i.test(n) || /MirrorRoller/i.test(n) || /MirrorMirrorRoller/i.test(n)) {
                    node.material = materialRoller;
                    wheelMeshes.push(node);
                } else if (/Mecanum/i.test(n) || /Side\s*[12]/i.test(n)) {
                    node.material = materialWheel;
                    wheelMeshes.push(node);
                } else if (/Mirror/i.test(n)) {
                    node.material = materialWheel;
                    wheelMeshes.push(node);
                } else {
                    // Alternate chassis vs accent by mesh index for visual interest
                    node.material = (node.id % 3 === 0) ? materialAccent : materialChassis;
                }
            });

            console.log('[IDUB] Wheel meshes found:', wheelMeshes.length);

            // Setup curiosity visualization overlay on the AGV
            curiosityViz = setupCuriosityViz(scene, agvModel);

            setupGUI(envLights.ambientLight, envLights.directionalLight, envLights.floorMaterial, materialChassis);
            setupWebSocket(agvModel, obstacleMeshes, rpmsState, rlState);

            animate();
        })
        .catch(error => {
            console.error('[IDUB] Błąd ładowania modelu', error);
            document.getElementById('status').textContent = 'Błąd ładowania modelu 3D';
        });
}

// --- FUNKCJE POMOCNICZE ---

function setupCameraToggle() {
    const btn = document.getElementById('camera-toggle');
    if (!btn) return;
    btn.addEventListener('click', () => {
        followCamera = !followCamera;
        if (followCamera) {
            btn.innerText = '🔓 Odłącz kamerę';
            btn.style.color = '#fff';
            if (agvModel) {
                const t = new THREE.Vector3();
                agvModel.getWorldPosition(t);
                controls.target.copy(t);
            }
        } else {
            btn.innerText = '🔒 Podążaj za wózkiem';
            btn.style.color = '#00ff00';
        }
    });
}

function setupObstaclePool() {
    const geo = new THREE.BoxGeometry(1, 1, 1);
    for (let i = 0; i < MAX_OBSTACLES; i++) {
        const mat = new THREE.MeshStandardMaterial({
            color: 0xff6600,
            transparent: true,
            opacity: 0.75,
            emissive: new THREE.Color(0x331400),
            emissiveIntensity: 0.5,
        });
        const mesh = new THREE.Mesh(geo, mat);
        mesh.visible = false;
        mesh.castShadow = true;
        scene.add(mesh);
        obstacleMeshes.push(mesh);
    }
}

function updateClock() {
    const el = document.getElementById('ui-clock');
    if (!el) return;
    const now = new Date();
    el.innerText =
        now.getFullYear() + '-' +
        String(now.getMonth() + 1).padStart(2, '0') + '-' +
        String(now.getDate()).padStart(2, '0') + ' ' +
        String(now.getHours()).padStart(2, '0') + ':' +
        String(now.getMinutes()).padStart(2, '0') + ':' +
        String(now.getSeconds()).padStart(2, '0');
}

function updateRLHUD() {
    const fields = [
        ['hud-intrinsic',   rlState.intrinsic_reward.toFixed(3),       rlState.intrinsic_reward > 0.5 ? '#ffdd00' : '#00ff99'],
        ['hud-extrinsic',   rlState.extrinsic_reward.toFixed(3),       '#00c8ff'],
        ['hud-total-r',     rlState.total_reward.toFixed(3),           '#ffffff'],
        ['hud-icm-error',   rlState.icm_prediction_error.toFixed(3),   rlState.icm_prediction_error > 0.4 ? '#ff4444' : '#aaaaaa'],
        ['hud-entropy',     rlState.policy_entropy.toFixed(3),         '#bb88ff'],
        ['hud-jerk',        rlState.jerk_mps3.toFixed(3),              rlState.jerk_mps3 > 0.15 ? '#ffaa00' : '#aaffaa'],
        ['hud-gap',         rlState.sim_to_real_gap.toFixed(3),        rlState.sim_to_real_gap > 0.5 ? '#ff6666' : '#66ff99'],
        ['hud-step',        rlState.training_step.toLocaleString(),    '#aaaaaa'],
    ];
    for (const [id, val, color] of fields) {
        const el = document.getElementById(id);
        if (el) { el.textContent = val; el.style.color = color; }
    }

    // Progress bars
    _bar('bar-intrinsic', rlState.intrinsic_reward);
    _bar('bar-icm-error', rlState.icm_prediction_error);
    _bar('bar-gap',       rlState.sim_to_real_gap);
    _bar('bar-entropy',   Math.min(1, rlState.policy_entropy / 2));
}

function _bar(id, ratio) {
    const el = document.getElementById(id);
    if (el) el.style.width = (Math.max(0, Math.min(1, ratio)) * 100).toFixed(1) + '%';
}

function updateFPS() {
    const now = performance.now();
    framesThisSecond++;
    if (now >= lastFpsTime + 1000) {
        currentFPS = framesThisSecond;
        framesThisSecond = 0;
        lastFpsTime = now;
    }
    const el = document.getElementById('performance-monitor');
    if (el) {
        el.innerHTML =
            `FPS: ${currentFPS}<br>` +
            `DRAW CALLS: ${renderer.info.render.calls}<br>` +
            `TRIANGLES: ${renderer.info.render.triangles.toLocaleString()}<br>` +
            `MESHES: ${renderer.info.memory.geometries}`;
    }
}

function onWindowResize() {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}
window.addEventListener('resize', onWindowResize);

// --- PĘTLA GŁÓWNA ---

function animate(frameTime = performance.now()) {
    requestAnimationFrame(animate);
    const dt = previousFrameTime === null ? 0 : (frameTime - previousFrameTime) / 1000;
    previousFrameTime = frameTime;

    updateClock();

    if (agvModel) {
        updatePhysics(agvModel, wheelMeshes, rpmsState, dt);

        if (curiosityViz) updateCuriosityViz(curiosityViz, rlState, dt);

        if (followCamera) {
            const target = new THREE.Vector3();
            agvModel.getWorldPosition(target);
            const prev = controls.target.clone();
            camera.position.add(target.clone().sub(prev));
            controls.target.copy(target);
        }

        updateRLHUD();
        updateFPS();
    }

    controls.update();
    renderer.render(scene, camera);

    if (Math.abs(camera.position.x) > 2000 || isNaN(camera.position.x)) {
        console.error('AWARIA KAMERY:', camera.position);
        controls.enabled = false;
    }
}

init();