// Multi-step form wizard for easier date planning
import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  MapPinIcon,
  ClockIcon,
  CurrencyDollarIcon,
  SparklesIcon,
  HeartIcon,
  UserGroupIcon,
  CalendarIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { DateRequest, EventType, Vibe, LocationType, TimePreference, SpecificDate } from '../types/index.ts';
import { useGeolocation } from '../hooks/useGeolocation.ts';

interface FormWizardProps {
  onSubmit: (request: DateRequest) => void;
  loading: boolean;
}

interface WizardStep {
  id: number;
  title: string;
  subtitle: string;
  icon: React.ComponentType<any>;
  fields: string[];
}

const WIZARD_STEPS: WizardStep[] = [
  {
    id: 1,
    title: "What's the Occasion?",
    subtitle: "Let's start with the basics",
    icon: HeartIcon,
    fields: ['event_type', 'time_preference', 'specific_dates']
  },
  {
    id: 2,
    title: "Time & Budget",
    subtitle: "How much time and money do you have?",
    icon: ClockIcon,
    fields: ['time_available', 'budget']
  },
  {
    id: 3,
    title: "Set the Mood",
    subtitle: "What vibe are you going for?",
    icon: SparklesIcon,
    fields: ['vibes', 'physical_activity', 'location_types']
  },
  {
    id: 4,
    title: "Where & Who",
    subtitle: "Location and participant details",
    icon: MapPinIcon,
    fields: ['location', 'participant_likes', 'participant_dislikes', 'participant_hobbies']
  },
  {
    id: 5,
    title: "Final Touches",
    subtitle: "Any special requests?",
    icon: CheckCircleIcon,
    fields: ['user_preferences', 'additional_info']
  }
];

const FormWizard: React.FC<FormWizardProps> = ({ onSubmit, loading }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<DateRequest>(() => {
    // Try to load saved form data from localStorage
    const saved = localStorage.getItem('dateFormProgress');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error('Failed to parse saved form data');
      }
    }
    
    return {
      event_type: EventType.CASUAL_DATING,
      time_available: 4,
      budget: 100,
      physical_activity: 5,
      vibes: [Vibe.FUN, Vibe.RELAXED],
      location_types: [LocationType.INDOORS, LocationType.OUTDOORS],
      location: '',
      time_preference: TimePreference.ANYTIME,
      specific_dates: [],
      participant_likes: '',
      participant_dislikes: '',
      participant_hobbies: '',
      participant_personality: '',
      user_preferences: '',
      additional_info: '',
    };
  });

  const [showSpecificDates, setShowSpecificDates] = useState(false);
  const [specificDates, setSpecificDates] = useState<SpecificDate[]>([
    { date: '', time: '' },
    { date: '', time: '' },
    { date: '', time: '' },
  ]);

  const { getCurrentLocation, getLocationString, loading: locationLoading } = useGeolocation();

  // Auto-save form progress
  useEffect(() => {
    localStorage.setItem('dateFormProgress', JSON.stringify(formData));
  }, [formData]);

  const handleInputChange = useCallback((field: keyof DateRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  }, []);

  const handleVibeToggle = useCallback((vibe: Vibe) => {
    setFormData(prev => ({
      ...prev,
      vibes: prev.vibes.includes(vibe)
        ? prev.vibes.filter(v => v !== vibe)
        : [...prev.vibes, vibe]
    }));
  }, []);

  const handleLocationTypeToggle = useCallback((locType: LocationType) => {
    setFormData(prev => ({
      ...prev,
      location_types: prev.location_types.includes(locType)
        ? prev.location_types.filter(l => l !== locType)
        : [...prev.location_types, locType]
    }));
  }, []);

  const handleGetLocation = useCallback(async () => {
    const coords = await getCurrentLocation();
    if (coords) {
      const locationStr = await getLocationString(coords.latitude, coords.longitude);
      handleInputChange('location', locationStr);
    }
  }, [getCurrentLocation, getLocationString, handleInputChange]);

  const nextStep = useCallback(() => {
    if (currentStep < WIZARD_STEPS.length) {
      setCurrentStep(prev => prev + 1);
    }
  }, [currentStep]);

  const prevStep = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
    }
  }, [currentStep]);

  const handleSubmit = useCallback(() => {
    // Add specific dates if selected
    if (formData.time_preference === TimePreference.SPECIFIC_DATES) {
      const validDates = specificDates.filter(sd => sd.date && sd.time);
      handleInputChange('specific_dates', validDates);
    }
    
    onSubmit(formData);
    // Clear saved progress after submission
    localStorage.removeItem('dateFormProgress');
  }, [formData, specificDates, onSubmit, handleInputChange]);

  const isStepValid = useCallback((step: number): boolean => {
    switch (step) {
      case 1:
        return true; // Basic selections always valid
      case 2:
        return formData.time_available > 0 && formData.budget > 0;
      case 3:
        return formData.vibes.length > 0 && formData.location_types.length > 0;
      case 4:
        return formData.location.length > 0;
      case 5:
        return true; // Optional fields
      default:
        return false;
    }
  }, [formData]);

  const currentStepData = WIZARD_STEPS[currentStep - 1];
  const StepIcon = currentStepData.icon;

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        className="bg-white rounded-2xl shadow-xl overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {/* Progress Bar */}
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <StepIcon className="w-8 h-8 text-white mr-3" />
              <div>
                <h2 className="text-2xl font-bold text-white">{currentStepData.title}</h2>
                <p className="text-indigo-100">{currentStepData.subtitle}</p>
              </div>
            </div>
            <div className="text-white text-sm font-medium">
              Step {currentStep} of {WIZARD_STEPS.length}
            </div>
          </div>
          
          {/* Step Indicators */}
          <div className="flex space-x-2">
            {WIZARD_STEPS.map((step) => (
              <div
                key={step.id}
                className={`flex-1 h-2 rounded-full transition-all ${
                  step.id <= currentStep ? 'bg-white' : 'bg-white/30'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Form Content */}
        <div className="p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              {/* Step 1: Event Type & Time */}
              {currentStep === 1 && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Event Type
                    </label>
                    <select
                      value={formData.event_type}
                      onChange={(e) => handleInputChange('event_type', e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      {Object.values(EventType).map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      When would you like to go?
                    </label>
                    <select
                      value={formData.time_preference}
                      onChange={(e) => {
                        handleInputChange('time_preference', e.target.value);
                        setShowSpecificDates(e.target.value === TimePreference.SPECIFIC_DATES);
                      }}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    >
                      {Object.values(TimePreference).map(pref => (
                        <option key={pref} value={pref}>{pref}</option>
                      ))}
                    </select>
                  </div>

                  {showSpecificDates && (
                    <div className="space-y-3 p-4 bg-indigo-50 rounded-lg">
                      <p className="text-sm font-medium text-gray-700">Enter up to 3 date/time options:</p>
                      {specificDates.map((sd, index) => (
                        <div key={index} className="flex space-x-2">
                          <input
                            type="text"
                            placeholder="e.g., Friday, April 19"
                            value={sd.date}
                            onChange={(e) => {
                              const newDates = [...specificDates];
                              newDates[index].date = e.target.value;
                              setSpecificDates(newDates);
                            }}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                          />
                          <input
                            type="text"
                            placeholder="e.g., 7 PM"
                            value={sd.time}
                            onChange={(e) => {
                              const newDates = [...specificDates];
                              newDates[index].time = e.target.value;
                              setSpecificDates(newDates);
                            }}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                          />
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}

              {/* Step 2: Time & Budget */}
              {currentStep === 2 && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      How much time do you have?
                    </label>
                    <div className="flex items-center space-x-4">
                      <input
                        type="range"
                        min="1"
                        max="12"
                        value={formData.time_available}
                        onChange={(e) => handleInputChange('time_available', parseInt(e.target.value))}
                        className="flex-1"
                      />
                      <div className="w-20 text-center">
                        <span className="text-2xl font-bold text-indigo-600">{formData.time_available}</span>
                        <span className="text-sm text-gray-600 block">hours</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Budget
                    </label>
                    <div className="flex items-center space-x-4">
                      <input
                        type="range"
                        min="0"
                        max="500"
                        step="10"
                        value={formData.budget}
                        onChange={(e) => handleInputChange('budget', parseInt(e.target.value))}
                        className="flex-1"
                      />
                      <div className="w-24 text-center">
                        <span className="text-2xl font-bold text-green-600">${formData.budget}</span>
                      </div>
                    </div>
                    {/* Budget suggestions */}
                    <div className="mt-3 flex flex-wrap gap-2">
                      {[0, 50, 100, 200, 300].map(amount => (
                        <button
                          key={amount}
                          onClick={() => handleInputChange('budget', amount)}
                          className={`px-3 py-1 rounded-full text-sm ${
                            formData.budget === amount
                              ? 'bg-indigo-600 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          ${amount}
                        </button>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {/* Step 3: Vibes & Activity */}
              {currentStep === 3 && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      What vibes are you going for? (Select multiple)
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {Object.values(Vibe).map(vibe => (
                        <button
                          key={vibe}
                          onClick={() => handleVibeToggle(vibe)}
                          className={`px-4 py-2 rounded-lg font-medium transition-all ${
                            formData.vibes.includes(vibe)
                              ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg scale-105'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {vibe}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Physical Activity Level
                    </label>
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-600">Low</span>
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={formData.physical_activity}
                        onChange={(e) => handleInputChange('physical_activity', parseInt(e.target.value))}
                        className="flex-1"
                      />
                      <span className="text-sm text-gray-600">High</span>
                      <div className="w-12 text-center">
                        <span className="text-xl font-bold text-indigo-600">{formData.physical_activity}</span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Location Types (Select multiple)
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {Object.values(LocationType).map(locType => (
                        <button
                          key={locType}
                          onClick={() => handleLocationTypeToggle(locType)}
                          className={`px-4 py-2 rounded-lg font-medium transition-all ${
                            formData.location_types.includes(locType)
                              ? 'bg-gradient-to-r from-green-500 to-teal-600 text-white shadow-lg scale-105'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {locType}
                        </button>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {/* Step 4: Location & Participants */}
              {currentStep === 4 && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Where are you located?
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={formData.location}
                        onChange={(e) => handleInputChange('location', e.target.value)}
                        placeholder="Enter city or address"
                        className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      />
                      <button
                        onClick={handleGetLocation}
                        disabled={locationLoading}
                        className="px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:bg-gray-400"
                      >
                        {locationLoading ? (
                          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <MapPinIcon className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      What do they like?
                    </label>
                    <textarea
                      value={formData.participant_likes}
                      onChange={(e) => handleInputChange('participant_likes', e.target.value)}
                      placeholder="e.g., Italian food, live music, art..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      rows={2}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      What should we avoid?
                    </label>
                    <textarea
                      value={formData.participant_dislikes}
                      onChange={(e) => handleInputChange('participant_dislikes', e.target.value)}
                      placeholder="e.g., crowded places, spicy food..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      rows={2}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Hobbies & Interests
                    </label>
                    <textarea
                      value={formData.participant_hobbies}
                      onChange={(e) => handleInputChange('participant_hobbies', e.target.value)}
                      placeholder="e.g., photography, hiking, cooking..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      rows={2}
                    />
                  </div>
                </>
              )}

              {/* Step 5: Final Details */}
              {currentStep === 5 && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Your preferences
                    </label>
                    <textarea
                      value={formData.user_preferences}
                      onChange={(e) => handleInputChange('user_preferences', e.target.value)}
                      placeholder="What would make this perfect for you?"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      rows={3}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Anything else we should know?
                    </label>
                    <textarea
                      value={formData.additional_info}
                      onChange={(e) => handleInputChange('additional_info', e.target.value)}
                      placeholder="Special occasions, accessibility needs, dietary restrictions..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      rows={3}
                    />
                  </div>

                  {/* Summary of selections */}
                  <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg">
                    <h3 className="font-semibold text-gray-900 mb-3">Your Date Summary</h3>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-gray-600">Event:</span>
                        <span className="ml-2 font-medium">{formData.event_type}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Time:</span>
                        <span className="ml-2 font-medium">{formData.time_available} hours</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Budget:</span>
                        <span className="ml-2 font-medium">${formData.budget}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Location:</span>
                        <span className="ml-2 font-medium">{formData.location || 'Not set'}</span>
                      </div>
                      <div className="col-span-2">
                        <span className="text-gray-600">Vibes:</span>
                        <span className="ml-2 font-medium">{formData.vibes.join(', ')}</span>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </motion.div>
          </AnimatePresence>

          {/* Navigation Buttons */}
          <div className="flex justify-between items-center mt-8">
            <button
              onClick={prevStep}
              disabled={currentStep === 1}
              className={`flex items-center px-6 py-3 rounded-lg font-medium transition-all ${
                currentStep === 1
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <ChevronLeftIcon className="w-5 h-5 mr-2" />
              Previous
            </button>

            {/* Step counter */}
            <div className="flex space-x-1">
              {WIZARD_STEPS.map((step) => (
                <button
                  key={step.id}
                  onClick={() => setCurrentStep(step.id)}
                  className={`w-8 h-8 rounded-full font-medium text-sm transition-all ${
                    step.id === currentStep
                      ? 'bg-indigo-600 text-white'
                      : step.id < currentStep
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {step.id < currentStep ? '✓' : step.id}
                </button>
              ))}
            </div>

            {currentStep < WIZARD_STEPS.length ? (
              <button
                onClick={nextStep}
                disabled={!isStepValid(currentStep)}
                className={`flex items-center px-6 py-3 rounded-lg font-medium transition-all ${
                  isStepValid(currentStep)
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-lg transform hover:scale-105'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                Next
                <ChevronRightIcon className="w-5 h-5 ml-2" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={loading || !isStepValid(currentStep)}
                className={`flex items-center px-6 py-3 rounded-lg font-medium transition-all ${
                  !loading && isStepValid(currentStep)
                    ? 'bg-gradient-to-r from-green-600 to-teal-600 text-white hover:shadow-lg transform hover:scale-105'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Generating...
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-5 h-5 mr-2" />
                    Generate My Perfect Date
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default FormWizard;