import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as THREE from 'three';

const SKIP_PATTERNS = [/camera/i, /light/i];

export class AGVLoader {
    constructor(scene) {
        this.scene = scene;
        this.loader = new GLTFLoader();
    }

    /**
     * Wczytuje model glTF/GLB, automatycznie wyśrodkowuje w osiach X i Z,
     * stawia koła na podłodze Y=0 i normalizuje rozmiar do zadanego targetSize w metrach.
     */
    loadModel(url, targetSize = 2.2, initialPos = { x: 0, y: 0, z: 0 }, groupName = 'AGV_ROOT') {
        return new Promise((resolve, reject) => {
            this.loader.load(
                url,
                (gltf) => {
                    const model = gltf.scene;

                    // Ukryj zbędne węzły CAD (kamery, światła)
                    model.traverse(node => {
                        if (SKIP_PATTERNS.some(p => p.test(node.name))) {
                            node.visible = false;
                        }
                    });

                    const root = new THREE.Group();
                    root.name = groupName;

                    // Obliczenie rzeczywistych wymiarów modelu
                    const box = new THREE.Box3().setFromObject(model);
                    const center = box.getCenter(new THREE.Vector3());
                    const size = box.getSize(new THREE.Vector3());

                    const maxDim = Math.max(size.x, size.z);
                    const scale = (maxDim > 0.001) ? (targetSize / maxDim) : 10.0;

                    model.scale.set(scale, scale, scale);

                    // Wyśrodkowanie wewnątrz grupy root, spód na Y = 0
                    model.position.set(
                        -center.x * scale,
                        -box.min.y * scale,
                        -center.z * scale
                    );

                    root.add(model);
                    root.position.set(initialPos.x, initialPos.y, initialPos.z);
                    this.scene.add(root);

                    console.log(`[IDUB Loader] Załadowano ${groupName} (${url}): skala ${scale.toFixed(2)}x, rozmiar ${targetSize}m`);
                    resolve(root);
                },
                null,
                (error) => {
                    console.error(`[IDUB Loader] Błąd ładowania ${url}:`, error);
                    reject(error);
                }
            );
        });
    }
}