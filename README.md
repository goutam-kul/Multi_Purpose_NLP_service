# NLP Services API

## Project Overview
A comprehensive Natural Language Processing (NLP) service that provides multiple text analysis capabilities through a RESTful API interface. The service uses state-of-the-art language models including Llama3.2 and TinyLlama for various NLP tasks.

## Features Implemented

### 1. Sentiment Analysis
- Implementation: Using Ollama with llama3.2:3b model
- Endpoint: POST /analyze (task="sentiment_analysis")
- Features:
  - Sentiment classification (POSITIVE/NEGATIVE/NEUTRAL)
  - Confidence scores
  - Explanatory text

### 2. Named Entity Recognition (NER)
- Implementation: Fine-tuned TinyLlama model
- Endpoint: POST /analyze (task="ner")
- Features:
  - Entity detection and classification
  - Support for PERSON, ORGANIZATION, LOCATION, MISCELLANEOUS
  - Position tracking in text

### 3. Text Summarization
- Implementation: Using Ollama with llama3.2:3b model
- Endpoint: POST /summarize
- Features:
  - Abstractive and extractive summarization
  - Configurable summary length
  - Compression ratio calculation
  - Key points extraction

### 4. Text Classification
- Implementation: Using Ollama with llama3.2:3b model
- Endpoint: POST /classify
- Features:
  - Multi-label classification
  - Confidence scores for each category
  - Support for custom categories
  - Balanced category distribution

## To Be Implemented

### 1. Caching Layer
- Implement caching for all services
- Consider Redis or local TTLCache
- Cache invalidation strategy
- Monitoring cache hits/misses

### 2. Error Handling & Logging
- Comprehensive error handling
- Logging system implementation
- Service health monitoring
- Input validation improvements

### 3. Testing
- Unit tests for each service
- Integration tests
- Performance testing
- Edge case handling

### 4. Documentation
- OpenAPI/Swagger documentation
- API usage examples
- Request/Response formats
- Configuration guide

### 5. Performance Optimization
- Batch processing capability
- Response time optimization
- Resource usage monitoring
- Load handling improvements

### 6. Deployment
- Containerization (Docker)
- Environment configuration
- Deployment scripts
- Scaling strategy

## Setup and Installation
[To be added]

## API Documentation
[To be added]

## Dependencies
- FastAPI
- Pydantic
- Ollama Client
- Transformers
- TinyLlama
- PEFT

## Known Issues
1. Extreme confidence splits in classification (being addressed)
2. No caching mechanism currently
3. Limited error handling
4. No batch processing support

## Contributing
[To be added]

## License
[To be added]