import { GUI } from 'lil-gui';

export function setupGUI(ambientLight, directionalLight, floorMaterial, materialPodwozie) {
    const gui = new GUI({ title: '🎛️ Tuning Środowiska 3D' });

    const lightFolder = gui.addFolder('Oświetlenie');
    lightFolder.add(ambientLight, 'intensity', 0, 4, 0.1).name('Jasność tła (Ambient)');
    lightFolder.add(directionalLight, 'intensity', 0, 5, 0.1).name('Jasność słońca (Dir)');

    const posFolder = lightFolder.addFolder('Pozycja Słońca (Cienie)');
    posFolder.add(directionalLight.position, 'x', -30, 30, 1).name('Pozycja X');
    posFolder.add(directionalLight.position, 'y', 5, 50, 1).name('Wysokość Y');
    posFolder.add(directionalLight.position, 'z', -30, 30, 1).name('Pozycja Z');

    const floorFolder = gui.addFolder('Właściwości Podłogi');
    floorFolder.add(floorMaterial, 'roughness', 0, 1, 0.05).name('Szorstkość');
    floorFolder.add(floorMaterial, 'metalness', 0, 1, 0.05).name('Metaliczność');

    const agvFolder = gui.addFolder('Wygląd Wózka AGV');
    agvFolder.add(materialPodwozie, 'metalness', 0, 1, 0.05).name('Metaliczność Karoserii');
    agvFolder.add(materialPodwozie, 'roughness', 0, 1, 0.05).name('Matowość (Roughness)');

    const colorPickers = {
        floorColor: '#' + floorMaterial.color.getHexString(),
        chassisColor: '#' + materialPodwozie.color.getHexString(),
        lightColor: '#' + directionalLight.color.getHexString()
    };

    floorFolder.addColor(colorPickers, 'floorColor').name('Kolor Podłogi').onChange(value => floorMaterial.color.set(value));
    agvFolder.addColor(colorPickers, 'chassisColor').name('Kolor Podwozia').onChange(value => materialPodwozie.color.set(value));
    lightFolder.addColor(colorPickers, 'lightColor').name('Barwa Światła').onChange(value => directionalLight.color.set(value));

    gui.open();
}