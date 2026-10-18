import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as THREE from 'three';

const SKIP_PATTERNS = [/camera/i, /light/i];

export class AGVLoader {
    constructor(scene) {
        this.scene = scene;
        this.loader = new GLTFLoader();
        this.agvModel = null;
    }

    loadModel(url) {
        return new Promise((resolve, reject) => {
            const statusEl = document.getElementById('status');
            if (statusEl) statusEl.textContent = 'Ładowanie modelu 3D AGV (Mecanum)...';

            this.loader.load(
                url,
                (gltf) => {
                    const model = gltf.scene;

                    // Ukryj zbędne węzły eksportu CAD (np. kamery)
                    model.traverse(node => {
                        if (SKIP_PATTERNS.some(p => p.test(node.name))) {
                            node.visible = false;
                        }
                    });

                    // Kontener główny (root)
                    const root = new THREE.Group();
                    root.name = 'AGV_ROOT';

                    // Obliczenie rzeczywistych wymiarów modelu
                    const box = new THREE.Box3().setFromObject(model);
                    const center = box.getCenter(new THREE.Vector3());
                    const size = box.getSize(new THREE.Vector3());
                    console.log('[IDUB Loader] Raw model size:', size, 'center:', center);

                    // Normalizacja skali: AGV powinien mieć długość ~2.2 metra
                    const maxDim = Math.max(size.x, size.z);
                    const targetSize = 2.2;
                    const scale = (maxDim > 0.001) ? (targetSize / maxDim) : 10.0;

                    model.scale.set(scale, scale, scale);

                    // Wyśrodkowanie w osiach X i Z oraz postawienie kół dokładnie na podłodze (Y = 0)
                    model.position.set(
                        -center.x * scale,
                        -box.min.y * scale,
                        -center.z * scale
                    );

                    root.add(model);
                    this.scene.add(root);
                    this.agvModel = root;

                    console.log(`[IDUB Loader] Model załadowany pomyślnie! Skala: ${scale.toFixed(2)}x`);
                    if (statusEl) statusEl.textContent = 'Model AGV załadowany';
                    resolve(root);
                },
                (xhr) => {
                    if (xhr.total > 0) {
                        const pct = (xhr.loaded / xhr.total * 100).toFixed(0);
                        if (statusEl && statusEl.textContent.includes('Ładowanie')) {
                            statusEl.textContent = `Ładowanie modelu 3D: ${pct}%`;
                        }
                    }
                },
                (error) => {
                    console.error('[IDUB Loader] Błąd ładowania modelu podstawowego:', error);
                    // Automatyczny fallback do agv.glb jeśli nowy model nie może się wczytać
                    if (url !== 'assets/models/agv.glb') {
                        console.warn('[IDUB Loader] Próba załadowania modelu zapasowego agv.glb...');
                        this.loadModel('assets/models/agv.glb').then(resolve).catch(reject);
                        return;
                    }
                    if (statusEl) statusEl.textContent = 'Błąd ładowania modelu 3D';
                    reject(error);
                }
            );
        });
    }
}