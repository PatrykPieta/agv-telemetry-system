/**
 * IDUB Neuro-Curiosity Showcase — Environment
 *
 * Industrial warehouse testing arena (100x100m) with navigation grids,
 * amber safety perimeter boundary, structural pillars, and balanced lighting.
 */
import * as THREE from 'three';

export function setupEnvironment(scene) {
    scene.background = new THREE.Color(0x060c16);
    scene.fog = new THREE.FogExp2(0x060c16, 0.015);

    // Oświetlenie otoczenia (Ambient) — neutralna biel, wyraźny wgląd w oba modele
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    // Główne światło kierunkowe (Słońce hali)
    const directionalLight = new THREE.DirectionalLight(0xe8f2ff, 1.6);
    directionalLight.position.set(15, 25, 20);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width  = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near   = 0.5;
    directionalLight.shadow.camera.far    = 90;
    directionalLight.shadow.camera.left   = -35;
    directionalLight.shadow.camera.right  =  35;
    directionalLight.shadow.camera.top    =  35;
    directionalLight.shadow.camera.bottom = -35;
    directionalLight.shadow.bias = -0.001;
    scene.add(directionalLight);

    // Światło wypełniające (AGH Blue)
    const fillLight = new THREE.DirectionalLight(0x0055aa, 0.5);
    fillLight.position.set(-20, 10, -15);
    scene.add(fillLight);

    // Posadzka hali przemysłowej (100x100m)
    const floorGeo = new THREE.PlaneGeometry(100, 100);
    const floorMaterial = new THREE.MeshStandardMaterial({
        color: 0x0f1824,
        roughness: 0.8,
        metalness: 0.2,
    });
    const floor = new THREE.Mesh(floorGeo, floorMaterial);
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    scene.add(floor);

    // Siatka nawigacyjna (kratki 1m)
    const gridFine = new THREE.GridHelper(100, 100, 0x162c42, 0x0c1b2b);
    gridFine.position.y = 0.005;
    scene.add(gridFine);

    // Siatka głównych stref (kratki 10m)
    const gridCoarse = new THREE.GridHelper(100, 10, 0x007acc, 0x002244);
    gridCoarse.position.y = 0.006;
    scene.add(gridCoarse);

    // --- Wizualny perymetr bezpieczeństwa (Promień 21m) ---
    // Żółto-bursztynowy świetlny pierścień strefy testowej
    const boundaryGeo = new THREE.RingGeometry(20.9, 21.3, 128);
    const boundaryMat = new THREE.MeshBasicMaterial({
        color: 0xffaa00,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.7,
    });
    const boundaryRing = new THREE.Mesh(boundaryGeo, boundaryMat);
    boundaryRing.rotation.x = -Math.PI / 2;
    boundaryRing.position.y = 0.008;
    scene.add(boundaryRing);

    // Filary konstrukcyjne hali (z LEDami strefowymi)
    _addColumn(scene, -22,  22, 0x0066cc);
    _addColumn(scene,  22,  22, 0x00cc66);
    _addColumn(scene, -22, -22, 0xff8800);
    _addColumn(scene,  22, -22, 0xcc0066);

    return { ambientLight, directionalLight, floorMaterial };
}

function _addColumn(scene, x, z, color) {
    const geo = new THREE.BoxGeometry(0.5, 6, 0.5);
    const mat = new THREE.MeshStandardMaterial({ color: 0x1a2636, metalness: 0.7, roughness: 0.3 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(x, 3, z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    scene.add(mesh);

    // Dioda LED na szczycie filaru
    const led = new THREE.PointLight(color, 1.2, 10);
    led.position.set(x, 5.8, z);
    scene.add(led);
}