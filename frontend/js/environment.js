/**
 * IDUB Neuro-Curiosity Showcase — Environment
 *
 * Industrial warehouse scene: dark floor, grid, accent lights,
 * subtle fog to enhance depth. The AGV navigates this environment.
 */
import * as THREE from 'three';

export function setupEnvironment(scene) {
    // Deep space background
    scene.background = new THREE.Color(0x03080f);
    scene.fog = new THREE.FogExp2(0x03080f, 0.025);

    // Ambient — very low, industrial
    const ambientLight = new THREE.AmbientLight(0x1a2a3a, 0.6);
    scene.add(ambientLight);

    // Key light (overhead, cold white)
    const directionalLight = new THREE.DirectionalLight(0xc8e0ff, 1.8);
    directionalLight.position.set(8, 18, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width  = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near   = 0.5;
    directionalLight.shadow.camera.far    = 60;
    directionalLight.shadow.camera.left   = -15;
    directionalLight.shadow.camera.right  =  15;
    directionalLight.shadow.camera.top    =  15;
    directionalLight.shadow.camera.bottom = -15;
    directionalLight.shadow.bias = -0.001;
    scene.add(directionalLight);

    // Fill light (AGH blue accent)
    const fillLight = new THREE.DirectionalLight(0x004488, 0.6);
    fillLight.position.set(-10, 5, -8);
    scene.add(fillLight);

    // Rim light from behind (cool separation)
    const rimLight = new THREE.DirectionalLight(0x002244, 0.4);
    rimLight.position.set(0, 8, -15);
    scene.add(rimLight);

    // Industrial floor — dark concrete
    const floorGeo = new THREE.PlaneGeometry(60, 60);
    const floorMaterial = new THREE.MeshStandardMaterial({
        color: 0x0d1420,
        roughness: 0.85,
        metalness: 0.15,
    });
    const floor = new THREE.Mesh(floorGeo, floorMaterial);
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    scene.add(floor);

    // Fine grid — navigation reference
    const gridHelper = new THREE.GridHelper(60, 60, 0x0a1e30, 0x081220);
    gridHelper.position.y = 0.005;
    scene.add(gridHelper);

    // Coarse grid — zone boundaries
    const zoneGrid = new THREE.GridHelper(60, 6, 0x00294d, 0x001a33);
    zoneGrid.position.y = 0.006;
    scene.add(zoneGrid);

    // --- Warehouse structural elements (columns) for depth ---
    _addColumn(scene, -8,  8, 0x0a1a28);
    _addColumn(scene,  8,  8, 0x0a1a28);
    _addColumn(scene, -8, -8, 0x0a1a28);
    _addColumn(scene,  8, -8, 0x0a1a28);

    // --- Status indicator point lights (colour by zone) ---
    _addSpotMarker(scene, -8,  8, 0x0044aa); // NW
    _addSpotMarker(scene,  8,  8, 0x004400); // NE
    _addSpotMarker(scene, -8, -8, 0x002244); // SW
    _addSpotMarker(scene,  8, -8, 0x002244); // SE

    return { ambientLight, directionalLight, floorMaterial };
}

function _addColumn(scene, x, z, color) {
    const geo = new THREE.BoxGeometry(0.2, 4, 0.2);
    const mat = new THREE.MeshStandardMaterial({ color, metalness: 0.6, roughness: 0.4 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(x, 2, z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    scene.add(mesh);

    // Top LED strip suggestion
    const stripGeo = new THREE.BoxGeometry(0.22, 0.05, 0.22);
    const stripMat = new THREE.MeshStandardMaterial({
        color: 0x005fa3,
        emissive: new THREE.Color(0x002244),
        emissiveIntensity: 1,
    });
    const strip = new THREE.Mesh(stripGeo, stripMat);
    strip.position.set(x, 4.02, z);
    scene.add(strip);
}

function _addSpotMarker(scene, x, z, color) {
    const light = new THREE.PointLight(color, 0.8, 6);
    light.position.set(x, 3.8, z);
    scene.add(light);
}