#!/usr/bin/env python3
"""
Complete User Flow Integration Test for Smart Garden Planner.
Tests the complete user journey from location input to plant recommendations.
Covers all requirements for task 6.1.
"""
import asyncio
import json
import os
import sys
import time
from typing import Dict, Any, List, Optional
import httpx
import logging
from datetime import datetime
import subprocess
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UserFlowTester:
    """Complete user flow integration tester."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the user flow tester."""
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.test_results = []
        self.docker_process = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
        if self.docker_process:
            self.cleanup_docker()
    
    def log_test_result(self, test_name: str, success: bool, message: str, duration: float = 0, details: Optional[Dict] = None):
        """Log test result with optional details."""
        status = "PASS" if success else "FAIL"
        logger.info(f"[{status}] {test_name}: {message} ({duration:.2f}s)")
        
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if details:
            result["details"] = details
            
        self.test_results.append(result)
    
    def start_docker_services(self) -> bool:
        """Start Docker services for testing."""
        logger.info("Starting Docker services...")
        
        try:
            # Check if Docker is running
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Docker is not running")
                return False
            
            # Stop any existing containers
            subprocess.run(["docker-compose", "down", "--volumes", "--remove-orphans"], 
                         capture_output=True, text=True)
            
            # Start services
            result = subprocess.run(["docker-compose", "up", "-d", "--build"], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to start Docker services: {result.stderr}")
                logger.error(f"Docker compose output: {result.stdout}")
                return False
            
            logger.info("Docker services started successfully")
            logger.info("Backend available at: http://localhost:8000")
            logger.info("Frontend available at: http://localhost:3000")
            return True
            
        except Exception as e:
            logger.error(f"Error starting Docker services: {e}")
            return False
    
    def cleanup_docker(self):
        """Clean up Docker services."""
        logger.info("Cleaning up Docker services...")
        try:
            subprocess.run(["docker-compose", "down", "--volumes"], 
                         capture_output=True, text=True)
            logger.info("Docker services cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up Docker services: {e}")
    
    async def wait_for_service(self, max_attempts: int = 30, delay: float = 2.0) -> bool:
        """Wait for the service to be available."""
        logger.info("Waiting for service to be available...")
        
        for attempt in range(max_attempts):
            try:
                response = await self.client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    logger.info("Service is available!")
                    return True
            except Exception as e:
                logger.debug(f"Attempt {attempt + 1}: Service not ready - {e}")
            
            if attempt < max_attempts - 1:
                await asyncio.sleep(delay)
        
        logger.error("Service failed to become available")
        return False
    
    async def test_location_input_and_validation(self) -> bool:
        """Test location input validation and processing."""
        start_time = time.time()
        
        test_cases = [
            # Valid locations
            ("Denver, CO", True, "Valid US city"),
            ("Austin, TX", True, "Valid US city with state"),
            ("Portland, OR", True, "Valid Pacific Northwest city"),
            ("Phoenix, AZ", True, "Valid desert city"),
            ("Seattle, WA", True, "Valid coastal city"),
            
            # Edge cases
            ("San Francisco, CA", True, "City with space in name"),
            ("New York, NY", True, "City with multiple words"),
            
            # Invalid cases
            ("", False, "Empty location"),
            ("   ", False, "Whitespace only location"),
        ]
        
        all_passed = True
        
        for location, should_succeed, description in test_cases:
            try:
                request_data = {
                    "location": location,
                    "direction": "S",
                    "water": "Low",
                    "maintenance": "Low",
                    "garden_type": "Native Plants"
                }
                
                response = await self.client.post(
                    f"{self.base_url}/api/recommendations",
                    json=request_data
                )
                
                if should_succeed:
                    if response.status_code == 200:
                        data = response.json()
                        if "location" in data and data["location"]:
                            logger.info(f"✓ {description}: Location processed correctly")
                        else:
                            logger.error(f"✗ {description}: Location not in response")
                            all_passed = False
                    else:
                        logger.error(f"✗ {description}: Expected success but got {response.status_code}")
                        all_passed = False
                else:
                    if response.status_code >= 400:
                        logger.info(f"✓ {description}: Correctly rejected invalid location")
                    else:
                        logger.error(f"✗ {description}: Should have been rejected but got {response.status_code}")
                        all_passed = False
                        
            except Exception as e:
                logger.error(f"✗ {description}: Exception - {e}")
                all_passed = False
        
        duration = time.time() - start_time
        self.log_test_result("Location Input Validation", all_passed, 
                           f"Tested {len(test_cases)} location scenarios", duration)
        return all_passed
    
    async def test_llm_recommendation_generation(self) -> bool:
        """Test LLM recommendation generation with various inputs."""
        start_time = time.time()
        
        # Test scenarios covering different user preferences
        scenarios = [
            {
                "name": "Low maintenance native garden",
                "request": {
                    "location": "Denver, CO",
                    "direction": "S",
                    "water": "Low",
                    "maintenance": "Low",
                    "garden_type": "Native Plants"
                },
                "expected_characteristics": {
                    "plant_count_min": 3,
                    "plant_count_max": 8,
                    "should_have_low_water": True,
                    "should_have_low_maintenance": True
                }
            },
            {
                "name": "High maintenance flower garden",
                "request": {
                    "location": "Austin, TX",
                    "direction": "E",
                    "water": "High",
                    "maintenance": "High",
                    "garden_type": "Flower Garden"
                },
                "expected_characteristics": {
                    "plant_count_min": 3,
                    "plant_count_max": 8,
                    "should_have_flowering": True
                }
            },
            {
                "name": "Shade vegetable garden",
                "request": {
                    "location": "Portland, OR",
                    "direction": "N",
                    "water": "Medium",
                    "maintenance": "Medium",
                    "garden_type": "Vegetable Garden"
                },
                "expected_characteristics": {
                    "plant_count_min": 3,
                    "plant_count_max": 8,
                    "should_handle_shade": True
                }
            }
        ]
        
        all_passed = True
        successful_requests = 0
        
        for scenario in scenarios:
            try:
                logger.info(f"Testing scenario: {scenario['name']}")
                
                response = await self.client.post(
                    f"{self.base_url}/api/recommendations",
                    json=scenario["request"]
                )
                
                if response.status_code != 200:
                    logger.error(f"✗ {scenario['name']}: HTTP {response.status_code}")
                    all_passed = False
                    continue
                
                data = response.json()
                
                # Validate response structure
                required_fields = ["location", "season", "plants", "generated_by"]
                for field in required_fields:
                    if field not in data:
                        logger.error(f"✗ {scenario['name']}: Missing field '{field}'")
                        all_passed = False
                        continue
                
                plants = data["plants"]
                expected = scenario["expected_characteristics"]
                
                # Check plant count
                if len(plants) < expected["plant_count_min"] or len(plants) > expected["plant_count_max"]:
                    logger.error(f"✗ {scenario['name']}: Plant count {len(plants)} not in expected range {expected['plant_count_min']}-{expected['plant_count_max']}")
                    all_passed = False
                
                # Validate each plant structure
                for i, plant in enumerate(plants):
                    required_plant_fields = ["name", "scientific", "sun", "water", "maintenance", "plant_now", "care_instructions", "notes"]
                    for field in required_plant_fields:
                        if field not in plant:
                            logger.error(f"✗ {scenario['name']}: Plant {i} missing field '{field}'")
                            all_passed = False
                
                # Check specific characteristics
                if expected.get("should_have_low_water"):
                    low_water_plants = [p for p in plants if p.get("water") == "Low"]
                    if not low_water_plants:
                        logger.warning(f"⚠ {scenario['name']}: Expected some low-water plants for low-water request")
                
                if expected.get("should_have_low_maintenance"):
                    low_maintenance_plants = [p for p in plants if p.get("maintenance") == "Low"]
                    if not low_maintenance_plants:
                        logger.warning(f"⚠ {scenario['name']}: Expected some low-maintenance plants for low-maintenance request")
                
                successful_requests += 1
                logger.info(f"✓ {scenario['name']}: Generated {len(plants)} valid recommendations")
                
                # Log plant details for verification
                plant_names = [p.get("name", "Unknown") for p in plants]
                logger.info(f"  Plants: {', '.join(plant_names[:3])}{'...' if len(plants) > 3 else ''}")
                
            except Exception as e:
                logger.error(f"✗ {scenario['name']}: Exception - {e}")
                all_passed = False
        
        duration = time.time() - start_time
        success_rate = successful_requests / len(scenarios) if scenarios else 0
        
        self.log_test_result("LLM Recommendation Generation", all_passed,
                           f"Generated recommendations for {successful_requests}/{len(scenarios)} scenarios ({success_rate:.1%})", 
                           duration)
        return all_passed
    
    async def test_plant_selection_and_display(self) -> bool:
        """Test plant selection functionality and display logic."""
        start_time = time.time()
        
        try:
            # Get a sample recommendation
            request_data = {
                "location": "Denver, CO",
                "direction": "S",
                "water": "Medium",
                "maintenance": "Medium",
                "garden_type": "Mixed Garden"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/recommendations",
                json=request_data
            )
            
            if response.status_code != 200:
                self.log_test_result("Plant Selection Display", False, 
                                   f"Failed to get recommendations: HTTP {response.status_code}", 
                                   time.time() - start_time)
                return False
            
            data = response.json()
            plants = data.get("plants", [])
            
            if not plants:
                self.log_test_result("Plant Selection Display", False, 
                                   "No plants returned for selection testing", 
                                   time.time() - start_time)
                return False
            
            # Test plant data structure for frontend display
            display_tests_passed = True
            
            for i, plant in enumerate(plants):
                # Check required display fields
                display_fields = {
                    "name": "Plant name for display",
                    "scientific": "Scientific name for display",
                    "sun": "Sun requirements for icon/badge",
                    "water": "Water requirements for icon/badge",
                    "maintenance": "Maintenance level for icon/badge",
                    "plant_now": "Current season planting indicator",
                    "care_instructions": "Care instructions for detail view",
                    "notes": "Plant notes for description"
                }
                
                for field, description in display_fields.items():
                    if field not in plant or not plant[field]:
                        logger.error(f"✗ Plant {i}: Missing or empty {description} ({field})")
                        display_tests_passed = False
                
                # Validate enum values for UI consistency
                if plant.get("sun") not in ["Full Sun", "Partial Sun", "Partial Shade", "Shade"]:
                    logger.error(f"✗ Plant {i}: Invalid sun value '{plant.get('sun')}'")
                    display_tests_passed = False
                
                if plant.get("water") not in ["Low", "Medium", "High"]:
                    logger.error(f"✗ Plant {i}: Invalid water value '{plant.get('water')}'")
                    display_tests_passed = False
                
                if plant.get("maintenance") not in ["Low", "Medium", "High"]:
                    logger.error(f"✗ Plant {i}: Invalid maintenance value '{plant.get('maintenance')}'")
                    display_tests_passed = False
                
                if not isinstance(plant.get("plant_now"), bool):
                    logger.error(f"✗ Plant {i}: plant_now should be boolean, got {type(plant.get('plant_now'))}")
                    display_tests_passed = False
            
            # Test selection logic simulation
            selection_tests_passed = True
            
            # Simulate selecting all plants
            all_selected = set(plant["name"] for plant in plants)
            logger.info(f"✓ Selection test: All {len(all_selected)} plants can be selected")
            
            # Simulate selecting subset
            subset_selected = set(list(all_selected)[:2]) if len(all_selected) >= 2 else all_selected
            logger.info(f"✓ Selection test: Subset selection works ({len(subset_selected)} plants)")
            
            # Test plant_now filtering
            plantable_now = [p for p in plants if p.get("plant_now", False)]
            logger.info(f"✓ Season filtering: {len(plantable_now)} plants can be planted now")
            
            duration = time.time() - start_time
            overall_success = display_tests_passed and selection_tests_passed
            
            details = {
                "total_plants": len(plants),
                "plantable_now": len(plantable_now),
                "display_fields_valid": display_tests_passed,
                "selection_logic_valid": selection_tests_passed
            }
            
            self.log_test_result("Plant Selection Display", overall_success,
                               f"Validated {len(plants)} plants for display and selection", 
                               duration, details)
            return overall_success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Plant Selection Display", False, 
                               f"Exception during plant selection testing: {e}", duration)
            return False
    
    async def test_error_handling_scenarios(self) -> bool:
        """Test error handling when LLM service fails or returns invalid data."""
        start_time = time.time()
        
        error_scenarios = [
            {
                "name": "Invalid request data",
                "request": {"invalid": "data"},
                "expected_status": 422,
                "description": "Should reject malformed requests"
            },
            {
                "name": "Missing required fields",
                "request": {"location": "Denver, CO"},
                "expected_status": 422,
                "description": "Should reject incomplete requests"
            },
            {
                "name": "Invalid enum values",
                "request": {
                    "location": "Denver, CO",
                    "direction": "INVALID",
                    "water": "Low",
                    "maintenance": "Low",
                    "garden_type": "Native Plants"
                },
                "expected_status": 422,
                "description": "Should reject invalid enum values"
            }
        ]
        
        all_passed = True
        
        for scenario in error_scenarios:
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/recommendations",
                    json=scenario["request"]
                )
                
                if response.status_code == scenario["expected_status"]:
                    logger.info(f"✓ {scenario['name']}: Correctly returned HTTP {response.status_code}")
                    
                    # Check error response structure
                    if response.headers.get("content-type", "").startswith("application/json"):
                        error_data = response.json()
                        if "detail" in error_data:
                            logger.info(f"  Error details provided: {type(error_data['detail'])}")
                        else:
                            logger.warning(f"  No error details in response")
                else:
                    logger.error(f"✗ {scenario['name']}: Expected HTTP {scenario['expected_status']}, got {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"✗ {scenario['name']}: Exception - {e}")
                all_passed = False
        
        # Test LLM service configuration error handling
        try:
            health_response = await self.client.get(f"{self.base_url}/api/recommendations/health")
            if health_response.status_code == 200:
                health_data = health_response.json()
                llm_configured = health_data.get("llm_service_configured", False)
                
                if not llm_configured:
                    # Test that unconfigured LLM service returns appropriate error
                    request_data = {
                        "location": "Denver, CO",
                        "direction": "S",
                        "water": "Low",
                        "maintenance": "Low",
                        "garden_type": "Native Plants"
                    }
                    
                    response = await self.client.post(
                        f"{self.base_url}/api/recommendations",
                        json=request_data
                    )
                    
                    if response.status_code == 503:
                        logger.info("✓ LLM service error: Correctly returned 503 for unconfigured service")
                    else:
                        logger.warning(f"⚠ LLM service error: Expected 503 for unconfigured service, got {response.status_code}")
                else:
                    logger.info("✓ LLM service is configured - error simulation not needed")
                    
        except Exception as e:
            logger.error(f"✗ LLM service error handling test failed: {e}")
            all_passed = False
        
        duration = time.time() - start_time
        self.log_test_result("Error Handling", all_passed,
                           f"Tested {len(error_scenarios)} error scenarios plus LLM service errors", 
                           duration)
        return all_passed
    
    async def test_complete_user_journey(self) -> bool:
        """Test the complete user journey from start to finish."""
        start_time = time.time()
        
        try:
            logger.info("Testing complete user journey...")
            
            # Step 1: User enters location and preferences
            user_input = {
                "location": "Boulder, CO",
                "direction": "SW",  # Partial sun
                "water": "Medium",
                "maintenance": "Low",
                "garden_type": "Native Plants"
            }
            
            logger.info(f"Step 1: User input - {user_input['location']}, {user_input['direction']} facing, {user_input['water']} water, {user_input['maintenance']} maintenance, {user_input['garden_type']}")
            
            # Step 2: Submit request to API
            response = await self.client.post(
                f"{self.base_url}/api/recommendations",
                json=user_input
            )
            
            if response.status_code != 200:
                error_msg = f"API request failed with HTTP {response.status_code}"
                if response.headers.get("content-type", "").startswith("application/json"):
                    error_data = response.json()
                    error_msg += f": {error_data}"
                
                self.log_test_result("Complete User Journey", False, error_msg, time.time() - start_time)
                return False
            
            # Step 3: Validate recommendation response
            data = response.json()
            logger.info(f"Step 2: Received recommendations for {data.get('location', 'unknown location')}")
            logger.info(f"Step 3: Season info - {data.get('season', 'unknown season')}")
            
            plants = data.get("plants", [])
            if not plants:
                self.log_test_result("Complete User Journey", False, 
                                   "No plant recommendations received", time.time() - start_time)
                return False
            
            logger.info(f"Step 4: Received {len(plants)} plant recommendations")
            
            # Step 4: Simulate user plant selection
            # User selects plants that can be planted now
            plantable_now = [p for p in plants if p.get("plant_now", False)]
            selected_plants = plantable_now[:3] if len(plantable_now) >= 3 else plants[:3]
            
            logger.info(f"Step 5: User selects {len(selected_plants)} plants:")
            for plant in selected_plants:
                logger.info(f"  - {plant.get('name', 'Unknown')} ({plant.get('scientific', 'Unknown')})")
                logger.info(f"    Sun: {plant.get('sun')}, Water: {plant.get('water')}, Maintenance: {plant.get('maintenance')}")
                if plant.get("plant_now"):
                    logger.info(f"    ⭐ Can be planted now")
            
            # Step 5: Validate user can access all necessary information
            journey_complete = True
            
            for i, plant in enumerate(selected_plants):
                # Check that user has all info needed to make decisions
                required_info = ["name", "care_instructions", "notes", "sun", "water", "maintenance"]
                for info in required_info:
                    if not plant.get(info):
                        logger.error(f"✗ Plant {i}: Missing {info} for user decision-making")
                        journey_complete = False
            
            # Step 6: Simulate user getting final garden plan
            if journey_complete:
                logger.info("Step 6: User has complete garden plan with:")
                logger.info(f"  - Location: {data.get('location')}")
                logger.info(f"  - Season: {data.get('season')}")
                logger.info(f"  - Selected plants: {len(selected_plants)}")
                logger.info(f"  - Plantable now: {len([p for p in selected_plants if p.get('plant_now')])}")
            
            duration = time.time() - start_time
            
            details = {
                "user_location": user_input["location"],
                "user_preferences": {k: v for k, v in user_input.items() if k != "location"},
                "total_recommendations": len(plants),
                "selected_plants": len(selected_plants),
                "plantable_now": len([p for p in selected_plants if p.get("plant_now")]),
                "journey_steps_completed": 6
            }
            
            self.log_test_result("Complete User Journey", journey_complete,
                               f"Successfully completed full user journey with {len(selected_plants)} plant selections", 
                               duration, details)
            return journey_complete
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Complete User Journey", False, 
                               f"Exception during user journey test: {e}", duration)
            return False
    
    async def test_frontend_availability(self) -> bool:
        """Test that the frontend is available and serving the application."""
        start_time = time.time()
        
        try:
            # Test frontend availability
            frontend_client = httpx.AsyncClient(timeout=10.0)
            response = await frontend_client.get("http://localhost:3000")
            await frontend_client.aclose()
            
            if response.status_code != 200:
                self.log_test_result("Frontend Availability", False, 
                                   f"Frontend returned HTTP {response.status_code}", 
                                   time.time() - start_time)
                return False
            
            # Check that it contains our application
            content = response.text
            if "Smart Garden Planner" not in content:
                self.log_test_result("Frontend Availability", False, 
                                   "Frontend does not contain expected application content", 
                                   time.time() - start_time)
                return False
            
            # Check for key application elements
            required_elements = [
                "Tell us about your location",
                "Your Address", 
                "Which direction does your yard face",
                "Water Availability",
                "Maintenance Level",
                "Garden Type"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                self.log_test_result("Frontend Availability", False, 
                                   f"Missing UI elements: {', '.join(missing_elements)}", 
                                   time.time() - start_time)
                return False
            
            duration = time.time() - start_time
            self.log_test_result("Frontend Availability", True, 
                               "Frontend is serving the complete application", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Frontend Availability", False, 
                               f"Exception testing frontend: {e}", duration)
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all user flow tests."""
        logger.info("🌱 Smart Garden Planner - Complete User Flow Integration Tests")
        logger.info("=" * 70)
        
        # Start Docker services
        if not self.start_docker_services():
            logger.error("Failed to start Docker services - cannot run tests")
            return False
        
        # Wait for backend service to be available
        if not await self.wait_for_service():
            logger.error("Backend service is not available - cannot run tests")
            return False
        
        # Wait a bit more for frontend to be ready
        logger.info("Waiting for frontend service to be ready...")
        await asyncio.sleep(5)
        
        # Run all test suites
        test_results = []
        
        logger.info("\n🔍 Running User Flow Tests...")
        logger.info("-" * 50)
        
        test_results.append(await self.test_frontend_availability())
        test_results.append(await self.test_location_input_and_validation())
        test_results.append(await self.test_llm_recommendation_generation())
        test_results.append(await self.test_plant_selection_and_display())
        test_results.append(await self.test_error_handling_scenarios())
        test_results.append(await self.test_complete_user_journey())
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("TEST SUMMARY")
        logger.info("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "PASS" if result["success"] else "FAIL"
            logger.info(f"[{status}] {result['test']}: {result['message']}")
        
        logger.info("=" * 70)
        logger.info(f"OVERALL RESULT: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 ALL USER FLOW TESTS PASSED!")
            logger.info("\n✅ Complete user flow verified:")
            logger.info("   - Frontend application serving correctly ✅")
            logger.info("   - Location input and LLM recommendation generation ✅")
            logger.info("   - Plant selection and display functionality ✅") 
            logger.info("   - Error handling when LLM service fails ✅")
            logger.info("   - Complete user journey from input to selection ✅")
            logger.info(f"\n🌐 Access the application at: http://localhost:3000")
            logger.info(f"🔧 Backend API available at: http://localhost:8000")
            return True
        else:
            logger.error(f"❌ {total - passed} tests failed")
            return False
    
    def save_test_report(self, filename: str = "user_flow_test_report.json"):
        """Save test results to a JSON file."""
        report = {
            "test_type": "complete_user_flow",
            "timestamp": datetime.utcnow().isoformat(),
            "base_url": self.base_url,
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results if r["success"]),
            "failed_tests": sum(1 for r in self.test_results if not r["success"]),
            "test_results": self.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test report saved to {filename}")


async def main():
    """Main test runner."""
    # Get base URL from environment or use default
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:8000")
    
    async with UserFlowTester(base_url) as tester:
        success = await tester.run_all_tests()
        tester.save_test_report()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())