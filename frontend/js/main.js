import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { AGVLoader } from './loader.js';

const container = document.getElementById('scene-container');
let scene, camera, renderer, controls;
let followCamera = true; // Domyślnie kamera podąża za wózkiem
let agvModel;
let wheelMeshes = []; 
let obstacleMeshes = []; 
const MAX_OBSTACLES = 15; // Tworzymy pulę 15 sześcianów

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
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap; // Miękkie, rozmyte brzegi cieni (efekt premium)

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8); 
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2); 
    directionalLight.position.set(10, 20, 15); // Wyżej i mocniej z boku
    directionalLight.castShadow = true;        // Aktywacja rzucania cieni
    
    // Konfiguracja rozdzielczości cieni (im wyższa, tym cienie są ostrzejsze, 2048 to złoty środek)
    directionalLight.shadow.mapSize.width = 1024;
    directionalLight.shadow.mapSize.height = 1024;
    // Zasięg kamery cienia (dopasowany do wielkości wózka)
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 40;
    directionalLight.shadow.camera.left = -10;
    directionalLight.shadow.camera.right = 10;
    directionalLight.shadow.camera.top = 10;
    directionalLight.shadow.camera.bottom = -10;
    
    scene.add(directionalLight);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; 

    // --- NOWOŚĆ: EFEKT MGŁY (Nadaje głębię i ukrywa krawędzie świata) ---
    scene.fog = new THREE.FogExp2(0x333333, 0.03); // Kolor mgły zgodny z tłem, gęstość 0.03

    // --- NOWOŚĆ: REALISTYCZNA POSADZKA HALI (Beton/Metal) ---
    const floorGeometry = new THREE.PlaneGeometry(100, 100); // Hala o wymiarach 100x100 metrów
    const floorMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x1a1a1a,      // Ciemna, przemysłowa posadzka
        roughness: 0.4,       // Lekki połysk odbijający światło reflektorów
        metalness: 0.3        // Delikatny metaliczny akcent
    });
    const floorMesh = new THREE.Mesh(floorGeometry, floorMaterial);
    floorMesh.rotation.x = -Math.PI / 2; // Obracamy płaszczyznę poziomo
    floorMesh.receiveShadow = true;      // Posadzka będzie przyjmować cienie wózka!
    scene.add(floorMesh);

    // --- NOWOŚĆ: SUBTELNA SIATKA PRZEMYSŁOWA ---
    // Główne linie co 2 metry, mniejsze co 1 metr
    const gridHelper = new THREE.GridHelper(100, 50, 0x444444, 0x252525);
    gridHelper.position.y = 0.01; // Minimalnie uniesiona nad podłogę, aby uniknąć tzw. z-fightingu (migania tekstur)
    scene.add(gridHelper);

    // --- NOWOŚĆ: Przycisk zmiany trybu kamery ---
    const cameraToggleBtn = document.getElementById('camera-toggle');
    if (cameraToggleBtn) {
        cameraToggleBtn.addEventListener('click', () => {
            followCamera = !followCamera; // Odwracamy stan
            
            if (followCamera) {
                cameraToggleBtn.innerText = "🔓 Odłącz kamerę";
                cameraToggleBtn.style.color = "#fff";
                
                // Kiedy znowu podpinamy kamerę, natychmiast każemy OrbitControls spojrzeć na wózek
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

    // --- INICJALIZACJA PULI PRZESZKÓD (OBJECT POOLING) ---
    const obstacleGeometry = new THREE.BoxGeometry(1, 1, 1); // Bazowy sześcian
    for (let i = 0; i < MAX_OBSTACLES; i++) {
        // Podstawowy materiał, kolor będziemy nadpisywać na bieżąco
        const material = new THREE.MeshStandardMaterial({ 
            color: 0x888888, 
            transparent: true, 
            opacity: 0.8 
        });
        const mesh = new THREE.Mesh(obstacleGeometry, material);
        mesh.visible = false; // Ukryte na start
        scene.add(mesh);
        obstacleMeshes.push(mesh);
    }

    const agvLoader = new AGVLoader(scene);
    
    agvLoader.loadModel('assets/models/agv.glb') 
        .then(model => {
            agvModel = model;
            window.agvModel = model;
            model.scale.set(10, 10, 10);

            const materialPodwozie = new THREE.MeshStandardMaterial({ color: 0x6A0DAD, metalness: 0.6, roughness: 0.4 });
            const materialKola = new THREE.MeshStandardMaterial({ color: 0x151515, metalness: 0.1, roughness: 0.8 });

            agvModel.traverse(node => {
                if (node.isMesh) {
                    node.castShadow = true;     // <-- NOWOŚĆ: wózek rzuca cień
                    node.receiveShadow = true;  // <-- NOWOŚĆ: elementy wózka cieniują same siebie
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
// --- PĘTLA ANIMACJI Z FIZYKĄ OMNIWHEEL ---
// --- PĘTLA ANIMACJI Z FIZYKĄ OMNIWHEEL ---
function animate() {
    requestAnimationFrame(animate);
    controls.update(); 

    if (agvModel) {
        // --- INTELIGENTNA KAMERA PODĄŻAJĄCA ---
        if (followCamera) { // <-- Robimy to tylko, gdy przełącznik jest włączony
            const currentTarget = new THREE.Vector3();
            agvModel.getWorldPosition(currentTarget); 
            
            const previousTarget = controls.target.clone();
            const deltaMovement = currentTarget.clone().sub(previousTarget);

            camera.position.add(deltaMovement);
            controls.target.copy(currentTarget);
        }
        // ----------------------------------------------

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
        if (agvModel.position.length() > 50) {
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
        
        // 1. TARCZA OCHRONNA (Parsowanie musi być absolutnie pierwsze!)
        try {
            data = JSON.parse(event.data);
            // Wyłączamy console.log, żeby nie "zaspamować" przeglądarki przy 10 klatkach na sekundę
            // console.log("📦 Przyszła paczka z serwera:", data); 
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
            return; // Zakończ obieg, to był tylko alarm, nie ma tu telemetrii
        }

        // 3. ZAKTUALIZOWANA LOGIKA OMNIWHEEL (Zbieranie danych dla 4 kół)
        if (data.telemetry && data.telemetry.motors) {
            // UI
            const rpmEl = document.getElementById('ui-rpm');
            const voltEl = document.getElementById('ui-volt');
            if (rpmEl) rpmEl.innerText = data.telemetry.motors.front_left.speed_rpm;
            if (voltEl) voltEl.innerText = data.telemetry.power_supply.bus_voltage_V;

            // Przypisujemy RPM dla każdego koła osobno do zmiennych globalnych
            rpmFL = data.telemetry.motors.front_left.speed_rpm;
            rpmFR = data.telemetry.motors.front_right.speed_rpm;
            rpmRL = data.telemetry.motors.rear_left.speed_rpm;
            rpmRR = data.telemetry.motors.rear_right.speed_rpm;
        }

        // 4. NOWOŚĆ: Rysowanie Przeszkód z LiDAR-a (DBSCAN)
        if (data.obstacles) {
            // Najpierw ukrywamy wszystkie aktywne przeszkody
            obstacleMeshes.forEach(mesh => mesh.visible = false);

            // Mapujemy nowe dane na sześciany z naszej puli
            for (let i = 0; i < data.obstacles.length; i++) {
                if (i >= MAX_OBSTACLES) break; // Zabezpieczenie przed brakiem sześcianów w puli

                const obs = data.obstacles[i];
                const cube = obstacleMeshes[i];

                // 1. Skalowanie: Zmieniamy wymiary sześcianu (Wysokość stała: 1m, szerokość/głębokość z DBSCAN)
                cube.scale.set(obs.size_m, 1, obs.size_m);

                // 2. Pozycjonowanie: (W Three.js oś Y to góra/dół. Nasze X i Y z LiDARa to tu X i Z)
                cube.position.set(obs.center_x_m, 0.5, -obs.center_y_m);

                // 3. Kolorowanie (Reflectivity): Im wyższe odbicie, tym bardziej jaskrawy/ciepły kolor
                if (obs.avg_reflectivity > 200) {
                    cube.material.color.setHex(0xffaa00); // Jasne / Ostrzegawcze (np. pachołek, człowiek)
                    cube.material.opacity = 0.9;
                } else if (obs.avg_reflectivity > 100) {
                    cube.material.color.setHex(0xaaaaaa); // Średnie (np. ściana z płyt)
                    cube.material.opacity = 0.7;
                } else {
                    cube.material.color.setHex(0x444444); // Ciemne (np. ciemny karton)
                    cube.material.opacity = 0.5;
                }

                // Pokaż zaktualizowany sześcian
                cube.visible = true;
            }
        }
    };
}

// Wywołanie startowe - musi zostać!
init();