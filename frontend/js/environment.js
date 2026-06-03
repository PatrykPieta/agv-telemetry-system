import * as THREE from 'three';

export function setupEnvironment(scene) {
    scene.background = new THREE.Color(0x333333);
    scene.fog = new THREE.FogExp2(0x333333, 0.03);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
    directionalLight.position.set(10, 20, 15);
    directionalLight.castShadow = true;
    
    // Cienie
    directionalLight.shadow.mapSize.width = 1024;
    directionalLight.shadow.mapSize.height = 1024;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 40;
    directionalLight.shadow.camera.left = -10;
    directionalLight.shadow.camera.right = 10;
    directionalLight.shadow.camera.top = 10;
    directionalLight.shadow.camera.bottom = -10;
    scene.add(directionalLight);

    // Posadzka
    const floorGeometry = new THREE.PlaneGeometry(100, 100);
    const floorMaterial = new THREE.MeshStandardMaterial({
        color: 0x1a1a1a,
        roughness: 0.4,
        metalness: 0.3
    });
    const floorMesh = new THREE.Mesh(floorGeometry, floorMaterial);
    floorMesh.rotation.x = -Math.PI / 2;
    floorMesh.receiveShadow = true;
    scene.add(floorMesh);

    // Siatka pomocnicza
    const gridHelper = new THREE.GridHelper(100, 50, 0x444444, 0x252525);
    gridHelper.position.y = 0.01;
    scene.add(gridHelper);

    // Zwracamy stworzone materiały, aby GUI mogło do nich się podpiąć
    return { ambientLight, directionalLight, floorMaterial };
}