import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export class AGVLoader {
    constructor(scene) {
        this.scene = scene;
        this.loader = new GLTFLoader();
        this.agvModel = null;
    }

    loadModel(url) {
        return new Promise((resolve, reject) => {
            this.loader.load(
                url,
                (gltf) => {
                    this.agvModel = gltf.scene;
                    
                    // Opcjonalnie: skalowanie i pozycjonowanie, jeśli model jest źle wyeksportowany
                    // this.agvModel.scale.set(0.1, 0.1, 0.1); 
                    // this.agvModel.position.y = 0;

                    // Dodanie modelu do sceny
                    this.scene.add(this.agvModel);
                    console.log('Model AGV załadowany pomyślnie!');
                    resolve(this.agvModel);
                },
                (xhr) => {
                    // Postęp ładowania
                    console.log(`Ładowanie modelu: ${(xhr.loaded / xhr.total * 100).toFixed(2)}%`);
                },
                (error) => {
                    console.error('Błąd podczas ładowania modelu:', error);
                    reject(error);
                }
            );
        });
    }
}