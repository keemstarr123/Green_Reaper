// --- Import section ---
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

// --- Setup constants ---
const width = 1200;
const height = 700;
const scale = 1;

// --- Scene, Camera, Renderer ---
const scene = new THREE.Scene();
scene.background = new THREE.Color('#ade7ff');
scene.fog = new THREE.Fog('#ade7ff', 50, 150);

const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
camera.position.set(15, 10, 25);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.shadowMap.enabled = true;
renderer.setSize(width, height);
document.getElementById('threejs-container').appendChild(renderer.domElement);

const labelRenderer = new CSS2DRenderer();
labelRenderer.setSize(width, height);
labelRenderer.domElement.style.position = 'absolute';
labelRenderer.domElement.style.top = '0px';
labelRenderer.domElement.style.pointerEvents = 'none';
document.getElementById('threejs-container').appendChild(labelRenderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.enableZoom = true;
controls.enablePan = true;
controls.screenSpacePanning = true;
controls.maxPolarAngle = Math.PI / 2.1;
controls.target.set(0, 2, 0);

// --- Lighting ---
scene.add(new THREE.AmbientLight(0xffffff, 0.6));

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(-20, 30, 30);
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.set(2048, 2048);
scene.add(directionalLight);

// --- Groups ---
const houseGroup = new THREE.Group();
const sustainabilityGroup = new THREE.Group();
scene.add(houseGroup);
scene.add(sustainabilityGroup);

// --- Functions ---
function generateHouseStructure(houseData = []) {
  houseGroup.clear();
  houseData.forEach(component => {
    const { geometry, material, position, rotation } = component;
    const geom = new THREE[geometry.type](...geometry.args.map(x => x * scale));
    const mat = new THREE.MeshStandardMaterial({ color: new THREE.Color(material.color) });
    const mesh = new THREE.Mesh(geom, mat);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.position.set(...position.map(p => p * scale));
    if (rotation) mesh.rotation.set(...rotation);
    houseGroup.add(mesh);
  });
}

function addSustainabilityFeatures(features = []) {
  sustainabilityGroup.clear();
  features.forEach(feature => {
    const { type, geometry, material, position, rotation } = feature;
    const geom = geometry
      ? new THREE[geometry.type](...geometry.args.map(x => x * scale))
      : new THREE.BoxGeometry(0.2 * scale, 0.2 * scale, 0.2 * scale);

    const mat = new THREE.MeshStandardMaterial({ color: new THREE.Color(material.color) });
    const mesh = new THREE.Mesh(geom, mat);

    mesh.position.set(...position.map(p => p * scale));
    if (rotation) mesh.rotation.set(...rotation);
    mesh.castShadow = true;
    mesh.receiveShadow = true;

    // Create label
    const labelDiv = document.createElement('div');
    labelDiv.className = 'label';
    labelDiv.textContent = type;
    labelDiv.style.background = 'rgba(255,255,255,0.8)';
    labelDiv.style.padding = '2px 6px';
    labelDiv.style.borderRadius = '4px';
    labelDiv.style.fontSize = '0.75em';

    const label = new CSS2DObject(labelDiv);
    label.position.set(0, 0.5 * scale, 0);
    mesh.add(label);

    sustainabilityGroup.add(mesh);
  });
}

function centerCameraOnScene() {
  const box = new THREE.Box3().setFromObject(scene);
  const size = box.getSize(new THREE.Vector3()).length();
  const center = box.getCenter(new THREE.Vector3());
  camera.position.copy(center.clone().add(new THREE.Vector3(size * 0.1, size * 0.05, size * 0.1)));
  controls.target.copy(center);
  camera.lookAt(center);
}

// --- Animate Loop ---
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
}

var data = {"houseData":[{"geometry":{"type":"BoxGeometry","args":[10,4,8]},"material":{"color":"#8B4513"},"position":[0,2,0]},{"geometry":{"type":"BoxGeometry","args":[10,0.2,5.385]},"material":{"color":"#555555"},"position":[0,5,2],"rotation":[0.38,0,0]},{"geometry":{"type":"BoxGeometry","args":[10,0.2,5.385]},"material":{"color":"#555555"},"position":[0,5,-2],"rotation":[-0.38,0,0]},{"geometry":{"type":"BoxGeometry","args":[1.5,1.5,0.1]},"material":{"color":"#ADD8E6"},"position":[-2.5,2,4.05]},{"geometry":{"type":"BoxGeometry","args":[1.5,1.5,0.1]},"material":{"color":"#ADD8E6"},"position":[2.5,2,4.05]},{"geometry":{"type":"BoxGeometry","args":[1,2,0.1]},"material":{"color":"#654321"},"position":[0,1,4.05]},{"geometry":{"type":"BoxGeometry","args":[10,0.2,2]},"material":{"color":"#D3D3D3"},"position":[0,0.4,5]},{"geometry":{"type":"BoxGeometry","args":[10.4,0.2,2.4]},"material":{"color":"#555555"},"position":[0,3,5]},{"geometry":{"type":"BoxGeometry","args":[0.3,2.6,0.3]},"material":{"color":"#FFFFFF"},"position":[-4.5,1.7,5.85]},{"geometry":{"type":"BoxGeometry","args":[0.3,2.6,0.3]},"material":{"color":"#FFFFFF"},"position":[-1.5,1.7,5.85]},{"geometry":{"type":"BoxGeometry","args":[0.3,2.6,0.3]},"material":{"color":"#FFFFFF"},"position":[1.5,1.7,5.85]},{"geometry":{"type":"BoxGeometry","args":[0.3,2.6,0.3]},"material":{"color":"#FFFFFF"},"position":[4.5,1.7,5.85]},{"geometry":{"type":"BoxGeometry","args":[9.3,0.8,0.1]},"material":{"color":"#FFFFFF"},"position":[0,0.8,5.95]},{"geometry":{"type":"BoxGeometry","args":[2,0.133,0.3]},"material":{"color":"#D3D3D3"},"position":[0,0.3335,6.15]},{"geometry":{"type":"BoxGeometry","args":[2,0.133,0.3]},"material":{"color":"#D3D3D3"},"position":[0,0.2005,6.45]},{"geometry":{"type":"BoxGeometry","args":[2,0.133,0.3]},"material":{"color":"#D3D3D3"},"position":[0,0.0675,6.75]}],"sustainabilityFeatures":[{"type":"solarPanel","position":[-2.5,5.3,2.5],"material":{"color":"#00008B"},"geometry":{"type":"BoxGeometry","args":[2,0.05,3]},"rotation":[0.38,0,0]},{"type":"solarPanel","position":[2.5,5.3,2.5],"material":{"color":"#00008B"},"geometry":{"type":"BoxGeometry","args":[2,0.05,3]},"rotation":[0.38,0,0]},{"type":"greenRoof","position":[0,3.15,5],"material":{"color":"#2E8B57"},"geometry":{"type":"BoxGeometry","args":[10,0.1,2]}},{"type":"rainwaterHarvestingSystem","position":[-5.5,0.75,2],"material":{"color":"#808080"},"geometry":{"type":"CylinderGeometry","args":[0.5,1.5,32]}},{"type":"permeablePaving","position":[-3,0.025,7],"material":{"color":"#DCDCDC"},"geometry":{"type":"BoxGeometry","args":[4,0.05,6]}},{"type":"nativeLandscaping","position":[3,0.25,6],"material":{"color":"#006400"},"geometry":{"type":"BoxGeometry","args":[0.5,0.5,0.5]}},{"type":"nativeLandscaping","position":[-3,0.2,6],"material":{"color":"#006400"},"geometry":{"type":"BoxGeometry","args":[0.6,0.4,0.6]}},{"type":"nativeLandscaping","position":[5.5,0.3,2],"material":{"color":"#006400"},"geometry":{"type":"BoxGeometry","args":[0.4,0.6,0.4]}}]};

function addGrassGround() {
  const geometry = new THREE.PlaneGeometry(200, 200);
  const material = new THREE.MeshStandardMaterial({ color: '#228B22' }); // dark green
  const ground = new THREE.Mesh(geometry, material);
  ground.rotation.x = -Math.PI / 2; // Rotate to be horizontal
  ground.position.y = 0; // Align with Y=0
  ground.receiveShadow = true;
  scene.add(ground);
}

function addSimpleTrees() {
  const treePositions = [
    [-20, 0, -20],
    [20, 0, -20],
    [-20, 0, 20],
    [20, 0, 20],
    [0, 0, 25]
  ];

  treePositions.forEach(pos => {
    // Tree trunk
    const trunkGeometry = new THREE.CylinderGeometry(0.5, 0.5, 4, 12);
    const trunkMaterial = new THREE.MeshStandardMaterial({ color: '#8B4513' });
    const trunk = new THREE.Mesh(trunkGeometry, trunkMaterial);
    trunk.position.set(pos[0], 2, pos[2]);
    trunk.castShadow = true;

    // Tree leaves (sphere)
    const leavesGeometry = new THREE.SphereGeometry(2.5, 16, 16);
    const leavesMaterial = new THREE.MeshStandardMaterial({ color: '#228B22' });
    const leaves = new THREE.Mesh(leavesGeometry, leavesMaterial);
    leaves.position.set(pos[0], 6, pos[2]);
    leaves.castShadow = true;

    scene.add(trunk);
    scene.add(leaves);
  });
}


// --- Start Three.js ---
function startThreejs() {
  document.getElementById('threed_scripts').classList.remove('hidden');
  generateHouseStructure(data.houseData);
  addSustainabilityFeatures(data.sustainabilityFeatures);
  addGrassGround(); // 🌿 Add this
  addSimpleTrees(); // 🌳 Add this
  centerCameraOnScene();
  animate();
}

// --- Call this function when you want to show the 3D model ---
startThreejs();
