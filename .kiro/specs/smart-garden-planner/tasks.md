# Implementation Plan

- [x] 1. Set up project structure and Docker configuration
  - Create Dockerfile for containerized deployment
  - Create docker-compose.yml for local development
  - Set up basic FastAPI project structure with main.py
  - Create requirements.txt with minimal dependencies
  - _Requirements: 1.1, 3.1_

- [-] 2. Implement data models and validation
  - [x] 2.1 Create Pydantic models for API requests and responses
    - Define RecommendationRequest model with location, direction, water, maintenance, garden_type
    - Define Plant and RecommendationResponse models for LLM output
    - Add validation for required fields and enum values
    - _Requirements: 1.1, 2.1, 2.2, 2.3, 3.2_

  - [x] 2.2 Set up SQLite database and Digital Ocean Object Storage
    - Create simple SQLite schema for logging user requests and responses
    - Implement basic database connection and models using SQLAlchemy
    - Set up Digital Ocean Spaces client for object storage
    - Add optional request/response logging with storage backup
    - _Requirements: 3.1_

- [x] 3. Implement LLM recommendation service
  - [x] 3.1 Create Digital Ocean LLM service interface
    - Implement Digital Ocean LLM API client with httpx
    - Create structured prompt template for plant recommendations
    - Add timeout and error handling for LLM requests
    - _Requirements: 3.1, 3.2, 3.5_

  - [x] 3.2 Create recommendations API endpoint
    - Implement POST /api/recommendations route
    - Process user input and create LLM prompt with location and preferences
    - Parse LLM JSON response and validate against Plant model
    - Add error handling for malformed LLM responses
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 3.1, 3.2, 3.4, 4.1, 4.2, 4.3, 4.4_

- [x] 4. Update React frontend integration
  - [x] 4.1 Replace mock API calls with real endpoint
    - Update form submission to call /api/recommendations directly
    - Remove mock data and use actual LLM-generated responses
    - Handle text-based location input (no geocoding needed)
    - _Requirements: 1.1, 1.3, 3.1_

  - [x] 4.2 Add proper error handling and loading states
    - Handle LLM API errors with user-friendly messages
    - Show loading spinners during LLM processing
    - Implement retry logic for failed LLM requests
    - _Requirements: 3.5_

  - [x] 4.3 Update plant selection and display logic
    - Ensure plant checkboxes work with LLM response data structure
    - Update plant card display to match LLM response format
    - Implement selection count tracking and summary display
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4_

- [x] 5. Environment setup and configuration
  - [x] 5.1 Create environment configuration
    - Set up .env file with Digital Ocean LLM API key and endpoint
    - Add Digital Ocean Spaces credentials and configuration
    - Create config.py for environment variable management
    - Add Docker environment variables configuration
    - _Requirements: 1.1, 3.1_

  - [x] 5.2 Create Docker setup and documentation
    - Write Dockerfile with Python FastAPI setup
    - Create docker-compose.yml with SQLite volume mounting and DO Spaces integration
    - Configure Digital Ocean Object Storage service in composition
    - Write README with Docker setup and run instructions
    - Add example .env file with DO LLM and Spaces placeholder values
    - _Requirements: All_

- [ ] 6. Integration testing and demo preparation
  - [ ] 6.1 Test complete user flow with Docker
    - Test location input and LLM recommendation generation
    - Verify plant selection and display functionality
    - Test error handling when LLM service fails
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4_

  - [ ] 6.2 Prepare demo scenarios
    - Test with various locations (Denver, Austin, Portland, etc.)
    - Verify different preference combinations work with LLM
    - Prepare demo script with reliable test cases
    - _Requirements: 3.5_