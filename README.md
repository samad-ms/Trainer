# SensAi - AI Sales Coach for Easify

SensAi is an intelligent AI-powered sales coaching platform designed specifically for Easify's marketing and communication platform. This tool helps sales representatives improve their skills and provide better customer service through real-time feedback and analysis.

## Features

### 1. Interactive Sales Simulation
- Simulates realistic customer interactions
- Generates dynamic prospect questions about Easify's products and services
- Provides immediate feedback on sales responses

### 2. Conversation Analysis
- Real-time transcription of sales calls
- Automatic labeling of speaker roles (Rep/Prospect)
- Contextual question-answering capabilities
- Intelligent conversation summarization

### 3. Product Knowledge Integration
- Deep integration with Easify's product features:
  - Bulk SMS/MMS marketing
  - AI content management
  - Geo-tagging
  - Secure calls
  - Ringless voicemail
  - Email functionality
  - Booking systems
  - Automation tools

### 4. Compliance and Integration Support
- Training on compliance requirements (10DLC, SHAKEN/STIR, CNAM)
- Knowledge of available integrations (Google Calendar, Chrome extensions)
- Pricing plan expertise

## Technical Stack

### Backend
- FastAPI framework
- OpenAI integration for AI capabilities
- LangChain for advanced language processing
- ChromaDB for vector storage
- WebSocket support for real-time communication

### Key Dependencies
- Python 3.x
- OpenAI API
- LangChain
- ChromaDB
- FastAPI
- python-dotenv for environment management

## Getting Started

1. Clone the repository
2. Set up environment variables:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
```

## Project Structure

```
├── backend/
│   ├── services/
│   │   ├── ailabeler.py         # AI labeling and analysis
│   │   ├── contextual_qa.py     # Context-aware Q&A
│   │   ├── prospect_simulator.py # Customer simulation
│   │   ├── summarizer.py        # Conversation summarization
│   │   ├── transcribe.py        # Audio transcription
│   │   └── vectorstore.py       # Vector storage management
│   ├── main.py                  # Main application entry
│   └── requirements.txt         # Python dependencies
```

## Features in Detail

### Prospect Simulation
Generates realistic customer inquiries based on Easify's product offerings, pricing, and features, helping sales representatives practice their responses to common questions and scenarios.

### Real-time Analysis
Provides immediate feedback on sales representatives' responses, helping them improve their communication skills and product knowledge.

### Conversation Processing
Automatically transcribes and analyzes sales conversations, providing valuable insights and helping identify areas for improvement.

## License

This project is proprietary and confidential. All rights reserved.

---

For more information or support, please contact the development team.