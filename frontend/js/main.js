import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { AGVLoader } from './loader.js';

// --- IMPORTY TWOICH NOWYCH MODUŁÓW ---
import { setupEnvironment } from './environment.js';
import { setupGUI } from './gui.js';
import { updatePhysics } from './physics.js';
import { setupWebSocket } from './network.js';

const container = document.getElementById('scene-container');
let scene, camera, renderer, controls;
let previousAGVPosition = null; // <-- DODAJ TĘ ZMIENNĄ
let followCamera = true;
let agvModel;
let wheelMeshes = [];
let obstacleMeshes = [];
const MAX_OBSTACLES = 15;

// --- GLOBALNY STAN APLIKACJI ---
const rpmsState = { FL: 0, FR: 0, RL: 0, RR: 0 };
let materialPodwozie;

// Zmienne wydajnościowe
let lastFpsTime = performance.now();
let framesThisSecond = 0;
let currentFPS = 0;

function init() {

    // --- NASZ DOWÓD NA TO, ŻE KOD SIĘ ODŚWIEŻYŁ ---
    console.log("🚀 START SYSTEMU - WERSJA 100");
    // ----------------------------------------------
    
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    // Pierwotna pozycja kamery
    camera.position.set(2, 2, 5);

    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    const envLights = setupEnvironment(scene);

   // PIERWOTNA KONFIGURACJA KONTROLERA (Czysty OrbitControls)
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; 
    controls.dampingFactor = 0.05; // Uściślamy bezwładność, żeby nie szarpało

    // --- NAPRAWA AGRESYWNEGO SCROLLA ---
    controls.zoomSpeed = 0.50; // Zmniejszamy czułość scrolla o 95%! 

    // Ograniczniki (zostawiamy je, to dobra inżynierska praktyka)
    controls.maxDistance = 60; 
    controls.minDistance = 3;  
    controls.maxPolarAngle = Math.PI / 2 - 0.02;
    // --- PUŁAPKA DIAGNOSTYCZNA ---
    let logCounter = 0;
    controls.addEventListener('change', () => {
        logCounter++;
        
    });
    // -----------------------------


    setupCameraToggle();
    setupObstaclePool();

    const agvLoader = new AGVLoader(scene);
    agvLoader.loadModel('assets/models/agv.glb')
        .then(model => {
            agvModel = model;
            window.agvModel = model;
            model.scale.set(10, 10, 10);

            materialPodwozie = new THREE.MeshStandardMaterial({ color: 0x6A0DAD, metalness: 0.6, roughness: 0.4 });
            const materialKola = new THREE.MeshStandardMaterial({ color: 0x151515, metalness: 0.1, roughness: 0.8 });

            agvModel.traverse(node => {
                if (node.isMesh) {
                    node.castShadow = true;
                    node.receiveShadow = true;
                    const name = node.name.toLowerCase();
                    if (name.includes('koło') || name.includes('wheel')) {
                        node.material = materialKola;
                        wheelMeshes.push(node);
                    } else {
                        node.material = materialPodwozie;
                    }
                }
            });

            setupGUI(envLights.ambientLight, envLights.directionalLight, envLights.floorMaterial, materialPodwozie);
            setupWebSocket(agvModel, obstacleMeshes, rpmsState);
            
            animate();
        })
        .catch(error => console.error("Błąd ładowania modelu", error));
}

// --- FUNKCJE POMOCNICZE ---

function setupCameraToggle() {
    const cameraToggleBtn = document.getElementById('camera-toggle');
    if (cameraToggleBtn) {
        cameraToggleBtn.addEventListener('click', () => {
            followCamera = !followCamera;
            if (followCamera) {
                cameraToggleBtn.innerText = "🔓 Odłącz kamerę";
                cameraToggleBtn.style.color = "#fff";
                if (agvModel) {
                    const currentTarget = new THREE.Vector3();
                    agvModel.getWorldPosition(currentTarget);
                    controls.target.copy(currentTarget);
                }
            } else {
                cameraToggleBtn.innerText = "🔒 Podążaj za wózkiem";
                cameraToggleBtn.style.color = "#00ff00";
            }
        });
    }
}

function setupObstaclePool() {
    const obstacleGeometry = new THREE.BoxGeometry(1, 1, 1);
    for (let i = 0; i < MAX_OBSTACLES; i++) {
        const material = new THREE.MeshStandardMaterial({ color: 0x888888, transparent: true, opacity: 0.8 });
        const mesh = new THREE.Mesh(obstacleGeometry, material);
        mesh.visible = false;
        scene.add(mesh);
        obstacleMeshes.push(mesh);
    }
}

function updateClock() {
    const clockEl = document.getElementById('ui-clock');
    if (clockEl) {
        const now = new Date();
        clockEl.innerText = now.getFullYear() + "-" +
                            String(now.getMonth() + 1).padStart(2, '0') + "-" +
                            String(now.getDate()).padStart(2, '0') + " " +
                            String(now.getHours()).padStart(2, '0') + ":" +
                            String(now.getMinutes()).padStart(2, '0') + ":" +
                            String(now.getSeconds()).padStart(2, '0');
    }
}

function updateFPS() {
    const now = performance.now();
    framesThisSecond++;
    if (now >= lastFpsTime + 1000) {
        currentFPS = framesThisSecond;
        framesThisSecond = 0;
        lastFpsTime = now;
    }
    const perfMonitor = document.getElementById("performance-monitor");
    if (perfMonitor) {
        perfMonitor.innerHTML = `FPS: ${currentFPS} <br> DRAW CALLS: ${renderer.info.render.calls} <br> TRÓJKĄTY: ${renderer.info.render.triangles} <br> GEOMETRIE: ${renderer.info.memory.geometries}`;
    }
}

function onWindowResize() {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}
window.addEventListener('resize', onWindowResize);

// --- PĘTLA GŁÓWNA ---

// --- PĘTLA GŁÓWNA (main.js) ---

function animate() {
    requestAnimationFrame(animate);

    updateClock();

    if (agvModel) {
        // 1. FIZYKA: Na samym początku wprawiamy wózek w ruch (jeśli dotarły dane RPM)
        updatePhysics(agvModel, wheelMeshes, rpmsState);

        // 2. OBLICZANIE PODĄŻANIA: Wózek się ruszył, więc aktualizujemy pozycję kamery
        if (followCamera) {
            const currentTarget = new THREE.Vector3();
            agvModel.getWorldPosition(currentTarget);
            const previousTarget = controls.target.clone();
            const deltaMovement = currentTarget.clone().sub(previousTarget);

            // Przesuwamy fizycznie kamerę oraz jej punkt patrzenia (target)
            camera.position.add(deltaMovement);
            controls.target.copy(currentTarget);
        }

        updateFPS();
    }

    // 3. AKTUALIZACJA KONTROLERA ZAWSZE NA KOŃCU!
    // OrbitControls dowiaduje się o nowej pozycji i nie generuje konfliktów przy scrollowaniu
    controls.update(); 

    renderer.render(scene, camera);

    // --- DIAGNOSTYKA KAMERY ---
    if (camera.position.x > 1000 || isNaN(camera.position.x)) {
        console.error("💥 AWARIA KAMERY! Pozycja: ", camera.position);
        controls.enabled = false; // Odcinamy myszkę, żeby zatrzymać spam
    }
}
// Start
init();