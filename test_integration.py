#!/usr/bin/env python3
"""
Integration test script for Smart Garden Planner.
Tests complete user flow with Docker setup.
"""
import asyncio
import json
import os
import sys
import time
from typing import Dict, Any, List
import httpx
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrationTester:
    """Integration test runner for Smart Garden Planner."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the integration tester."""
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.test_results = []
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    def log_test_result(self, test_name: str, success: bool, message: str, duration: float = 0):
        """Log test result."""
        status = "PASS" if success else "FAIL"
        logger.info(f"[{status}] {test_name}: {message} ({duration:.2f}s)")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        })
    
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
    
    async def test_health_endpoints(self) -> bool:
        """Test basic health endpoints."""
        start_time = time.time()
        
        try:
            # Test root endpoint
            response = await self.client.get(f"{self.base_url}/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "status" in data
            
            # Test health endpoint
            response = await self.client.get(f"{self.base_url}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            
            # Test recommendations health endpoint
            response = await self.client.get(f"{self.base_url}/api/recommendations/health")
            assert response.status_code == 200
            data = response.json()
            assert "service" in data
            assert "llm_service_configured" in data
            
            duration = time.time() - start_time
            self.log_test_result("Health Endpoints", True, "All health endpoints responding correctly", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Health Endpoints", False, f"Health check failed: {e}", duration)
            return False
    
    async def test_valid_recommendation_request(self, location: str, direction: str, 
                                              water: str, maintenance: str, garden_type: str) -> Dict[str, Any]:
        """Test a valid recommendation request."""
        start_time = time.time()
        test_name = f"Valid Request ({location})"
        
        try:
            request_data = {
                "location": location,
                "direction": direction,
                "water": water,
                "maintenance": maintenance,
                "garden_type": garden_type
            }
            
            logger.info(f"Testing recommendation request for {location}")
            
            response = await self.client.post(
                f"{self.base_url}/api/recommendations",
                json=request_data
            )
            
            # Check response status
            if response.status_code != 200:
                error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                raise Exception(f"HTTP {response.status_code}: {error_detail}")
            
            # Parse response
            data = response.json()
            
            # Validate response structure
            assert "location" in data, "Missing location in response"
            assert "season" in data, "Missing season in response"
            assert "plants" in data, "Missing plants in response"
            assert "generated_by" in data, "Missing generated_by in response"
            
            # Validate plants
            plants = data["plants"]
            assert isinstance(plants, list), "Plants should be a list"
            assert len(plants) >= 1, "Should have at least 1 plant recommendation"
            assert len(plants) <= 10, "Should have at most 10 plant recommendations"
            
            # Validate each plant
            for i, plant in enumerate(plants):
                assert "name" in plant, f"Plant {i} missing name"
                assert "scientific" in plant, f"Plant {i} missing scientific name"
                assert "sun" in plant, f"Plant {i} missing sun requirements"
                assert "water" in plant, f"Plant {i} missing water requirements"
                assert "maintenance" in plant, f"Plant {i} missing maintenance level"
                assert "plant_now" in plant, f"Plant {i} missing plant_now flag"
                assert "care_instructions" in plant, f"Plant {i} missing care instructions"
                assert "notes" in plant, f"Plant {i} missing notes"
                
                # Validate enum values
                assert plant["sun"] in ["Full Sun", "Partial Sun", "Partial Shade", "Shade"], f"Invalid sun value for plant {i}"
                assert plant["water"] in ["Low", "Medium", "High"], f"Invalid water value for plant {i}"
                assert plant["maintenance"] in ["Low", "Medium", "High"], f"Invalid maintenance value for plant {i}"
                assert isinstance(plant["plant_now"], bool), f"plant_now should be boolean for plant {i}"
            
            duration = time.time() - start_time
            self.log_test_result(test_name, True, f"Generated {len(plants)} valid plant recommendations", duration)
            return data
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, f"Request failed: {e}", duration)
            return {}
    
    async def test_invalid_requests(self) -> bool:
        """Test various invalid request scenarios."""
        start_time = time.time()
        
        invalid_requests = [
            # Missing required fields
            ({}, "Missing required fields"),
            ({"location": "Denver, CO"}, "Missing direction, water, maintenance, garden_type"),
            ({"location": "", "direction": "S", "water": "Low", "maintenance": "Low", "garden_type": "Native Plants"}, "Empty location"),
            
            # Invalid enum values
            ({"location": "Denver, CO", "direction": "INVALID", "water": "Low", "maintenance": "Low", "garden_type": "Native Plants"}, "Invalid direction"),
            ({"location": "Denver, CO", "direction": "S", "water": "INVALID", "maintenance": "Low", "garden_type": "Native Plants"}, "Invalid water level"),
            ({"location": "Denver, CO", "direction": "S", "water": "Low", "maintenance": "INVALID", "garden_type": "Native Plants"}, "Invalid maintenance level"),
            ({"location": "Denver, CO", "direction": "S", "water": "Low", "maintenance": "Low", "garden_type": "INVALID"}, "Invalid garden type"),
        ]
        
        all_passed = True
        
        for request_data, description in invalid_requests:
            try:
                response = await self.client.post(
                    f"{self.base_url}/api/recommendations",
                    json=request_data
                )
                
                # Should return 4xx error
                if response.status_code < 400 or response.status_code >= 500:
                    logger.error(f"Expected 4xx error for {description}, got {response.status_code}")
                    all_passed = False
                else:
                    logger.info(f"✓ Correctly rejected: {description} (HTTP {response.status_code})")
                    
            except Exception as e:
                logger.error(f"Unexpected error testing {description}: {e}")
                all_passed = False
        
        duration = time.time() - start_time
        self.log_test_result("Invalid Requests", all_passed, "Validation of invalid request handling", duration)
        return all_passed
    
    async def test_llm_service_error_handling(self) -> bool:
        """Test error handling when LLM service fails."""
        start_time = time.time()
        
        try:
            # Check if LLM service is configured
            health_response = await self.client.get(f"{self.base_url}/api/recommendations/health")
            health_data = health_response.json()
            
            if not health_data.get("llm_service_configured", False):
                # LLM service not configured - test that we get appropriate error
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
                
                # Should return 503 Service Unavailable
                assert response.status_code == 503, f"Expected 503, got {response.status_code}"
                
                error_data = response.json()
                assert "detail" in error_data, "Missing error detail"
                detail = error_data["detail"]
                assert "error" in detail, "Missing error code"
                assert "message" in detail, "Missing error message"
                assert detail["retry_suggested"] == False, "Should not suggest retry for configuration error"
                
                duration = time.time() - start_time
                self.log_test_result("LLM Error Handling", True, "Correctly handled unconfigured LLM service", duration)
                return True
            else:
                # LLM service is configured - we can't easily test failure scenarios
                # without breaking the service, so we'll just log this
                duration = time.time() - start_time
                self.log_test_result("LLM Error Handling", True, "LLM service configured - skipping error simulation", duration)
                return True
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("LLM Error Handling", False, f"Error testing LLM error handling: {e}", duration)
            return False
    
    async def test_plant_selection_scenarios(self) -> bool:
        """Test various plant selection scenarios to ensure diverse recommendations."""
        start_time = time.time()
        
        scenarios = [
            # Different locations
            ("Denver, CO", "S", "Low", "Low", "Native Plants", "Denver native plants"),
            ("Austin, TX", "S", "Medium", "Medium", "Flower Garden", "Austin flower garden"),
            ("Portland, OR", "N", "High", "High", "Vegetable Garden", "Portland vegetable garden"),
            ("Phoenix, AZ", "S", "Low", "Low", "Native Plants", "Phoenix desert plants"),
            ("Seattle, WA", "E", "High", "Medium", "Mixed Garden", "Seattle mixed garden"),
            
            # Different preferences
            ("San Francisco, CA", "W", "Low", "Low", "Native Plants", "Low water/maintenance"),
            ("San Francisco, CA", "W", "High", "High", "Flower Garden", "High water/maintenance"),
            
            # Different directions
            ("Chicago, IL", "N", "Medium", "Medium", "Native Plants", "North-facing shade"),
            ("Chicago, IL", "S", "Medium", "Medium", "Native Plants", "South-facing sun"),
        ]
        
        all_passed = True
        successful_requests = 0
        
        for location, direction, water, maintenance, garden_type, description in scenarios:
            try:
                result = await self.test_valid_recommendation_request(
                    location, direction, water, maintenance, garden_type
                )
                
                if result:  # Non-empty result means success
                    successful_requests += 1
                    
                    # Log some details about the recommendations
                    plants = result.get("plants", [])
                    plant_names = [p.get("name", "Unknown") for p in plants]
                    logger.info(f"  → {description}: {len(plants)} plants - {', '.join(plant_names[:3])}{'...' if len(plants) > 3 else ''}")
                else:
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"Failed scenario {description}: {e}")
                all_passed = False
        
        duration = time.time() - start_time
        success_rate = successful_requests / len(scenarios) if scenarios else 0
        self.log_test_result("Plant Selection Scenarios", all_passed, 
                           f"Tested {len(scenarios)} scenarios, {successful_requests} successful ({success_rate:.1%})", duration)
        return all_passed
    
    async def run_all_tests(self) -> bool:
        """Run all integration tests."""
        logger.info("Starting Smart Garden Planner Integration Tests")
        logger.info("=" * 60)
        
        # Wait for service to be available
        if not await self.wait_for_service():
            logger.error("Service is not available - cannot run tests")
            return False
        
        # Run all test suites
        test_results = []
        
        test_results.append(await self.test_health_endpoints())
        test_results.append(await self.test_invalid_requests())
        test_results.append(await self.test_llm_service_error_handling())
        test_results.append(await self.test_plant_selection_scenarios())
        
        # Summary
        logger.info("=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "PASS" if result["success"] else "FAIL"
            logger.info(f"[{status}] {result['test']}: {result['message']}")
        
        logger.info("=" * 60)
        logger.info(f"OVERALL RESULT: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 ALL TESTS PASSED!")
            return True
        else:
            logger.error(f"❌ {total - passed} tests failed")
            return False
    
    def save_test_report(self, filename: str = "integration_test_report.json"):
        """Save test results to a JSON file."""
        report = {
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
    
    async with IntegrationTester(base_url) as tester:
        success = await tester.run_all_tests()
        tester.save_test_report()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())