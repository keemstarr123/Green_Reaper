from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional
import time
import PyPDF2
from fastapi import FastAPI,  File, UploadFile
import httpx
import math
import json
from google.oauth2 import service_account
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi import Form
from fastapi.templating import Jinja2Templates
from google import genai
from google.genai import types
from google.auth import load_credentials_from_file
from google.auth.credentials import Credentials
import base64
from googleapiclient.discovery import build
import asyncio
import re
import io
import time
from datetime import datetime, date
from fastapi.responses import JSONResponse
import os; os.environ['GEMINI_API_KEY1'] = ''
import os; os.environ['GEMINI_API_KEY2'] = ''
import ee
import math
import json
from google.oauth2 import service_account
from pathlib import Path
from fastapi.staticfiles import StaticFiles


timeout_config = httpx.Timeout(
    connect=10.0,
    read=60.0,
    write=30.0,
    pool=5.0
)

TWO_TO_THREE_PROMPT = """
Role: “Gemini-2D-to-3D-Renderer” – a depth-aware engine that transforms flat PNG images into 3D-effect PNGs with accurate depth cues and shading.
Convert the supplied 2D PNG into a 3D-styled PNG
"""

JS_TEMPLATE = '''
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

function addSustainabilityFeatures(features = [], container) {
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
  camera.position.copy(center.clone().add(new THREE.Vector3(size * 0.2, size * 0.1, size * 0.2)));
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

var data = replace here;

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
  addSustainabilityFeatures(data.sustainabilityFeatures, document.getElementById('threejs_container'));
  addGrassGround(); // 🌿 Add this
  addSimpleTrees(); // 🌳 Add this
  centerCameraOnScene();
  animate();
}

// --- Call this function when you want to show the 3D model ---
startThreejs();
'''

def THREEJS_PROMPT(context_refined, sustainability_features): 
  return f'''
  You are a 3D architectural modeling assistant. I am creating a modular 3D model of a classic craftsman-style bungalow using Three.js. Your task is to generate a JSON structure that I can use directly in my scene.

  Context:
  {context_refined}

  Output only a JSON object in this format:
  {{
  "houseData": [...],
  "sustainabilityFeatures": [...]
  }}

  ---

  ## HOUSE STRUCTURE

  "houseData" must be an array of modular components. Each object must contain:

  - "geometry": {{
    "type": (e.g., "BoxGeometry", "CylinderGeometry"),
    "args": [width, height, depth] in meters
  }}
  - "material": {{
    "color": string — hex code for realistic architecture colors
  }}
  - "position": [x, y, z] in meters — aligned to form a realistic, stackable house
  - Optional: "rotation": [x, y, z] in radians, if needed for roof slope

  ### Architectural Requirements:
  - 10m wide × 4m tall × 8m deep base
  - Gabled roof with two visible slopes
  - Dormer centered on front roof slope with its own mini roof and two vertical windows
  - 2 window sets on the front facade (left and right of door)
  - Covered front porch:
  - Floor slab and roof
  - Railings across front edge
  - 4 equally spaced columns
  - Steps leading to ground

  Use **BoxGeometry** for walls, dormer, roof, and porch parts. Use **real-world alignment** to avoid floating parts. Materials:
  - Walls: dark grey (#4A4A4A) or brown (#8B4513)
  - Trim, columns, and railing: white (#FFFFFF)
  - Roof: brown (#A0522D) or dark grey (#555555)

  ---

  ## SUSTAINABILITY FEATURES

  "sustainabilityFeatures" must include green building elements, accurately placed and visually integrated with the home. These must include:
  {sustainability_features}

  Each object must include:
  - "type": string name (e.g., "solarPanels", "nativeLandscaping")
  - "position": [x, y, z] in meters
  - "material": {{
    "color": string — hex code for realistic environmental colors
  }}
  - Optional: "geometry": {{
    "type": string (e.g., "BoxGeometry", "CylinderGeometry"),
    "args": array of [w, h, d] in meters
  }}
  - Optional: "rotation": [x, y, z] in radians (e.g., sloped panel)

  ### Placement Rules:
  - Solar panels should sit on angled roof surfaces
  - Green roof sits on flat roofs (e.g., porch or dormer)
  - Native plants and compost bin on ground only
  - All features should be logically placed with no overlapping or floating
  - Proportions should match real-world scale (e.g., compost bin < 1m³)

  ---

Important:
- Output raw JSON directly without triple backticks (```), without markdown formatting.
- Do not insert newlines (`\\n`) or line breaks inside JSON values.
- Do not escape double quotes (`"`), except where normally required by JSON.
- Output fully minified JSON.
- Return valid parsable JSON object.
- Return the json in one line will do
  '''

class RiskItem(BaseModel):
    risk: str
    likelihood: str
    impact: str
    elaboration: str

class ActionItem(BaseModel):
    title: str
    elaboration: str

class InsulationRValues(BaseModel):
    walls: str
    roof: str

class SustainabilityRisk(BaseModel):
    risk: str
    likelihood: str
    impact: str
    elaboration: str

class SustainabilitySuggestion(BaseModel):
    feature: str 
    description: str

class SustainabilityAssessment(BaseModel):
    greenCertificationTarget: str
    certificationLevel: str
    netZeroReady: str
    solarPVCapacity_kW: str
    solarCoverage_pct: str
    batteryStorage_kWh: str
    evChargingReady: str
    rainwaterHarvestingCapacity_liters: str
    waterSavings_pct: str
    insulationRValues: InsulationRValues
    energyEfficiencyMeasures: List[str]
    annualEnergySavings_RM: str
    annualWaterSavings_RM: str
    operationalOPEXReduction_pct: str
    bepsCompliance: str
    greenGrantSubsidyApplied: str
    embodiedCarbonAssessment: str
    sustainabilityScore: str
    sustainabilityRisks: List[SustainabilityRisk]
    recommendations: List[SustainabilitySuggestion]
    finalSustainabilityVerdict: str

class CostDetail(BaseModel):
    amount: str
    pctOfTDC: str

class CostBreakdown(BaseModel):
    landAcquisitionLease: CostDetail
    hardCosts: CostDetail
    softCosts: CostDetail
    financingInterest: CostDetail
    contingency: CostDetail
    benchmark: str

class CapitalStackItem(BaseModel):
    source: str
    type: str
    amount: str
    pctOfTDC: str

class PaybackPeriod(BaseModel):
    years: str
    months: str

class FinancialMetrics(BaseModel):
    ROI_pct: str
    IRR_pct: str
    NPV: str
    discountRate_pct: str
    paybackPeriod: PaybackPeriod
    DSCR: str
    costPerUnit: str

class FiveYearProjectionItem(BaseModel):
    year: str
    opex: str
    energySavings: str
    waterSavings: str
    netCF: str
    cumulativeCF: str

class SensitivityItem(BaseModel):
    variable: str
    base: str
    minus10: str
    plus10: str
    impactOnIRR_NPV: str

class FinancialSnapshot(BaseModel):
    projectName: str
    location: str
    scope: str
    totalDevelopmentCost: str
    tenderBudget: str
    overallFinancialFeasibility: str
    costBreakdown: CostBreakdown
    financingCapitalStack: List[CapitalStackItem]
    keyFinancialMetrics: FinancialMetrics
    fiveYearProjection: List[FiveYearProjectionItem]
    sensitivityAnalysis: List[SensitivityItem]
    recommendations: List[str]
    finalVerdict: str

class CertificationAlignment(BaseModel):
    certification: str
    status: int

class CompositeRatings(BaseModel):
    sustainability: float
    finance: float
    efficiency: float

class ScoreTableItem(BaseModel):
    criterion: str
    max: float
    awarded: float
    evidence: str

class OverallFinalScore(BaseModel):
    overallScore_pct: float

class TenderValidationOutput(BaseModel):
    gaps: List[ActionItem]
    mandatoryActions: List[ActionItem]
    mediocreActions: List[ActionItem]
    complianceRiskMatrix: List[RiskItem]
    goodToHaveUpgrades: List[ActionItem]
    sustainabilityAssessment: SustainabilityAssessment
    carbonFootprintReduction_tCO2_perYear: float
    financialSnapshot: FinancialSnapshot
    certificationAlignment: List[CertificationAlignment]
    certificationSteps: List[str]
    compositeRatings: CompositeRatings
    detailedScoreTable: List[ScoreTableItem]
    overallFinalScore: OverallFinalScore
    winningRate_pct: float

class Address(BaseModel):
    address: str

class DateTimeField(BaseModel):
    dateTime: str
    timeZone: str

class GoogleCalendarEvent(BaseModel):
    summary: str
    location: str
    description: str 
    start: DateTimeField
    end: DateTimeField

class GoogleEventList(BaseModel):
    event_list: list[GoogleCalendarEvent]

SERVICE_ACCOUNT_FILE = 'KitahackServiceAccount.json'

# Path to your service account credentials
SERVICE_ACCOUNT_FILE2 = 'GCC_account.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Authenticate the service account
credentials3 = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE2, scopes=SCOPES
)

# Build the Calendar API client
service = build('calendar', 'v3', credentials=credentials3)

# Load credentials using google-auth
credential = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/earthengine']
)

ee.Initialize(credential)
print("✅ Earth Engine initialized successfully!")

cred = credentials.Certificate("green-reaper.json")
app = firebase_admin.initialize_app(cred)
print("✅ Firebase initialized successfully!")
db = firestore.client()
templates = Jinja2Templates(directory=str("html"))

apps = FastAPI()
apps.mount("/assets", StaticFiles(directory="."), name="assets")
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "html"))  # ✅ now added

async def generate(context, pattern = None, image_bytes = None):

  credentials, project_id = load_credentials_from_file(
        r"green-reaper.json", 
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
  )

  client = genai.Client(
      credentials=credentials,
      vertexai=True,
      project="green-reaper",
      location="us-central1",
  )
  

  model = "gemini-2.5-pro-exp-03-25"
  part = [
      types.Part(text=context),
      ]
  if image_bytes != None:
    part.append(types.Part(
          inline_data=types.Blob(
              mime_type="image/png",
              data=image_bytes
          )
      ))
  scheme =  {"type":"OBJECT","properties":{"houseData":{"type":"ARRAY","items":{"type":"OBJECT","properties":{"geometry":{"type":"OBJECT","properties":{"type":{"type":"STRING"},"args":{"type":"ARRAY","items":{"type":"NUMBER"}}},"required":["type","args"]},"material":{"type":"OBJECT","properties":{"color":{"type":"STRING"}},"required":["color"]},"position":{"type":"ARRAY","items":{"type":"NUMBER"}},"rotation":{"type":"ARRAY","items":{"type":"NUMBER"}}},"required":["geometry","material","position"]}},"sustainabilityFeatures":{"type":"ARRAY","items":{"type":"OBJECT","properties":{"type":{"type":"STRING"},"geometry":{"type":"OBJECT","properties":{"type":{"type":"STRING"},"args":{"type":"ARRAY","items":{"type":"NUMBER"}}}},"material":{"type":"OBJECT","properties":{"color":{"type":"STRING"}}},"position":{"type":"ARRAY","items":{"type":"NUMBER"}},"rotation":{"type":"ARRAY","items":{"type":"NUMBER"}}},"required":["type","position","material"]}}},"required":["houseData","sustainabilityFeatures"]}
  model = "gemini-2.5-pro-exp-03-25"
  contents = [
    types.Content(
      role="user",
      parts=part
    )
  ]

  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 20000,
    response_modalities = ["TEXT"],
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
    response_mime_type = "application/json",
    response_schema = scheme,
  )
  generation_result = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
  print(generation_result.text,type(generation_result))
  cleaned_text = re.sub(pattern[1], "", generation_result.text)


  # Step 4: Replace "replace here" in your JS_TEMPLATE
  script = re.sub(pattern[0], cleaned_text, JS_TEMPLATE)
  with open("secondthree.js", "w", encoding="utf-8") as file:
        file.write(script)
    
  return script

def fetch_lst(lat, lon):
    """Fetches Land Surface Temperature (LST) for a given point."""
    try:
        dataset = ee.ImageCollection("MODIS/061/MOD11A1") \
            .filterDate('2024-02-01', '2025-02-28') \
            .select("LST_Day_1km") \
            .mean() \
            .multiply(0.02) \
            .subtract(273.15)

        point = ee.Geometry.Point([float(lon), float(lat)])

        sampled_data = dataset.sample(
            region=point,
            scale=1000,
            numPixels=1
        ).getInfo()

        if not sampled_data or not sampled_data.get('features') or len(sampled_data['features']) == 0:
            print(f"fetch_lst returned no data for lat={lat}, lon={lon}")
            return None

        lst = sampled_data['features'][0]['properties'].get('LST_Day_1km')
        print(f"fetch_lst success for lat={lat}, lon={lon}, value: {lst}")
        return lst
    except ee.EEException as e:
        print(f"fetch_lst Earth Engine error for lat={lat}, lon={lon}: {e}")
        return None
    except Exception as e:
        print(f"fetch_lst Python error for lat={lat}, lon={lon}: {e}")
        return None

def fetch_ndvi(lat, lon):
    """Fetches Normalized Difference Vegetation Index (NDVI) for a given point."""
    try:
        point = ee.Geometry.Point([float(lon), float(lat)])

        dataset = ee.ImageCollection("COPERNICUS/S2") \
            .filterBounds(point) \
            .filterDate('2024-02-01', '2025-02-28') \
            .sort("system:time_start") \
            .first()

        if dataset is None:
            print(f"fetch_ndvi: No Sentinel-2 imagery found for lat={lat}, lon={lon} in the specified date range.")
            return None

        ndvi = dataset.normalizedDifference(['B8', 'B4'])

        sampled_data = ndvi.sample(
            region=point,
            scale=10,
            numPixels=1
        ).getInfo()

        if not sampled_data or not sampled_data.get('features') or len(sampled_data['features']) == 0:
            print(f"fetch_ndvi returned no data for lat={lat}, lon={lon}")
            return None

        ndvi_value = sampled_data['features'][0]['properties'].get('nd')
        print(f"fetch_ndvi success for lat={lat}, lon={lon}, value: {ndvi_value}")
        return ndvi_value
    except ee.EEException as e:
        print(f"fetch_ndvi Earth Engine error for lat={lat}, lon={lon}: {e}")
        return None
    except Exception as e:
        print(f"fetch_ndvi Python error for lat={lat}, lon={lon}: {e}")
        return None

def fetch_rainfall(lat, lon):
    """Fetches average daily rainfall for February 2024 for a given point."""
    try:
        point = ee.Geometry.Point([float(lon), float(lat)])

        dataset = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
            .filterBounds(point) \
            .filterDate('2024-02-01', '2024-02-28') \
            .select("precipitation") \
            .mean()

        reduced_region = dataset.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=1000,
            maxPixels=1e9
        ).getInfo()

        if reduced_region and 'precipitation' in reduced_region:
            rainfall = reduced_region['precipitation']
            print(f"fetch_rainfall success for lat={lat}, lon={lon}, value: {rainfall}")
            return rainfall
        else:
            print(f"fetch_rainfall: No rainfall data available for lat={lat}, lon={lon}")
            return None
    except ee.EEException as e:
        print(f"fetch_rainfall Earth Engine error for lat={lat}, lon={lon}: {e}")
        return None
    except Exception as e:
        print(f"fetch_rainfall Python error for lat={lat}, lon={lon}: {e}")
        return None

def fetch_flood_history(lat, lon):
    """Fetches maximum flood depth history for a given point."""
    try:
        point = ee.Geometry.Point([float(lon), float(lat)])

        flood_hazard = ee.ImageCollection("JRC/CEMS_GLOFAS/FloodHazard/v1") \
            .select("depth") \
            .max()

        reduced_region = flood_hazard.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=1000,
            maxPixels=1e9
        ).getInfo()

        if reduced_region and 'depth' in reduced_region:
            flood_depth = reduced_region['depth']
            print(f"fetch_flood_history success for lat={lat}, lon={lon}, value: {flood_depth}")
            return flood_depth
        else:
            print(f"fetch_flood_history: No flood hazard data available for lat={lat}, lon={lon}")
            return None
    except ee.EEException as e:
        print(f"fetch_flood_history Earth Engine error for lat={lat}, lon={lon}: {e}")
        return None
    except Exception as e:
        print(f"fetch_flood_history Python error for lat={lat}, lon={lon}: {e}")
        return None

def fetch_wind_data_and_solar(lat, lon):
    """Fetches mean wind speed, direction, and solar radiation for a given point."""
    try:
        point = ee.Geometry.Point([float(lon), float(lat)])

        dataset = ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY') \
            .filterBounds(point) \
            .filter(ee.Filter.date('2024-02-01', '2025-02-28')) \
            .select(["u_component_of_wind_10m", "v_component_of_wind_10m", 'surface_net_solar_radiation']).mean()

        reduced_region = dataset.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=9000,
            maxPixels=1e9
        ).getInfo()

        if reduced_region:
            u_wind = reduced_region.get('u_component_of_wind_10m', 0)
            v_wind = reduced_region.get('v_component_of_wind_10m', 0)
            solar_value = reduced_region.get('surface_net_solar_radiation', 0)
            wind_speed = (u_wind**2 + v_wind**2)**0.5
            wind_direction = (math.atan2(-u_wind, -v_wind) * 180 / math.pi + 360) % 360 if (u_wind != 0 or v_wind != 0) else 0

            print(f"fetch_wind_data_and_solar success for lat={lat}, lon={lon}, value: {wind_speed:.2f} {wind_direction:.2f} {solar_value:.2f}")
            return f"{wind_speed:.2f} {wind_direction:.2f} {solar_value:.2f}"
        else:
            print(f"fetch_wind_data_and_solar: No data available for lat={lat}, lon={lon}")
            return None
    except ee.EEException as e:
        print(f"fetch_wind_data_and_solar Earth Engine error for lat={lat}, lon={lon}: {e}")
        return None
    except Exception as e:
        print(f"fetch_wind_data_and_solar Python error for lat={lat}, lon={lon}: {e}")
        return None

def fetch_elevation_difference(lat, lon):
    """Fetches elevation at a point and the average elevation of the surrounding area."""
    try:
        point = ee.Geometry.Point([float(lon), float(lat)])
        elevation = ee.Image('USGS/SRTMGL1_003').select('elevation')

        elevation_at_point_region = elevation.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=30,
            maxPixels=1e9
        ).getInfo()

        if not elevation_at_point_region or 'elevation' not in elevation_at_point_region:
            print(f"fetch_elevation_difference: Failed to fetch elevation at point for lat={lat}, lon={lon}")
            return None

        elevation_at_point = elevation_at_point_region['elevation']

        surrounding_elevation_region = elevation.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point.buffer(1000),
            scale=30,
            maxPixels=1e9
        ).getInfo()

        if not surrounding_elevation_region or 'elevation' not in surrounding_elevation_region:
            print(f"fetch_elevation_difference: Failed to fetch surrounding elevation for lat={lat}, lon={lon}")
            return f"{elevation_at_point:.2f} None"

        avg_surrounding_elevation = surrounding_elevation_region['elevation']
        elevation_diff = elevation_at_point - avg_surrounding_elevation

        print(f"fetch_elevation_difference success for lat={lat}, lon={lon}, value: {elevation_at_point:.2f} {elevation_diff:.2f}")
        return f"{elevation_at_point:.2f} {elevation_diff:.2f}m"
    except ee.EEException as e:
        print(f"fetch_elevation_difference Earth Engine error for lat={lat}, lon={lon}: {e}")
        return None
    except Exception as e:
        print(f"fetch_elevation_difference Python error for lat={lat}, lon={lon}: {e}")
        return None

def fetch_ee_data(latitude, longitude):
    lst_value = fetch_lst(latitude, longitude)
    ndvi_value = fetch_ndvi(latitude, longitude)
    rainfall_value = fetch_rainfall(latitude, longitude)
    flood_history_value = fetch_flood_history(latitude, longitude)
    wind_solar_value = fetch_wind_data_and_solar(latitude, longitude).split()
    wind_speed = wind_solar_value[0]
    wind_direction = wind_solar_value[1]
    solar_radiation = wind_solar_value[2]
    elevation_diff_value = fetch_elevation_difference(latitude, longitude).split()
    elevation_level = elevation_diff_value[0]
    elevation_diff = elevation_diff_value[1]
    response = {'LST_avg': lst_value, 'NDVI_avg':ndvi_value,'rainfall_monthly_avg':rainfall_value, 'flood_history': flood_history_value, 'wind_speed_avg': wind_speed, 'wind_direction':wind_direction, 'solar_radiation':solar_radiation, 'elevation_level':elevation_level, "elevation_difference":elevation_diff}
    return response

parser1 = PydanticOutputParser(pydantic_object=Address)

parser2 = PydanticOutputParser(pydantic_object=TenderValidationOutput)

prompt_for_location_extraction = PromptTemplate(
    template="""
Based on the context below, find the location of the project and return it in the form that is easy for geocoding, {format_instructions}                    
CONTEXT:
<<TENDER_DOCUMENT>>
{document}
<<END_DOCUMENT>>

""",
    input_variables=["document"],
    partial_variables={"format_instructions": parser1.get_format_instructions()}
)

prompt_for_detail_generation = PromptTemplate(
    template="""You are the ultimate affordable-housing tender expert: twenty years of underwriting, financial modeling & policy review at Google, Facebook and Amazon housing equity teams. You command DHCD, HUD, LIHTC, DC BEPS and every regulatory framework inside out
Your mission: perform a surgical, end-to-end comparison of a tender submission against its RFP, then generate a fully populated JSON report.
Regarding to financial metrics, provide some logical figures, you may also make some suggestions.

TASKS (in order):
1. Parse the RFP—extract every scoring criterion, sub-criterion, and point weight.
2. Assign sub-scores (0→full) with one-sentence evidence citing exact text/paragraph.
3. Compute ROI, DSCR, NPV, payback, leverage—show formulas.
4. Normalize raw total (0–163) to “overallFinalScore.overallScore_pct” (0–100%).
5. Map that score to “winningRate_pct” (≥85→90%; 70–85→50%; <70→10%).
6. Populate **gaps**: list missing/incomplete threshold items, with title & description.
7. Populate **mandatoryActions**, **mediocreActions**, **goodToHaveUpgrades**.
8. Build **complianceRiskMatrix**. 
9 **sustainabilityAssessment** (green targets, certificationLevel, netZeroReady, solarPVCapacity_kW, solarCoverage_pct, batteryStorage_kWh, evChargingReady, rainwaterHarvestingCapacity_liters, waterSavings_pct, insulationRValues.walls & .roof, energyEfficiencyMeasures, annualEnergySavings_RM, annualWaterSavings_RM, operationalOPEXReduction_pct, bepsCompliance, greenGrantSubsidyApplied, embodiedCarbonAssessment, sustainabilityScore, sustainabilityRisks[], recommendations[], finalSustainabilityVerdict).
10. SustainabilitySuggestion(BaseModel):feature: str, description: str. Choose based on this example: 50000$ {sus_feature}
11. Estimate **carbonFootprintReduction_tCO2_perYear**.
11. Fill **financialSnapshot**: projectName, location, scope, totalDevelopmentCost, tenderBudget, overallFinancialFeasibility, costBreakdown.*, financingCapitalStack[], keyFinancialMetrics.*, fiveYearProjection[], sensitivityAnalysis[], recommendations[], finalVerdict. (Must provide ROI, IRR and NPV)
12. Populate **certificationAlignment[]**.
13. Add **certificationNextSteps[]**: str for Next Steps for Certification
14. Populate **compositeRatings** (sustainability, finance, durability).
15. Populate **detailedScoreTable[]**.
16. Return **overallFinalScore** and **winningRate_pct**.

❗ **Strictly** adhere to the schema—no extra or missing fields. Output only the JSON.
                                     
CONTEXT:
<<TENDER_DOCUMENT>>
{document}
<<END_DOCUMENT>>

<<TENDER_SUBMISSION>>
{submission}
<<END_SUBMISSION>>

Answer it in {format_instructions}
""",
    input_variables=["document", "submission", "sus_feature"],
    partial_variables={"format_instructions": parser2.get_format_instructions()},
)

llm2 = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro-exp-03-25",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key = ""
)

llm1 = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite-001",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key = ""
)

llm3 = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite-001",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key = ""
)

def generates(prompt, model, parser, parameters):
    chain = prompt | model | parser
    return chain.invoke(parameters)

def post_to_agent(document, submission, processed_data):
    url = "http://127.0.0.1:7000/run"   # or whatever your endpoint is
    payload = {
    "app_name": "multi_tool_agent",
    "user_id": "u_123",
    "session_id": "s_123",
    "new_message": {
        "role": "user",
        "parts": [{
        "text": f"Remember this info for further usage. Tender Document: {document}, \n\nTender Submission by user: {submission}, \n\n Data processed by another agent: {processed_data}. Just return ok, dont use any tool yet. get it quick. "
        }]
        },
    }
    headers = {"Content-Type": "application/json"}

    # create a client, send the POST, and get back JSON
    with httpx.Client(timeout=timeout_config) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()        # raises if 4xx/5xx
        data = response.json()
        print("Got:", data)

    return data

def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)

async def image_generate(prompt, file):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY1"),
    )
    parts=[types.Part.from_text(text=prompt)]
    files = [
            client.files.upload(file=file),
        ]
    image = types.Part.from_uri(
                    file_uri=files[0].uri,
                    mime_type=files[0].mime_type,
                ) 
    parts.append(image)
    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=parts,
        )
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=20000,
        response_modalities=[
            "image",
            "text",
        ],
        safety_settings=[
            types.SafetySetting(
                category="HARM_CATEGORY_CIVIC_INTEGRITY",
                threshold="OFF",  # Off
            ),
        ],
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
            continue
        if chunk.candidates[0].content.parts[0].inline_data:
            file_name = "3d_model.jpg"
            save_binary_file(
                file_name, chunk.candidates[0].content.parts[0].inline_data.data
            )
            
            print(
                f"✅ File saved to: {file_name} (MIME: {chunk.candidates[0].content.parts[0].inline_data.mime_type})"
            )
            return chunk.candidates[0].content.parts[0].inline_data.data
        else:
            print(chunk.text)

def calendar_creation(actions:List[ActionItem]):
    calendar_id = "1fcbaedeedb15f25a1c8e71ad79eded5f1a118c95cf4c32f091ce736c140e41d@group.calendar.google.com"
    parser = PydanticOutputParser(pydantic_object=GoogleEventList)
    prompt = PromptTemplate(template="""You are an elite AI construction assistant trained to build a full action timeline from a tender improvement plan.

    Based on the mandatory action list provided, extract 3–5 key scheduled actions required to improve or complete the construction tender submission.

    For each action, return the following fields:
    - summary: A short, clear title of the action item
    - location: Where the action occurs (or "Online" if not location-specific)
    - description: A concise elaboration of what the action entails and why it is required
    - start: Scheduled start date/time in ISO 8601 format (e.g., "2025-05-10T09:00:00+08:00")
    - end: Scheduled end date/time in ISO 8601 format
    - timeZone: Use "Asia/Kuala_Lumpur" by default

    Return the full output as a JSON object with the format:

    {format_instructions}

    ---

    📋 Mandatory action list for tender improvement:
    "{mandatory_actions}"

    💡 Output only the structured event list in JSON format.""",
    input_variables=['mandatory_actions'],
    partial_variables={"format_instructions": parser.get_format_instructions()},)
    events = generates(prompt, llm1, parser, {"mandatory_actions":actions}).event_list

    for event in events:
        created_event = service.events().insert(calendarId=calendar_id, body=event.model_dump()).execute()
        print("✅ Event created:", created_event['htmlLink'])
    return "Calendar done"

    



@apps.post("/process", response_class=HTMLResponse)
def preload(request: Request, document: UploadFile = File(...), submission: UploadFile  = File(...),image: UploadFile= File(...)):
    start = time.time()
    files = [document.file, submission.file]
    image_byte = asyncio.run(image.read())
    content = []
    for i in files:
        reader = PyPDF2.PdfReader(i)
        all_text = []

                # Iterate through each page and extract text
        for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        all_text.append(text)

        # Combine all extracted text
        full_text = "\n\n".join(all_text)
        content.append(full_text)

    start = time.time()
    location = generates(prompt_for_location_extraction, llm1, parser1, {'document':content[0]})
    destination = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key=AIzaSyB5oltuq_EXN0Gx_lo6jo8idtA0EtT0nII"
    print(location, destination)
    with httpx.Client(timeout=timeout_config) as client:
        response = client.get(destination)
        data = response.json()

        if data["status"] == "OK":
            loc = data["results"][0]["geometry"]["location"]
            print("Latitude:", loc["lat"])
            print("Longitude:", loc["lng"])
        else:
            print("Error:", data["status"])

        ee_context = json.dumps(fetch_ee_data(loc['lat'], loc['lat']))
    skeleton = generates(prompt_for_detail_generation, llm2, parser2, {'document':content[0],'submission':content[1],'sus_feature':ee_context})
    print(skeleton)

    data = skeleton.model_dump()
    data = data | {"timestamp":firestore.SERVER_TIMESTAMP}
    write_time, doc_ref = db.collection("projects").add(data) 
    db.collection("caching_data").add({"timestamp":firestore.SERVER_TIMESTAMP, "document":content[0], "submission":content[1], "data":data})
    print(doc_ref, write_time)
    new_id = doc_ref.id
    print(data)

    response = post_to_agent(document, submission, data)
    print(f"Done sending to agent.\nAgent response: {response}")
    print(f"Time taken = {time.time()-start}")
    #threed_image = asyncio.run(image_generate(TWO_TO_THREE_PROMPT,io.BytesIO(image)))
    asyncio.run(generate(THREEJS_PROMPT(data, skeleton.sustainabilityAssessment.recommendations), pattern = [re.compile(r"(replace here)"), re.compile(r"(```json)|(```)")], image_bytes = image_byte))
    print(calendar_creation(skeleton.mandatoryActions))
    return templates.TemplateResponse("risk.html", {
        "request": request,
        "id" : new_id,
        **data 
    })


@apps.get("/", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})

@apps.get("/start", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("nland.html", {"request": request})


url = "http://localhost:7000/apps/multi_tool_agent/users/u_123/sessions/s_123"   # or whatever your endpoint is
headers = {"Content-Type": "application/json"}

try:
    with httpx.Client(timeout=timeout_config) as client:
        response = client.post(url, headers=headers)
        response.raise_for_status()  # Raises HTTPStatusError if status is 4xx/5xx
        data = response.json()
        print("✅ Session started:", data)

except httpx.HTTPStatusError as e:
    if e.response.status_code == 409:
        print("⚠️ Session already initiated. Skipping re-init.")
    else:
        print(f"❌ HTTP error occurred: {e.response.status_code} - {e.response.text}")

except httpx.RequestError as e:
    print(f"❌ Request failed: {str(e)}")

except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")

items = list(db.collection("caching_data").order_by("timestamp", direction=firestore.Query.DESCENDING).stream())[0].to_dict()
print(items)
document = items['document']
submission = items['submission']
data = items['data']
post_to_agent(document, submission, data)

@apps.post("/test",response_class=HTMLResponse)
def test(request: Request):
    time.sleep(3)
    return templates.TemplateResponse("risk.html", {"request":request, "document": document, "submission": submission, **data })
