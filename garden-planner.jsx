import React, { useState } from 'react';
import { Leaf, MapPin, Droplets, Sun, Calendar, Sprout, Loader2 } from 'lucide-react';

export default function GardenPlanner() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    location: '',
    direction: '',
    maintenance: '',
    water: '',
    garden_type: '',
    photo: null
  });
  const [recommendations, setRecommendations] = useState(null);
  const [selectedPlants, setSelectedPlants] = useState(new Set());
  const [generatedImage, setGeneratedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generatingImage, setGeneratingImage] = useState(false);

  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const handleSubmit = async (e, isRetry = false) => {
    e?.preventDefault();
    setLoading(true);
    setError(null);
    
    if (!isRetry) {
      setRetryCount(0);
    }
    
    try {
      const requestData = {
        location: formData.location,
        direction: formData.direction,
        water: formData.water,
        maintenance: formData.maintenance,
        garden_type: formData.garden_type
      };

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const response = await fetch('/api/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json();
        const errorDetail = errorData.detail || {};
        
        // Create a more user-friendly error message
        let userMessage = 'Unable to generate plant recommendations. ';
        
        if (response.status === 503) {
          userMessage += 'The recommendation service is currently unavailable.';
        } else if (response.status === 429) {
          userMessage += 'Too many requests. Please wait a moment and try again.';
        } else if (response.status === 504) {
          userMessage += 'The request timed out. Please try again.';
        } else {
          userMessage += errorDetail.message || 'Please try again.';
        }
        
        const error = new Error(userMessage);
        error.retryable = errorDetail.retry_suggested !== false;
        error.statusCode = response.status;
        throw error;
      }

      const data = await response.json();
      setRecommendations(data);
      
      // Initialize all plants as selected
      const allPlantNames = data.plants.map(p => p.name);
      setSelectedPlants(new Set(allPlantNames));
      setRetryCount(0); // Reset retry count on success
      setStep(3);
    } catch (err) {
      console.error('Error getting recommendations:', err);
      
      if (err.name === 'AbortError') {
        setError('Request timed out. Please check your connection and try again.');
      } else {
        setError(err.message);
      }
      
      // Set retry count for display
      if (isRetry) {
        setRetryCount(prev => prev + 1);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    handleSubmit(null, true);
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
                  value={formData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
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
                disabled={!formData.location || !formData.direction}
                className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed"
              >
                Continue to Preferences
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Preferences */}
        {step === 2 && (
          <div className="bg-gray-800 rounded-lg shadow-2xl p-8 border border-gray-700 relative">
            <h2 className="text-2xl font-bold text-green-400 mb-6">
              What are your gardening preferences?
            </h2>
            
            {error && (
              <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 mb-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-red-300 font-semibold mb-2">Unable to get recommendations</p>
                    <p className="text-red-200 mb-3">{error}</p>
                    {retryCount > 0 && (
                      <p className="text-red-400 text-sm">Retry attempt: {retryCount}</p>
                    )}
                  </div>
                </div>
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={handleRetry}
                    disabled={loading}
                    className="bg-red-700 hover:bg-red-600 disabled:bg-red-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-semibold transition-colors"
                  >
                    {loading ? 'Retrying...' : 'Try Again'}
                  </button>
                  <button
                    onClick={() => setError(null)}
                    className="bg-gray-700 hover:bg-gray-600 text-gray-200 px-4 py-2 rounded-lg font-semibold transition-colors"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            )}
            
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
                  {['Native Plants', 'Flower Garden', 'Vegetable Garden', 'Mixed Garden'].map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => handleInputChange('garden_type', type)}
                      className={`py-3 px-4 rounded-lg font-semibold transition-colors ${
                        formData.garden_type === type
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
                  disabled={!formData.water || !formData.maintenance || !formData.garden_type || loading}
                  className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading && <Loader2 className="w-5 h-5 animate-spin" />}
                  {loading ? 'Generating Plan...' : 'Get My Plant Plan'}
                </button>
              </div>
            </form>
            
            {/* Loading overlay */}
            {loading && (
              <div className="absolute inset-0 bg-gray-900/75 rounded-lg flex items-center justify-center">
                <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 text-center">
                  <Loader2 className="w-8 h-8 animate-spin text-green-400 mx-auto mb-3" />
                  <p className="text-green-300 font-semibold">Generating your personalized plant recommendations...</p>
                  <p className="text-gray-400 text-sm mt-1">This may take up to 30 seconds</p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Step 3: Results */}
        {step === 3 && recommendations && (
          <div className="space-y-6">
            {/* Location and Season Info */}
            <div className="bg-gray-800 rounded-lg shadow-2xl p-6 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-300">Location</h3>
                  <p className="text-2xl font-bold text-green-400">{recommendations.location}</p>
                </div>
                <div className="text-right">
                  <h3 className="text-lg font-semibold text-gray-300">Current Season</h3>
                  <p className="text-xl font-bold text-orange-400">{recommendations.season}</p>
                </div>
              </div>
            </div>

            {/* Selection Summary */}
            {selectedPlants.size > 0 && (
              <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-green-300">Your Garden Selection</h3>
                    <p className="text-green-200">
                      {selectedPlants.size} plant{selectedPlants.size !== 1 ? 's' : ''} selected for your {formData.garden_type.toLowerCase()} in {formData.location}
                    </p>
                    {(() => {
                      const selectedPlantObjects = recommendations.plants.filter(p => selectedPlants.has(p.name));
                      const plantNowCount = selectedPlantObjects.filter(p => p.plant_now).length;
                      return plantNowCount > 0 && (
                        <p className="text-orange-300 text-sm mt-1">
                          {plantNowCount} can be planted now
                        </p>
                      );
                    })()}
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-green-400">{selectedPlants.size}</p>
                    <p className="text-sm text-green-300">Plants</p>
                  </div>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {Array.from(selectedPlants).map(plantName => {
                    const plant = recommendations.plants.find(p => p.name === plantName);
                    return (
                      <span 
                        key={plantName} 
                        className={`px-3 py-1 rounded-full text-sm border ${
                          plant?.plant_now 
                            ? 'bg-orange-800/50 text-orange-200 border-orange-600' 
                            : 'bg-green-800/50 text-green-200 border-green-600'
                        }`}
                      >
                        {plantName}
                        {plant?.plant_now && ' ⭐'}
                      </span>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Plant Recommendations */}
            <div className="bg-gray-800 rounded-lg shadow-2xl p-6 border border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-green-400 flex items-center gap-2">
                  <Leaf className="w-6 h-6" />
                  Recommended Plants for Your Yard
                </h2>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className="text-lg font-semibold text-green-300">
                      {selectedPlants.size} of {recommendations.plants.length}
                    </span>
                    <p className="text-sm text-gray-400">selected</p>
                  </div>
                  <button
                    onClick={() => {
                      if (selectedPlants.size === recommendations.plants.length) {
                        setSelectedPlants(new Set());
                      } else {
                        setSelectedPlants(new Set(recommendations.plants.map(p => p.name)));
                      }
                    }}
                    className="bg-green-700 hover:bg-green-600 text-white px-3 py-1 rounded-lg text-sm font-semibold transition-colors"
                  >
                    {selectedPlants.size === recommendations.plants.length ? 'Deselect All' : 'Select All'}
                  </button>
                </div>
              </div>
              
              {selectedPlants.size === 0 && (
                <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4 mb-4">
                  <p className="text-yellow-300 font-semibold">No plants selected</p>
                  <p className="text-yellow-200 text-sm">Click on plant cards or checkboxes to select plants for your garden.</p>
                </div>
              )}
              
              <div className="grid gap-4">
                {recommendations.plants.map((plant, idx) => (
                  <div 
                    key={idx} 
                    className={`border-2 rounded-lg p-4 transition-all cursor-pointer hover:border-green-400 ${
                      selectedPlants.has(plant.name)
                        ? 'border-green-500 bg-gray-700/50 shadow-lg shadow-green-500/20'
                        : 'border-gray-600 bg-gray-700/20 opacity-70 hover:opacity-90'
                    }`}
                    onClick={() => togglePlant(plant.name)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-start gap-3 flex-1">
                        <input
                          type="checkbox"
                          checked={selectedPlants.has(plant.name)}
                          onChange={(e) => {
                            e.stopPropagation();
                            togglePlant(plant.name);
                          }}
                          className="mt-1 w-5 h-5 rounded border-gray-600 bg-gray-700 checked:bg-green-600 cursor-pointer"
                        />
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-green-300">{plant.name}</h3>
                          <p className="text-sm text-gray-400 italic">{plant.scientific}</p>
                        </div>
                      </div>
                      {plant.plant_now && (
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
                        <p className="text-xs text-gray-400">Care</p>
                        <p className="font-semibold text-sm text-green-300">Instructions</p>
                      </div>
                    </div>

                    <p className="text-gray-300 mb-2 ml-8">{plant.notes}</p>
                    
                    <div className="bg-emerald-900/30 p-3 rounded mt-2 ml-8 border border-emerald-700/30">
                      <p className="text-sm font-semibold text-emerald-300 mb-1">Care Instructions:</p>
                      <p className="text-sm text-emerald-400">{plant.care_instructions}</p>
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



            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={() => {
                  setStep(1);
                  setRecommendations(null);
                  setSelectedPlants(new Set());
                  setGeneratedImage(null);
                  setError(null);
                  setRetryCount(0);
                  setFormData({
                    location: '',
                    direction: '',
                    maintenance: '',
                    water: '',
                    garden_type: '',
                    photo: null
                  });
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