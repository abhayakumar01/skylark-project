🚁 Skylark Drone Ops Agent
Skylark is an AI-powered operations agent designed to streamline drone mission management. Using the Gemini 2.0 Flash model, it allows users to check pilot availability, browse drone fleets, and book new missions using natural language.
<img width="1918" height="1077" alt="image" src="https://github.com/user-attachments/assets/bbb53841-dd22-4485-8da8-63174d53b628" />

🌟 Key Features
Natural Language Booking: Chat with the agent to schedule missions.

Real-time Status: Dashboard metrics for active missions and available pilots.

Smart Logic: Automatically calculates costs based on pilot rates and mission duration.

Fleet Management: Visualized tables of drones (LiDAR, Thermal, RGB) and pilots.

Data Export: Generate and download missions.csv directly from the UI.

🛠️ Tech Stack
Frontend: Streamlit (Python)

Backend: FastAPI

AI Engine: Google Gemini 2.0 Flash

Data Handling: Pandas & Pydantic

🚀 Getting Started
1. Clone the Repository
Bash
git clone https://github.com/your-username/skylark-drone-ops.git
cd skylark-drone-ops
2. Set Up Environment Variables
Create a .env file in the root directory and add your Google AI API key:

Plaintext
GEMINI_API_KEY=your_api_key_here
3. Install Dependencies
Bash
pip install -r requirements.txt
🏃‍♂️ How to Run
You need to run the Backend and Frontend in two separate terminals.

Step 1: Start the FastAPI Backend
Bash
# Terminal 1
uvicorn backend:app --reload
The API will be live at http://localhost:8000

Step 2: Start the Streamlit Frontend
Bash
# Terminal 2
streamlit run frontend.py
The dashboard will open at http://localhost:8501

📂 Project Structure
Plaintext
├── backend.py        # FastAPI server with Gemini integration
├── frontend.py       # Streamlit UI & Chat interface
├── .env              # Private API keys (not for version control)
├── requirements.txt  # Project dependencies
└── README.md         # You are here!
⚠️ Known Issues & Quotas
As this project uses the Gemini Free Tier, you may encounter a ResourceExhausted (Rate Limit) error if you send messages too quickly. The system is designed to catch these errors and notify you to wait 60 seconds.

📜 License
This project is licensed under the MIT License.

A few tips for your GitHub repo:
.gitignore: Make sure you create a .gitignore file and add .env to it so you don't accidentally push your API key to the internet!

Screenshots: Once you have the app running, take a screenshot of the chat and the sidebar and add it to a /images folder to make your README look even better.
