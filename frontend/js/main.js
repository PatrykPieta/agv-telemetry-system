import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { AGVLoader } from './loader.js';

const container = document.getElementById('scene-container');
let scene, camera, renderer, controls;
let agvModel;
let wheelMeshes = []; 

const perfMonitor = document.getElementById("performance-monitor");

// --- NOWE: Kinematyka napędu różnicowego ---
let speedL = 0; // Prędkość lewej gąsienicy/kół
let speedR = 0; // Prędkość prawej gąsienicy/kół

function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x333333); 

    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(2, 2, 5); 

    renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" }); 
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio); 
    container.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8); 
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1); 
    directionalLight.position.set(5, 10, 7.5);
    scene.add(directionalLight);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; 

    const gridHelper = new THREE.GridHelper(20, 20); // Powiększyłam siatkę, bo wózek zacznie skręcać!
    scene.add(gridHelper);

    const agvLoader = new AGVLoader(scene);
    
    agvLoader.loadModel('assets/models/agv.glb') 
        .then(model => {
            agvModel = model;
            window.agvModel = model;

            const materialPodwozie = new THREE.MeshStandardMaterial({ color: 0x6A0DAD, metalness: 0.6, roughness: 0.4 });
            const materialKola = new THREE.MeshStandardMaterial({ color: 0x151515, metalness: 0.1, roughness: 0.8 });

            agvModel.traverse(node => {
                if (node.isMesh) {
                    const name = node.name.toLowerCase();
                    if (name.includes('koło') || name.includes('wheel')) {
                        node.material = materialKola;
                        wheelMeshes.push(node); 
                    } else {
                        node.material = materialPodwozie;
                    }
                }
            });

            setupWebSocket(); 
            animate(); 
        })
        .catch(error => console.error("Błąd ładowania modelu", error));
}

function onWindowResize() {
    // Łapiemy kontener dla pewności wewnątrz funkcji
    const container = document.getElementById('scene-container'); 
    
    // Obliczamy nowe proporcje na podstawie 65% ekranu, a nie całego
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    
    // Ustawiamy nowy, bezpieczny rozmiar dla płótna 3D
    renderer.setSize(container.clientWidth, container.clientHeight);
}
window.addEventListener('resize', onWindowResize);
// --- PĘTLA ANIMACJI Z FIZYKĄ ---
// --- NOWE: Kinematyka kół Omniwheel (Mecanum) ---
let rpmFL = 0; // Prędkość koła lewy-przód
let rpmFR = 0; // Prędkość koła prawy-przód
let rpmRL = 0; // Prędkość koła lewy-tył
let rpmRR = 0; // Prędkość koła prawy-tył

// Parametry geometrii wózka do przeliczeń fizyki
const AGV_GEOMETRY = {
    wheelRadius: 0.1,  // Promień koła w metrach
    lx: 0.4,           // Odległość od środka do osi przedniej/tylnej
    ly: 0.3            // Odległość od środka do osi lewej/prawej
};

// --- PĘTLA ANIMACJI Z FIZYKĄ OMNIWHEEL ---
function animate() {
    requestAnimationFrame(animate);
    controls.update(); 

    if (agvModel) {
        // 1. Zamiana prędkości obrotowej (RPM) na prędkość liniową (m/s)
        const toMps = (rpm) => (rpm / 60) * 2 * Math.PI * AGV_GEOMETRY.wheelRadius;
        
        const vFL = toMps(rpmFL);
        const vFR = toMps(rpmFR);
        const vRL = toMps(rpmRL);
        const vRR = toMps(rpmRR);

        // 2. Właściwa kinematyka Mecanum
        let forwardSpeed = (vFL + vFR + vRL + vRR) / 4; 
        let strafeSpeed  = (-vFL + vFR + vRL - vRR) / 4; 
        let turnSpeed    = (-vFL + vFR - vRL + vRR) / (4 * (AGV_GEOMETRY.lx + AGV_GEOMETRY.ly));

        // 3. Ruch całego wózka w przestrzeni
        agvModel.translateX(forwardSpeed * 0.1); // Oś X (Przód/Tył u Ciebie)
        agvModel.translateZ(strafeSpeed * 0.1);  // Oś Z (Jazda w BOK!)
        agvModel.rotateY(turnSpeed * 0.05);      // Oś Y (Obrót ramy w miejscu)

        // 4. Płynne kręcenie samymi kołami
        wheelMeshes.forEach(wheel => {
            const name = wheel.name.toLowerCase();
            let rotationVelocity = forwardSpeed * 0.05; // Wartość domyślna
            
            // Dopasowanie kręcenia do konkretnego koła po jego nazwie z Blendera
            if (name.includes('fl') || name.includes('front_left')) rotationVelocity = vFL;
            if (name.includes('fr') || name.includes('front_right')) rotationVelocity = vFR;
            if (name.includes('rl') || name.includes('rear_left')) rotationVelocity = vRL;
            if (name.includes('rr') || name.includes('rear_right')) rotationVelocity = vRR;
            
            wheel.rotateY(rotationVelocity * 0.5); 
        });

        // 5. Reset pozycji (żeby nie uciekł z ekranu)
        if (agvModel.position.length() > 10) {
            agvModel.position.set(0, 0, 0);
        }
    if (perfMonitor) {
        perfMonitor.innerHTML = `
            DRAW CALLS: ${renderer.info.render.calls} <br>
            TRÓJKĄTY:   ${renderer.info.render.triangles} <br>
            GEOMETRIE:  ${renderer.info.memory.geometries}
        `;
    }
    }
   
    renderer.render(scene, camera);
}

// --- NASŁUCHIWANIE DANYCH ---
function setupWebSocket() {
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
    
    // 1. TARCZA OCHRONNA: Jeśli to nie jest JSON, ignorujemy, żeby nie zabić skryptu
    try {
        data = JSON.parse(event.data);
        console.log("📦 Przyszła paczka z serwera:", data);
    } catch (error) {
        console.warn("Zignorowano śmieciową paczkę:", event.data);
        return; 
    }

    // 2. MÓZG BIG DATA: Odbiór alarmu o zatarciu koła ze Sparka
    if (data.ALERT_MSG) {
        console.error("🔥 ALARM Z SYSTEMU BIG DATA:", data.ALERT_MSG);
        
        const statusEl = document.getElementById('status');
        if (statusEl) {
            statusEl.innerText = "🔥 ZATARCIE KOŁA!";
            statusEl.style.color = "#ff0000"; 
        }

        if (agvModel) {
            agvModel.traverse(node => {
                // Czerwony alarm dla podwozia
                if (node.isMesh && (!node.name.toLowerCase().includes('koło') && !node.name.toLowerCase().includes('wheel'))) {
                    node.material.color.setHex(0xff0000); 
                }
            });
        }
        return; // Zakończ obieg, to był tylko alarm
    }

    // 3. ZAKTUALIZOWANA LOGIKA OMNIWHEEL (Zbieranie danych dla 4 kół)
    if (data.telemetry && data.telemetry.motors) {
        // UI
        const rpmEl = document.getElementById('ui-rpm');
        const voltEl = document.getElementById('ui-volt');
        if (rpmEl) rpmEl.innerText = data.telemetry.motors.front_left.speed_rpm;
        if (voltEl) voltEl.innerText = data.telemetry.power_supply.bus_voltage_V;

        // NOWOŚĆ: Przypisujemy RPM dla każdego koła osobno do zmiennych globalnych
        rpmFL = data.telemetry.motors.front_left.speed_rpm;
        rpmFR = data.telemetry.motors.front_right.speed_rpm;
        rpmRL = data.telemetry.motors.rear_left.speed_rpm;
        rpmRR = data.telemetry.motors.rear_right.speed_rpm;
    }
    };
}

// Wywołanie startowe - musi zostać!
init();