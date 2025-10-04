# Smart Garden Planner - Hacktoberfest Project Specification

## Project Overview

**Smart Garden Planner** is an AI-powered web application that helps users design native, climate-appropriate gardens by providing personalized plant recommendations and visual landscape designs.

### Core Value Proposition
- Simplifies garden planning with AI-driven recommendations
- Promotes native plants and sustainable landscaping
- Provides interactive visualization of garden designs
- Reduces decision paralysis with curated, zone-specific suggestions

---

## Process Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: LOCATION INPUT                                          │
│  ├─ Address (e.g., "123 Main St, Denver, CO")                   │
│  ├─ Yard Direction (N, S, E, W, NE, SE, SW, NW)                │
│  └─ Optional: Yard Photo Upload                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  GEOCODING & ZONE DETECTION                                      │
│  ├─ API: Address → Lat/Long                                     │
│  ├─ API: Lat/Long → USDA Hardiness Zone                        │
│  └─ Store: Zone, Coordinates, Season (from current date)        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: PREFERENCES INPUT                                       │
│  ├─ Water Availability (Low/Medium/High)                        │
│  ├─ Maintenance Level (Low/Medium/High)                         │
│  └─ Garden Type (Native/Flower/Vegetable/Mixed)                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  DIGITALOCEAN GRADIENT AI AGENT                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Agent Configuration                                        │ │
│  │ ├─ Model: OpenAI GPT-oss-120b                            │ │
│  │ ├─ Knowledge Base: Plant Database (attached)             │ │
│  │ └─ Instructions: Gardening Expert Prompt                 │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Agent Query:                                                    │
│  {                                                               │
│    "zone": "6b",                                                │
│    "direction": "S",                                            │
│    "water": "Low",                                              │
│    "maintenance": "Low",                                        │
│    "gardenType": "Native Plants",                              │
│    "currentDate": "2025-10-04",                                │
│    "currentSeason": "fall"                                      │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT PROCESSING                                                │
│  1. Query Knowledge Base with filters                           │
│  2. Filter by zone compatibility                                │
│  3. Filter by sun requirements (direction → sun level)          │
│  4. Filter by water/maintenance preferences                     │
│  5. Filter by planting season                                   │
│  6. Apply companion planting logic                              │
│  7. Generate care timeline based on current date                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: PLANT RECOMMENDATIONS                                   │
│  ├─ Display: 4-8 recommended plants                            │
│  ├─ Each plant shows:                                           │
│  │   - Common & scientific names                               │
│  │   - Sun/water/maintenance requirements                      │
│  │   - Planting season ("Plant Now" badge)                    │
│  │   - Spacing guidelines                                      │
│  │   - Care notes                                              │
│  │   - Companion plants                                        │
│  └─ User can: Check/uncheck plants to select                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  IMAGE GENERATION                                                │
│  ├─ Input: Selected plants + original photo (optional)         │
│  ├─ Service: Image Generation API (Stable Diffusion/DALL-E)    │
│  ├─ Prompt Construction:                                        │
│  │   "Landscape design photo showing [plant1], [plant2]...    │
│  │    arranged in a [direction]-facing yard, realistic style" │
│  ├─ Store: Generated image in DO Spaces                        │
│  └─ Display: Rendered landscape visualization                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  RE-GENERATION LOOP                                              │
│  ├─ User toggles plants on/off                                 │
│  ├─ Click "Regenerate Image"                                   │
│  └─ Generate new image with updated plant selection            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  FINAL OUTPUT                                                    │
│  ├─ Plant list with care instructions                          │
│  ├─ Visual landscape design                                     │
│  ├─ Month-by-month care timeline                               │
│  └─ Print/Export functionality                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Knowledge Base Structure

The DO Agent requires a comprehensive plant database as its knowledge base. This should be structured as JSON or CSV files that can be indexed and queried.

### Database Schema

#### Primary Plant Database (`plants.json`)

```json
{
  "plants": [
    {
      "id": "plant-001",
      "commonName": "Black-Eyed Susan",
      "scientificName": "Rudbeckia hirta",
      "category": "perennial",
      "native": true,
      "nativeRegions": ["Eastern US", "Midwest"],
      
      "growingConditions": {
        "zones": ["3", "4", "5", "6", "7", "8", "9"],
        "sunRequirements": "full",
        "waterNeeds": "low",
        "soilType": ["clay", "loam", "sand"],
        "soilPH": [6.0, 7.5],
        "maintenanceLevel": "low"
      },
      
      "plantingInfo": {
        "springPlanting": {
          "start": "04-01",
          "end": "05-30",
          "notes": "Plant after last frost"
        },
        "fallPlanting": {
          "start": "09-01",
          "end": "10-15",
          "notes": "Plant 6 weeks before first frost"
        },
        "spacing": "12-18 inches",
        "depth": "1/4 inch",
        "germinationDays": 7
      },
      
      "characteristics": {
        "matureHeight": "24-36 inches",
        "matureWidth": "12-18 inches",
        "bloomSeason": ["summer", "fall"],
        "bloomColor": ["yellow", "orange"],
        "foliageColor": "green",
        "wildlife": ["pollinators", "butterflies", "birds"],
        "deerResistant": false
      },
      
      "companionPlants": [
        "purple-coneflower",
        "switchgrass",
        "little-bluestem",
        "bee-balm"
      ],
      
      "care": {
        "watering": "Weekly during establishment, then drought tolerant",
        "fertilizing": "Not required",
        "pruning": "Deadhead for continuous blooms, or leave seed heads for birds",
        "pests": ["aphids"],
        "diseases": ["powdery mildew"],
        "winterCare": "Leave foliage standing for winter interest"
      },
      
      "benefits": [
        "Attracts pollinators",
        "Low maintenance",
        "Drought tolerant once established",
        "Provides food for birds",
        "Long bloom period"
      ],
      
      "tags": ["native", "pollinator-friendly", "low-water", "easy-care"]
    }
  ]
}
```

#### Companion Planting Matrix (`companions.json`)

```json
{
  "companions": [
    {
      "plant1": "tomato",
      "plant2": "basil",
      "relationship": "beneficial",
      "reason": "Basil repels pests and may improve tomato flavor"
    },
    {
      "plant1": "black-eyed-susan",
      "plant2": "purple-coneflower",
      "relationship": "beneficial",
      "reason": "Similar growing requirements, complementary bloom times"
    }
  ]
}
```

#### Seasonal Calendar (`planting_calendar.json`)

```json
{
  "zones": [
    {
      "zone": "6b",
      "firstFrostDate": "10-25",
      "lastFrostDate": "04-15",
      "seasons": {
        "spring": {
          "plantable": ["tomato", "basil", "black-eyed-susan"],
          "tasks": ["Prepare soil", "Start seeds indoors", "Plant after last frost"]
        },
        "fall": {
          "plantable": ["black-eyed-susan", "purple-coneflower"],
          "tasks": ["Plant perennials", "Add mulch", "Divide perennials"]
        }
      }
    }
  ]
}
```

#### Regional Native Plants (`native_plants.json`)

```json
{
  "regions": [
    {
      "region": "Rocky Mountains",
      "states": ["CO", "WY", "MT"],
      "zones": ["3", "4", "5", "6"],
      "nativePlants": [
        "penstemon",
        "columbine",
        "yarrow",
        "blue-grama-grass"
      ]
    }
  ]
}
```

### Knowledge Base Size Estimate

For a comprehensive US-focused database:
- **Native Plants**: ~500 entries (50 per region × 10 regions)
- **Popular Garden Plants**: ~200 entries
- **Companion Relationships**: ~1,000 pairs
- **Seasonal Calendar**: 13 zones × 4 seasons = 52 entries

**Total Storage**: Approximately 5-10MB of JSON data

### Data Sources to Populate Knowledge Base

1. **USDA Plants Database** (plants.usda.gov)
2. **Lady Bird Johnson Wildflower Center** (wildflower.org)
3. **Missouri Botanical Garden** (missouribotanicalgarden.org)
4. **Native Plant Finder** (nwf.org)
5. **State Extension Services** (university agricultural programs)

---

## Technical Architecture

### Frontend Stack
- **Framework**: React (via Vite or Next.js)
- **Styling**: Tailwind CSS
- **Hosting**: DigitalOcean App Platform
- **Image Upload**: Direct to DO Spaces

### Backend Services

#### 1. DigitalOcean Gradient AI Agent
- **Purpose**: Core recommendation engine
- **Model**: OpenAI GPT-oss-120b
- **Configuration**:
  ```
  Agent Name: Garden Planner Expert
  
  Instructions:
  You are an expert horticulturist and landscape designer. Your role is to 
  recommend climate-appropriate, native plants based on the user's location, 
  preferences, and current season.
  
  When providing recommendations:
  1. ALWAYS prioritize native plants for the user's region
  2. Filter by USDA Hardiness Zone compatibility
  3. Consider the current date and planting season
  4. Match sun requirements to yard direction (N=shade, S=full, E/W=partial)
  5. Respect user's water availability and maintenance preferences
  6. Suggest companion planting combinations
  7. Provide specific planting instructions based on current season
  8. Include care instructions and timeline
  
  Return recommendations in structured JSON format with plant details, 
  care instructions, and planting timeline.
  
  Always explain WHY each plant is recommended for the user's specific conditions.
  ```
  
- **Knowledge Base**: Upload `plants.json`, `companions.json`, `planting_calendar.json`

#### 2. Geocoding Service
- **Service**: Google Maps Geocoding API or MapBox
- **Purpose**: Convert address → coordinates
- **Fallback**: Manual zip code entry

#### 3. USDA Zone Lookup
- **Service**: Custom API or Phytosanitary Certificate API
- **Purpose**: Coordinates → Hardiness Zone
- **Fallback**: Embedded zone map with manual selection

#### 4. Image Generation Service
- **Option A**: Stable Diffusion API (Replicate, HuggingFace)
- **Option B**: DALL-E 3 API (OpenAI)
- **Option C**: Midjourney API
- **Purpose**: Generate landscape visualization
- **Prompt Template**:
  ```
  "Professional landscape photography of a [direction]-facing yard with 
  [plant1 common name], [plant2 common name], [plant3 common name] planted 
  in natural arrangement. Realistic, well-lit, showing plants at mature size. 
  Photorealistic style, garden photography."
  ```

#### 5. Storage
- **Service**: DigitalOcean Spaces
- **Usage**:
  - User-uploaded yard photos
  - Generated landscape images
  - Static plant images (optional)

### Database
- **Service**: DO Managed PostgreSQL or MongoDB
- **Purpose**: 
  - User sessions (optional)
  - Save/share garden plans
  - Usage analytics

---

## API Flow

### 1. Submit User Input
```javascript
POST /api/recommendations
{
  "address": "123 Main St, Denver, CO 80202",
  "direction": "S",
  "water": "Low",
  "maintenance": "Low",
  "gardenType": "Native Plants"
}
```

### 2. Backend Processing
```javascript
// Geocode address
const coords = await geocode(address);

// Get USDA zone
const zone = await getHardinessZone(coords.lat, coords.lng);

// Determine sun level from direction
const sunLevel = {
  'N': 'shade',
  'NE': 'partial', 'NW': 'partial',
  'E': 'partial', 'W': 'partial',
  'SE': 'partial', 'SW': 'partial',
  'S': 'full'
}[direction];

// Get current season
const season = getCurrentSeason(zone);

// Query DO Agent
const recommendations = await gradientAI.query({
  zone,
  sunLevel,
  water,
  maintenance,
  gardenType,
  season,
  currentDate: new Date().toISOString()
});
```

### 3. Agent Response
```json
{
  "zone": "6b",
  "season": "Fall Planting Season",
  "plants": [
    {
      "name": "Black-Eyed Susan",
      "scientific": "Rudbeckia hirta",
      "sun": "Full Sun",
      "water": "Low",
      "maintenance": "Low",
      "plantNow": true,
      "spacing": "12-18 inches",
      "companions": ["Purple Coneflower", "Switchgrass"],
      "notes": "Native perennial. Plant now for spring blooms..."
    }
  ],
  "timeline": [
    {
      "month": "October",
      "tasks": ["Plant perennials", "Add mulch", "Water deeply once"]
    }
  ]
}
```

### 4. Generate Image
```javascript
POST /api/generate-image
{
  "plants": ["Black-Eyed Susan", "Purple Coneflower", "Russian Sage"],
  "direction": "S",
  "originalPhoto": "base64..." // optional
}

// Response
{
  "imageUrl": "https://spaces.digitalocean.com/gardens/abc123.png"
}
```

---

## Implementation Checklist

### Phase 1: MVP (Core Functionality)
- [ ] Set up DO Gradient AI Agent
- [ ] Create plant knowledge base (50-100 essential plants)
- [ ] Build React frontend with 3-step wizard
- [ ] Implement address → zone lookup
- [ ] Connect to DO Agent API
- [ ] Display plant recommendations
- [ ] Add plant selection (checkboxes)
- [ ] Deploy to DO App Platform

### Phase 2: Image Generation
- [ ] Integrate image generation API
- [ ] Build prompt generation logic
- [ ] Set up DO Spaces for image storage
- [ ] Add image display and regeneration
- [ ] Optimize image loading

### Phase 3: Polish
- [ ] Add care timeline generation
- [ ] Implement print functionality
- [ ] Add error handling and loading states
- [ ] Create comprehensive README
- [ ] Add demo video/GIF
- [ ] Write CONTRIBUTING.md
- [ ] Add CODE_OF_CONDUCT.md
- [ ] Choose open-source license (MIT recommended)

### Phase 4: Documentation
- [ ] Document API endpoints
- [ ] Create knowledge base contribution guide
- [ ] Add deployment instructions
- [ ] Write agent configuration guide
- [ ] Create demo environment

---

## Environment Variables

```env
# DigitalOcean
DO_AGENT_API_KEY=your_agent_api_key
DO_AGENT_ENDPOINT=https://api.digitalocean.com/v1/agents/your-agent-id
DO_SPACES_KEY=your_spaces_key
DO_SPACES_SECRET=your_spaces_secret
DO_SPACES_ENDPOINT=nyc3.digitaloceanspaces.com
DO_SPACES_BUCKET=garden-planner

# Geocoding
GOOGLE_MAPS_API_KEY=your_google_maps_key
# OR
MAPBOX_API_KEY=your_mapbox_key

# Image Generation
REPLICATE_API_KEY=your_replicate_key
# OR
OPENAI_API_KEY=your_openai_key

# Optional
DATABASE_URL=postgresql://...
```

---

## Success Metrics

### Hackathon Judging Criteria

1. **Use of AI Platform** ✅
   - Core functionality powered by DO Gradient AI Agent
   - Knowledge base utilization for recommendations
   - Demonstrates agent capabilities

2. **Completeness** ✅
   - Full user flow implemented
   - Plant recommendations working
   - Image generation functional
   - Care instructions provided

3. **Impact** ✅
   - Promotes native plants and sustainability
   - Makes garden planning accessible
   - Real-world utility
   - Open-source knowledge base

4. **UI/UX** ✅
   - Clean, intuitive interface
   - Dark mode aesthetic
   - Step-by-step wizard
   - Visual feedback for selections

---

## Future Enhancements

- **User Accounts**: Save and share garden plans
- **Shopping List**: Generate plant purchasing list with local nursery links
- **Mobile App**: React Native version
- **Community Features**: Share designs, vote on favorites
- **AR Preview**: View plants in your actual yard using phone camera
- **Seasonal Reminders**: Email notifications for care tasks
- **Multi-Yard Support**: Manage front yard, back yard, containers separately
- **Budget Estimator**: Calculate total project cost
- **Video Tutorials**: Embedded planting and care videos
- **Climate Change Projections**: Show future zone predictions

---

## License

MIT License - Encourages open-source contribution and reuse

---

## Repository Structure

```
garden-planner/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── .env.example
├── package.json
├── vite.config.js
├── src/
│   ├── components/
│   │   ├── LocationForm.jsx
│   │   ├── PreferencesForm.jsx
│   │   ├── PlantCard.jsx
│   │   ├── ImageGenerator.jsx
│   │   └── Timeline.jsx
│   ├── services/
│   │   ├── gradientAI.js
│   │   ├── geocoding.js
│   │   ├── imageGen.js
│   │   └── storage.js
│   ├── utils/
│   │   ├── zoneLookup.js
│   │   └── seasonCalc.js
│   └── App.jsx
├── knowledge-base/
│   ├── plants.json
│   ├── companions.json
│   ├── planting_calendar.json
│   └── native_plants.json
├── docs/
│   ├── AGENT_SETUP.md
│   ├── API_DOCUMENTATION.md
│   └── KNOWLEDGE_BASE.md
└── demo/
    └── demo.gif
```

---

**Project Lead**: [Your Name]  
**Hackathon**: Hacktoberfest 2025  
**Tech Stack**: React + DigitalOcean Gradient AI + Tailwind CSS  
**Repository**: github.com/yourusername/smart-garden-planner
