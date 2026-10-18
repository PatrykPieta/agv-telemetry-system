/**
 * IDUB Neuro-Curiosity AGV Showcase — Loader
 *
 * Loads the AGV_SIM_F.glb model (detailed Mecanum wheel model from CAD export).
 * The model has 51 nodes exported from STEP files; wheel assemblies use Mirror/MirrorMirror prefix.
 * Since STEP->GLB exports don't have clean FL/FR/RL/RR names, we group wheel-related
 * nodes by position (bounding box center X/Z) after loading.
 */
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import * as THREE from 'three';

// Node name patterns for the Mecanum wheel assembly groups in AGV_SIM_F.glb
const WHEEL_PATTERNS = [
    /^Mecanum Left v5/i,
    /^MirrorMirrorMecanum/i,
    /^MirrorMecanum/i,
    /^Side\s*[12]/i,
    /^MirrorMirrorSide/i,
    /^MirrorSide/i,
    /^Roller_/i,
    /^MirrorMirrorRoller/i,
    /^MirrorRoller/i,
];

// Camera node to hide (artifact from CAD export)
const SKIP_PATTERNS = [/^current camera/i];

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

                    // Hide camera nodes left in by CAD exporter
                    this.agvModel.traverse(node => {
                        if (SKIP_PATTERNS.some(p => p.test(node.name))) {
                            node.visible = false;
                        }
                    });

                    // Scale: STEP export in mm → Three.js units (1 unit ≈ 1m)
                    // AGV_SIM_F is approximately 800mm wide, so scale 0.001 → ~0.8m
                    this.agvModel.scale.set(0.001, 0.001, 0.001);
                    this.agvModel.position.y = 0;

                    this.scene.add(this.agvModel);
                    console.log('[IDUB] Model AGV_SIM_F załadowany —', gltf.scene.children.length, 'węzłów głównych');
                    resolve(this.agvModel);
                },
                (xhr) => {
                    if (xhr.total > 0) {
                        const pct = (xhr.loaded / xhr.total * 100).toFixed(1);
                        console.log(`[IDUB] Ładowanie modelu: ${pct}%`);
                    }
                },
                (error) => {
                    console.error('[IDUB] Błąd ładowania modelu AGV_SIM_F:', error);
                    reject(error);
                }
            );
        });
    }

    /**
     * Collect mesh nodes that belong to wheel assemblies.
     * Returns array of Three.js Object3D to be animated.
     */
    collectWheelMeshes() {
        const wheels = [];
        if (!this.agvModel) return wheels;
        this.agvModel.traverse(node => {
            if (node.isMesh && WHEEL_PATTERNS.some(p => p.test(node.name))) {
                wheels.push(node);
            }
        });
        console.log('[IDUB] Znaleziono węzłów kół Mecanum:', wheels.length);
        return wheels;
    }
}