import React, { useState } from 'react';
import { Leaf, MapPin, Droplets, Sun, Calendar, Sprout } from 'lucide-react';

export default function GardenPlanner() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    address: '',
    direction: '',
    maintenance: '',
    water: '',
    gardenType: '',
    photo: null
  });
  const [recommendations, setRecommendations] = useState(null);
  const [selectedPlants, setSelectedPlants] = useState(new Set());
  const [generatedImage, setGeneratedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generatingImage, setGeneratingImage] = useState(false);

  // Mock plant data
  const mockRecommendations = {
    zone: "6b",
    season: "Fall Planting Season",
    plants: [
      {
        name: "Black-Eyed Susan",
        scientific: "Rudbeckia hirta",
        sun: "Full Sun",
        water: "Low",
        maintenance: "Low",
        plantNow: true,
        spacing: "12-18 inches",
        companions: ["Purple Coneflower", "Switchgrass"],
        notes: "Native perennial. Plant now for spring blooms. Attracts pollinators."
      },
      {
        name: "Autumn Joy Sedum",
        scientific: "Sedum spectabile",
        sun: "Full Sun",
        water: "Low",
        maintenance: "Low",
        plantNow: true,
        spacing: "18-24 inches",
        companions: ["Russian Sage", "Black-Eyed Susan"],
        notes: "Drought-tolerant succulent. Provides fall color and winter interest."
      },
      {
        name: "Russian Sage",
        scientific: "Perovskia atriplicifolia",
        sun: "Full Sun",
        water: "Low",
        maintenance: "Low",
        plantNow: true,
        spacing: "24-36 inches",
        companions: ["Sedum", "Ornamental Grasses"],
        notes: "Aromatic foliage. Long blooming period. Deer resistant."
      },
      {
        name: "Purple Coneflower",
        scientific: "Echinacea purpurea",
        sun: "Full Sun to Partial Shade",
        water: "Medium",
        maintenance: "Low",
        plantNow: true,
        spacing: "18-24 inches",
        companions: ["Black-Eyed Susan", "Switchgrass"],
        notes: "Native perennial. Medicinal properties. Birds love the seed heads."
      }
    ],
    timeline: [
      { month: "October", tasks: ["Plant perennials", "Add mulch", "Water deeply once"] },
      { month: "November", tasks: ["Stop watering", "Leave seed heads for birds"] },
      { month: "Spring", tasks: ["Cut back dead foliage", "Apply compost", "Watch for new growth"] }
    ]
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate API call to DO Agent
    setTimeout(() => {
      setRecommendations(mockRecommendations);
      // Initialize all plants as selected
      const allPlantNames = mockRecommendations.plants.map(p => p.name);
      setSelectedPlants(new Set(allPlantNames));
      setLoading(false);
      setStep(3);
    }, 2000);
  };

  const togglePlant = (plantName) => {
    const newSelected = new Set(selectedPlants);
    if (newSelected.has(plantName)) {
      newSelected.delete(plantName);
    } else {
      newSelected.add(plantName);
    }
    setSelectedPlants(newSelected);
  };

  const generateLandscapeImage = async () => {
    setGeneratingImage(true);
    // Simulate API call to image generation service
    setTimeout(() => {
      // Mock generated image
      setGeneratedImage('/api/placeholder/800/600');
      setGeneratingImage(false);
    }, 3000);
  };

  const handleInputChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-green-900 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8 pt-8">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Leaf className="w-10 h-10 text-green-400" />
            <h1 className="text-4xl font-bold text-green-100">Smart Garden Planner</h1>
          </div>
          <p className="text-green-300">AI-powered native plant recommendations for your yard</p>
        </div>

        {/* Progress Steps */}
        <div className="flex justify-center gap-4 mb-8">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${step >= 1 ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-400'}`}>
            <span className="font-semibold">1</span>
            <span>Location</span>
          </div>
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${step >= 2 ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-400'}`}>
            <span className="font-semibold">2</span>
            <span>Preferences</span>
          </div>
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${step >= 3 ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-400'}`}>
            <span className="font-semibold">3</span>
            <span>Results</span>
          </div>
        </div>

        {/* Step 1: Location */}
        {step === 1 && (
          <div className="bg-gray-800 rounded-lg shadow-2xl p-8 border border-gray-700">
            <h2 className="text-2xl font-bold text-green-400 mb-6 flex items-center gap-2">
              <MapPin className="w-6 h-6" />
              Tell us about your location
            </h2>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-200 mb-2">
                  Your Address
                </label>
                <input
                  type="text"
                  placeholder="123 Main St, Denver, CO 80202"
                  className="w-full px-4 py-3 bg-gray-700 border-2 border-gray-600 rounded-lg focus:border-green-500 focus:outline-none text-white placeholder-gray-400"
                  value={formData.address}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                />
                <p className="text-sm text-gray-400 mt-1">We'll auto-detect your USDA Hardiness Zone</p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-200 mb-2">
                  Which direction does your yard face?
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'].map((dir) => (
                    <button
                      key={dir}
                      onClick={() => handleInputChange('direction', dir)}
                      className={`py-3 px-4 rounded-lg font-semibold transition-colors ${
                        formData.direction === dir
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-700 text-gray-200 hover:bg-gray-600 border border-gray-600'
                      }`}
                    >
                      {dir}
                    </button>
                  ))}
                </div>
                <p className="text-sm text-gray-400 mt-1">
                  N = Shade • S = Full Sun • E/W = Partial Sun
                </p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-200 mb-2">
                  Upload a photo of your yard (optional)
                </label>
                <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-green-500 transition-colors cursor-pointer bg-gray-700/50">
                  <Sprout className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-300">Click to upload or drag and drop</p>
                  <p className="text-sm text-gray-400">For visual reference only</p>
                </div>
              </div>

              <button
                onClick={() => setStep(2)}
                disabled={!formData.address || !formData.direction}
                className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed"
              >
                Continue to Preferences
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Preferences */}
        {step === 2 && (
          <div className="bg-gray-800 rounded-lg shadow-2xl p-8 border border-gray-700">
            <h2 className="text-2xl font-bold text-green-400 mb-6">
              What are your gardening preferences?
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-200 mb-2 flex items-center gap-2">
                  <Droplets className="w-5 h-5" />
                  Water Availability
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {['Low', 'Medium', 'High'].map((level) => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => handleInputChange('water', level)}
                      className={`py-3 px-4 rounded-lg font-semibold transition-colors ${
                        formData.water === level
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-700 text-gray-200 hover:bg-gray-600 border border-gray-600'
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-200 mb-2 flex items-center gap-2">
                  <Sun className="w-5 h-5" />
                  Maintenance Level
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {['Low', 'Medium', 'High'].map((level) => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => handleInputChange('maintenance', level)}
                      className={`py-3 px-4 rounded-lg font-semibold transition-colors ${
                        formData.maintenance === level
                          ? 'bg-orange-600 text-white'
                          : 'bg-gray-700 text-gray-200 hover:bg-gray-600 border border-gray-600'
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-200 mb-2 flex items-center gap-2">
                  <Leaf className="w-5 h-5" />
                  Garden Type
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {['Native Plants', 'Flower Garden', 'Vegetable Garden', 'Mixed'].map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => handleInputChange('gardenType', type)}
                      className={`py-3 px-4 rounded-lg font-semibold transition-colors ${
                        formData.gardenType === type
                          ? 'bg-green-600 text-white'
                          : 'bg-gray-700 text-gray-200 hover:bg-gray-600 border border-gray-600'
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 bg-gray-700 text-gray-200 py-3 rounded-lg font-semibold hover:bg-gray-600 transition-colors border border-gray-600"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={!formData.water || !formData.maintenance || !formData.gardenType}
                  className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed"
                >
                  {loading ? 'Generating Plan...' : 'Get My Plant Plan'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Step 3: Results */}
        {step === 3 && recommendations && (
          <div className="space-y-6">
            {/* Zone Info */}
            <div className="bg-gray-800 rounded-lg shadow-2xl p-6 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-300">Your Growing Zone</h3>
                  <p className="text-3xl font-bold text-green-400">{recommendations.zone}</p>
                </div>
                <div className="text-right">
                  <h3 className="text-lg font-semibold text-gray-300">Current Season</h3>
                  <p className="text-xl font-bold text-orange-400">{recommendations.season}</p>
                </div>
              </div>
            </div>

            {/* Plant Recommendations */}
            <div className="bg-gray-800 rounded-lg shadow-2xl p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-green-400 flex items-center gap-2">
                  <Leaf className="w-6 h-6" />
                  Recommended Plants for Your Yard
                </h2>
                <span className="text-sm text-gray-400">
                  {selectedPlants.size} of {recommendations.plants.length} selected
                </span>
              </div>
              
              <div className="grid gap-4">
                {recommendations.plants.map((plant, idx) => (
                  <div 
                    key={idx} 
                    className={`border-2 rounded-lg p-4 transition-all ${
                      selectedPlants.has(plant.name)
                        ? 'border-green-500 bg-gray-700/50'
                        : 'border-gray-600 bg-gray-700/20 opacity-60'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-start gap-3 flex-1">
                        <input
                          type="checkbox"
                          checked={selectedPlants.has(plant.name)}
                          onChange={() => togglePlant(plant.name)}
                          className="mt-1 w-5 h-5 rounded border-gray-600 bg-gray-700 checked:bg-green-600 cursor-pointer"
                        />
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-green-300">{plant.name}</h3>
                          <p className="text-sm text-gray-400 italic">{plant.scientific}</p>
                        </div>
                      </div>
                      {plant.plantNow && (
                        <span className="bg-green-900/50 text-green-300 px-3 py-1 rounded-full text-sm font-semibold border border-green-700">
                          Plant Now
                        </span>
                      )}
                    </div>
                    
                    <div className="grid grid-cols-4 gap-2 my-3 ml-8">
                      <div className="bg-yellow-900/30 p-2 rounded text-center border border-yellow-700/30">
                        <p className="text-xs text-gray-400">Sun</p>
                        <p className="font-semibold text-sm text-yellow-300">{plant.sun}</p>
                      </div>
                      <div className="bg-blue-900/30 p-2 rounded text-center border border-blue-700/30">
                        <p className="text-xs text-gray-400">Water</p>
                        <p className="font-semibold text-sm text-blue-300">{plant.water}</p>
                      </div>
                      <div className="bg-purple-900/30 p-2 rounded text-center border border-purple-700/30">
                        <p className="text-xs text-gray-400">Care</p>
                        <p className="font-semibold text-sm text-purple-300">{plant.maintenance}</p>
                      </div>
                      <div className="bg-green-900/30 p-2 rounded text-center border border-green-700/30">
                        <p className="text-xs text-gray-400">Spacing</p>
                        <p className="font-semibold text-sm text-green-300">{plant.spacing}</p>
                      </div>
                    </div>

                    <p className="text-gray-300 mb-2 ml-8">{plant.notes}</p>
                    
                    <div className="bg-emerald-900/30 p-3 rounded mt-2 ml-8 border border-emerald-700/30">
                      <p className="text-sm font-semibold text-emerald-300 mb-1">Companion Plants:</p>
                      <p className="text-sm text-emerald-400">{plant.companions.join(', ')}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Image Generation */}
            <div className="bg-gray-800 rounded-lg shadow-2xl p-6 border border-gray-700">
              <h2 className="text-2xl font-bold text-green-400 mb-4 flex items-center gap-2">
                <Sprout className="w-6 h-6" />
                Visualize Your Garden
              </h2>
              
              {generatedImage ? (
                <div className="space-y-4">
                  <div className="relative rounded-lg overflow-hidden border-2 border-green-500">
                    <img 
                      src={generatedImage} 
                      alt="Generated landscape design"
                      className="w-full h-auto"
                    />
                    <div className="absolute top-4 right-4 bg-green-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
                      {selectedPlants.size} plants
                    </div>
                  </div>
                  <button
                    onClick={generateLandscapeImage}
                    disabled={generatingImage || selectedPlants.size === 0}
                    className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {generatingImage ? (
                      <>Regenerating Image...</>
                    ) : (
                      <>
                        <Sprout className="w-5 h-5" />
                        Regenerate with Selected Plants
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-gray-300">
                    Generate a landscape design visualization showing your selected plants arranged in your yard.
                  </p>
                  <button
                    onClick={generateLandscapeImage}
                    disabled={generatingImage || selectedPlants.size === 0}
                    className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {generatingImage ? (
                      <>Generating Image...</>
                    ) : (
                      <>
                        <Sprout className="w-5 h-5" />
                        Generate Landscape Design ({selectedPlants.size} plants)
                      </>
                    )}
                  </button>
                  {selectedPlants.size === 0 && (
                    <p className="text-sm text-red-400 text-center">
                      Select at least one plant to generate an image
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Timeline */}
            <div className="bg-gray-800 rounded-lg shadow-2xl p-6 border border-gray-700">
              <h2 className="text-2xl font-bold text-green-400 mb-4 flex items-center gap-2">
                <Calendar className="w-6 h-6" />
                Your Care Timeline
              </h2>
              
              <div className="space-y-4">
                {recommendations.timeline.map((item, idx) => (
                  <div key={idx} className="border-l-4 border-green-500 pl-4">
                    <h3 className="font-bold text-lg text-gray-200">{item.month}</h3>
                    <ul className="list-disc list-inside text-gray-300">
                      {item.tasks.map((task, tidx) => (
                        <li key={tidx}>{task}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={() => {
                  setStep(1);
                  setRecommendations(null);
                  setSelectedPlants(new Set());
                  setGeneratedImage(null);
                }}
                className="flex-1 bg-gray-700 text-gray-200 py-3 rounded-lg font-semibold hover:bg-gray-600 transition-colors border border-gray-600"
              >
                Start Over
              </button>
              <button
                onClick={() => window.print()}
                className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
              >
                Print Garden Plan
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}