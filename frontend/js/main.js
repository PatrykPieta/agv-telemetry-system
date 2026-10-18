import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { AGVLoader } from './loader.js';

import { setupEnvironment } from './environment.js';
import { setupGUI } from './gui.js';
import { updatePhysics, updateBaselinePhysics } from './physics.js';
import { setupWebSocket } from './network.js';
import { setupCuriosityViz, updateCuriosityViz, appendTrailPoint } from './curiosity_viz.js';

const container = document.getElementById('scene-container');
let scene, camera, renderer, controls;
let previousFrameTime = null;

// Tryb kamery: 'agv01' | 'agv02' | 'fleet' | 'free'
let cameraMode = 'agv01';

// AGV-01: Neuro-Curiosity (Nowy model CAD Mecanum)
let agv01Model = null;
let wheelMeshes01 = [];

// AGV-02: Baseline Agent / Wózek Inżynierski (Model referencyjny)
let agv02Model = null;
let wheelMeshes02 = [];

let obstacleMeshes = [];
const MAX_OBSTACLES = 20;

// --- GLOBALNY STAN TELEMETRII ---
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

let curiosityViz = null;
let guiInstance = null;
let materialChassis01 = null;

// Zmienne wydajnościowe
let lastFpsTime = performance.now();
let framesThisSecond = 0;
let currentFPS = 0;

function init() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(55, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(4.0, 3.0, 5.5);

    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.3;

    const envLights = setupEnvironment(scene);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.zoomSpeed = 0.6;
    controls.maxDistance = 120;
    controls.minDistance = 1.0;
    controls.maxPolarAngle = Math.PI / 2 - 0.02;
    controls.target.set(0, 0.5, 0);

    setupCameraControls();
    setupObstaclePool();

    const agvLoader = new AGVLoader(scene);
    const statusEl = document.getElementById('status');
    if (statusEl) statusEl.textContent = 'Ładowanie wózków AGV (Flota)...';

    // 1. ŁADOWANIE AGV-01: Neuro-Curiosity (Nowy model Mecanum AGV_SIM_F.glb)
    agvLoader.loadModel('assets/models/AGV_SIM_F.glb', 2.2, { x: 0, y: 0, z: 0 }, 'AGV_01_NEURO')
        .then(root01 => {
            agv01Model = root01;
            window.agvModel = root01;

            // Wyraziste materiały PBR AGV-01: Tytan + Szafir AGH + Aluminium
            materialChassis01 = new THREE.MeshStandardMaterial({
                color: 0x3a4856,
                metalness: 0.75,
                roughness: 0.3,
            });
            const materialWheel01 = new THREE.MeshStandardMaterial({
                color: 0xcccccc,
                metalness: 0.85,
                roughness: 0.2,
            });
            const materialRoller01 = new THREE.MeshStandardMaterial({
                color: 0x181818,
                metalness: 0.1,
                roughness: 0.9,
            });
            const materialAccent01 = new THREE.MeshStandardMaterial({
                color: 0x0077cc,
                metalness: 0.6,
                roughness: 0.35,
                emissive: new THREE.Color(0x002244),
                emissiveIntensity: 0.5,
            });

            agv01Model.traverse(node => {
                if (!node.isMesh) return;
                node.castShadow = true;
                node.receiveShadow = true;
                const n = node.name.toLowerCase();

                if (n.includes('roller')) {
                    node.material = materialRoller01;
                    wheelMeshes01.push(node);
                } else if (n.includes('mecanum') || n.includes('side') || n.includes('wheel') || n.includes('kolo')) {
                    node.material = materialWheel01;
                    wheelMeshes01.push(node);
                } else if (n.includes('mirror')) {
                    node.material = materialWheel01;
                    wheelMeshes01.push(node);
                } else {
                    node.material = (node.id % 2 === 0) ? materialChassis01 : materialAccent01;
                }
            });

            // Nakładka kognitywna Neuro-Curiosity (ring aury, wektor, ślad)
            curiosityViz = setupCuriosityViz(scene, agv01Model);

            // 2. ŁADOWANIE AGV-02: Baseline Agent (Oryginalny model agv.glb)
            return agvLoader.loadModel('assets/models/agv.glb', 2.1, { x: 5, y: 0, z: 4 }, 'AGV_02_BASELINE');
        })
        .then(root02 => {
            agv02Model = root02;
            window.agv02Model = root02;

            // Barwy AGV-02: Industrial Amber / Safety Orange + Carbon (dla kontrastu z AGV-01)
            const materialChassis02 = new THREE.MeshStandardMaterial({
                color: 0xff6600,       // Pomarańcz ostrzegawczy
                metalness: 0.45,
                roughness: 0.4,
            });
            const materialWheel02 = new THREE.MeshStandardMaterial({
                color: 0x151515,
                metalness: 0.3,
                roughness: 0.7,
            });

            agv02Model.traverse(node => {
                if (!node.isMesh) return;
                node.castShadow = true;
                node.receiveShadow = true;
                const n = node.name.toLowerCase();
                if (n.includes('wheel') || n.includes('koło') || n.includes('kolo')) {
                    node.material = materialWheel02;
                    wheelMeshes02.push(node);
                } else {
                    node.material = materialChassis02;
                }
            });

            // Dodaj marker świetlny na AGV-02 (pomarańczowy beacon)
            const beacon = new THREE.PointLight(0xff6600, 0.8, 4.0);
            beacon.position.set(0, 0.5, 0);
            agv02Model.add(beacon);

            console.log('[IDUB] Oba wózki AGV-01 i AGV-02 załadowane pomyślnie!');
            if (statusEl) statusEl.textContent = '🟢 Flota AGV aktywna';
        })
        .catch(err => {
            console.warn('[IDUB] Ostrzeżenie przy ładowaniu floty:', err);
            if (statusEl) statusEl.textContent = '🟢 Gotowe';
        })
        .finally(() => {
            if (materialChassis01) {
                guiInstance = setupGUI(envLights.ambientLight, envLights.directionalLight, envLights.floorMaterial, materialChassis01);
            }
            setupSceneOptionsButton();
            setupWebSocket(agv01Model, obstacleMeshes, rpmsState, rlState);
            animate();
        });
}

// --- KONTROLA KAMERY ---

function setupCameraControls() {
    const btn01 = document.getElementById('cam-agv01');
    const btn02 = document.getElementById('cam-agv02');
    const btnFleet = document.getElementById('cam-fleet');
    const btnFree = document.getElementById('cam-free');
    const legacyToggle = document.getElementById('camera-toggle');

    function setActiveBtn(activeBtn) {
        [btn01, btn02, btnFleet, btnFree, legacyToggle].forEach(b => {
            if (b) b.classList.remove('active');
        });
        if (activeBtn) activeBtn.classList.add('active');
    }

    if (btn01) {
        btn01.addEventListener('click', () => {
            cameraMode = 'agv01';
            setActiveBtn(btn01);
            if (agv01Model) {
                const p = new THREE.Vector3();
                agv01Model.getWorldPosition(p);
                camera.position.set(p.x + 3.5, p.y + 2.5, p.z + 4.5);
                controls.target.copy(p);
            }
        });
    }

    if (btn02) {
        btn02.addEventListener('click', () => {
            cameraMode = 'agv02';
            setActiveBtn(btn02);
            if (agv02Model) {
                const p = new THREE.Vector3();
                agv02Model.getWorldPosition(p);
                camera.position.set(p.x + 3.5, p.y + 2.5, p.z + 4.5);
                controls.target.copy(p);
            }
        });
    }

    if (btnFleet) {
        btnFleet.addEventListener('click', () => {
            cameraMode = 'fleet';
            setActiveBtn(btnFleet);
            camera.position.set(0, 22, 26);
            controls.target.set(0, 0, 0);
        });
    }

    if (btnFree || legacyToggle) {
        const handler = () => {
            if (cameraMode !== 'free') {
                cameraMode = 'free';
                if (legacyToggle) legacyToggle.innerText = '🔒 Podążaj za wózkiem';
                setActiveBtn(btnFree || legacyToggle);
            } else {
                cameraMode = 'agv01';
                if (legacyToggle) legacyToggle.innerText = '🔓 Odłącz kamerę';
                setActiveBtn(btn01);
            }
        };
        if (btnFree) btnFree.addEventListener('click', handler);
        if (legacyToggle) legacyToggle.addEventListener('click', handler);
    }
}

function setupSceneOptionsButton() {
    const btn = document.getElementById('scene-options');
    if (!btn || !guiInstance) return;
    btn.addEventListener('click', () => {
        if (guiInstance._hidden) {
            guiInstance.show();
        } else {
            guiInstance.hide();
        }
    });
}

function setupObstaclePool() {
    const geo = new THREE.BoxGeometry(1, 1, 1);
    for (let i = 0; i < MAX_OBSTACLES; i++) {
        const mat = new THREE.MeshStandardMaterial({
            color: 0xff4400,
            transparent: true,
            opacity: 0.8,
            emissive: new THREE.Color(0x331000),
            emissiveIntensity: 0.6,
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
            `DRAWS: ${renderer.info.render.calls}<br>` +
            `TRIS: ${renderer.info.render.triangles.toLocaleString()}`;
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

    // 1. Aktualizacja AGV-01 (Neuro-Curiosity)
    if (agv01Model) {
        updatePhysics(agv01Model, wheelMeshes01, rpmsState, dt);

        if (curiosityViz) {
            updateCuriosityViz(curiosityViz, rlState, dt);
            appendTrailPoint(curiosityViz, agv01Model);
        }
    }

    // 2. Aktualizacja AGV-02 (Baseline Agent / Badania porównawcze)
    if (agv02Model) {
        updateBaselinePhysics(agv02Model, wheelMeshes02, dt, agv01Model);
    }

    // 3. Obsługa kamery w zależności od wybranego trybu
    if (cameraMode === 'agv01' && agv01Model) {
        const target = new THREE.Vector3();
        agv01Model.getWorldPosition(target);
        const prev = controls.target.clone();
        camera.position.add(target.clone().sub(prev));
        controls.target.copy(target);
    } else if (cameraMode === 'agv02' && agv02Model) {
        const target = new THREE.Vector3();
        agv02Model.getWorldPosition(target);
        const prev = controls.target.clone();
        camera.position.add(target.clone().sub(prev));
        controls.target.copy(target);
    } else if (cameraMode === 'fleet' && agv01Model && agv02Model) {
        // Punkt skupienia pomiędzy oboma wózkami
        const p1 = new THREE.Vector3();
        const p2 = new THREE.Vector3();
        agv01Model.getWorldPosition(p1);
        agv02Model.getWorldPosition(p2);
        const midPoint = p1.clone().add(p2).multiplyScalar(0.5);
        controls.target.lerp(midPoint, 0.05);
    }

    updateRLHUD();
    updateFPS();

    controls.update();
    renderer.render(scene, camera);
}

init();