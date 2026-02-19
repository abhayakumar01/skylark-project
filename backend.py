import os
import json
import random
import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core import exceptions

# --- CONFIGURATION ---
load_dotenv() # Load environment variables from a .env file if present

# IMPORTANT: You must set your API key here or in an environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD24heR6IgfKe9wR7XT5POWo_n5gMRV8RA") 

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="Skylark Drone Ops API")

# Allow CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- IN-MEMORY DATABASE (Simulating CSVs) ---

PILOTS = [
    {"id": "P001", "name": "Arjun", "skills": ["Mapping", "Survey"], "certs": ["DGCA", "Night Ops"], "location": "Bangalore", "status": "Available", "rate": 1500},
    {"id": "P002", "name": "Neha", "skills": ["Inspection"], "certs": ["DGCA"], "location": "Mumbai", "status": "Assigned", "rate": 3000},
    {"id": "P003", "name": "Rohit", "skills": ["Inspection", "Mapping"], "certs": ["DGCA"], "location": "Mumbai", "status": "Available", "rate": 1500},
    {"id": "P004", "name": "Sneha", "skills": ["Survey", "Thermal"], "certs": ["DGCA", "Night Ops"], "location": "Bangalore", "status": "On Leave", "rate": 5000},
]

DRONES = [
    {"id": "D001", "model": "DJI M300", "capabilities": ["LiDAR", "RGB"], "status": "Available", "maintenance": False, "location": "Bangalore", "weather_rating": "IP43"},
    {"id": "D002", "model": "DJI Mavic 3", "capabilities": ["RGB"], "status": "Maintenance", "maintenance": True, "location": "Mumbai", "weather_rating": "Standard"},
    {"id": "D003", "model": "DJI Mavic 3T", "capabilities": ["Thermal"], "status": "Available", "maintenance": False, "location": "Mumbai", "weather_rating": "IP43"},
    {"id": "D004", "model": "Autel Evo II", "capabilities": ["Thermal", "RGB"], "status": "Available", "maintenance": False, "location": "Bangalore", "weather_rating": "Standard"},
]

MISSIONS = [
    {
        "id": "PRJ001", "client": "Client A", "location": "Bangalore", 
        "start": "2026-02-06", "end": "2026-02-08", 
        "assigned_pilot": "P001", "assigned_drone": "D001", "budget": 10500
    },
    {
        "id": "PRJ002", "client": "Client B", "location": "Mumbai", 
        "start": "2026-02-07", "end": "2026-02-09", 
        "assigned_pilot": "P002", "assigned_drone": "D003", "budget": 10500
    },
    {
        "id": "PRJ003", "client": "Client C", "location": "Bangalore", 
        "start": "2026-02-10", "end": "2026-02-12", 
        "assigned_pilot": None, "assigned_drone": None, "budget": 10500
    }
]

# --- MODELS ---

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[ChatMessage]
    user_input: str

class ChatResponse(BaseModel):
    text: str
    action_taken: Optional[Dict[str, Any]] = None

# --- HELPERS ---

def execute_booking(data: dict):
    new_id = f"PRJ-{random.randint(1000, 9999)}"
    booking_token = f"SKY-{str(datetime.datetime.now().timestamp())[-4:]}-{random.randint(100, 999)}"
    
    new_mission = {
        "id": new_id,
        "bookingToken": booking_token,
        "client": "AI Booking",
        "location": data.get("location"),
        "start": data.get("start"),
        "end": data.get("end"),
        "assigned_pilot": data.get("assigned_pilot_id"),
        "assigned_drone": data.get("assigned_drone_id"),
        "budget": data.get("budget")
    }
    
    MISSIONS.append(new_mission)
    
    # Update statuses
    for p in PILOTS:
        if p["id"] == data.get("assigned_pilot_id"):
            p["status"] = "Assigned"
            
    for d in DRONES:
        if d["id"] == data.get("assigned_drone_id"):
            d["status"] = "Deployed"
            
    return new_mission

# --- ENDPOINTS ---

# @app.post("/chat", response_model=ChatResponse)
# async def chat_endpoint(request: ChatRequest):
#     if not GEMINI_API_KEY:
#         return ChatResponse(text="Error: Gemini API Key is missing on the server. Please check backend.py or your .env file.")

#     system_prompt = f"""
#       You are Skylark, an advanced Drone Operations AI Agent.
      
#       **Role:** Help users book drone missions and query availability.
      
#       **Current Database State:**
#       - Pilots: {json.dumps(PILOTS)}
#       - Drones: {json.dumps(DRONES)}
#       - Active Missions: {json.dumps(MISSIONS)}
      
#       **Booking Rules:**
#       1. To book a mission, you need: Location, Start Date, End Date, Drone Model preference, and Budget (INR).
#       2. **Availability Check:** - Pilot and Drone MUST be in the requested Location.
#          - Pilot/Drone Status must be 'Available' OR 'Assigned' (only if dates do not overlap).
#          - Drone cannot be in 'Maintenance'.
#       3. **Cost Logic:** Cost = Pilot's Daily Rate * Duration (Days).
#       4. **Budget Logic:** If Cost > Budget, warn the user and DO NOT book.
      
#       **Instructions:**
#       - Be conversational and helpful.
#       - If missing details, ask for them politely.
#       - **CRITICAL:** If the user confirms a booking and all rules pass, you MUST output a special JSON block at the end of your response.
      
#       **Action Format:**
#       If booking is confirmed, append this EXACT format at the very end:
#       ___BOOK_ACTION___
#       {{
#         "location": "...",
#         "start": "YYYY-MM-DD",
#         "end": "YYYY-MM-DD",
#         "assigned_pilot_id": "...",
#         "assigned_drone_id": "...",
#         "budget": 0,
#         "cost": 0
#       }}
      
#       **Date Helper:** Today is {datetime.date.today()}.
#     """

#     try:
#         model = genai.GenerativeModel("gemini-2.0-flash")
        
#         # Convert history to Gemini format
#         gemini_history = []
#         for msg in request.history[-6:]: # Keep context short
#             role = "user" if msg.role == "user" else "model"
#             gemini_history.append({"role": role, "parts": [msg.content]})
            
#         chat = model.start_chat(history=gemini_history)
        
#         # Add system prompt context to the current message
#         full_prompt = f"{system_prompt}\n\nUser Query: {request.user_input}"
        
#         response = chat.send_message(full_prompt)
#         ai_text = response.text
        
#         # Check for Action Block
#         action_marker = "___BOOK_ACTION___"
#         booking_data = None
        
#         if action_marker in ai_text:
#             parts = ai_text.split(action_marker)
#             visible_text = parts[0].strip()
#             json_str = parts[1].strip()
            
#             try:
#                 booking_details = json.loads(json_str)
#                 booked_mission = execute_booking(booking_details)
#                 booking_data = booked_mission
                
#                 # Append success message
#                 visible_text += f"\n\n✅ **System Update:** Mission {booked_mission['id']} confirmed. Token: {booked_mission['bookingToken']}"
#                 ai_text = visible_text
#             except Exception as e:
#                 print(f"Booking Error: {e}")
#                 visible_text += "\n\n(System Error: Failed to execute booking database update.)"
#                 ai_text = visible_text

#         return ChatResponse(text=ai_text, action_taken=booking_data)

#     except Exception as e:
#         print(f"Gemini Error: {e}")
#         return ChatResponse(text="I'm currently unable to connect to the AI network. Please try again later.")
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # ... (existing check for API KEY) ...

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # FIX: Keep history short to avoid hitting Token Limits (TPM)
        gemini_history = []
        for msg in request.history[-6:]: 
            role = "user" if msg.role == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg.content]})
            
        chat = model.start_chat(history=gemini_history)
        full_prompt = f"{system_prompt}\n\nUser Query: {request.user_input}"
        
        # Send the message and catch Quota errors
        response = chat.send_message(full_prompt)
        ai_text = response.text
        
        # ... (rest of your action-marker logic) ...

    except exceptions.ResourceExhausted:
        return ChatResponse(
            text="🚨 **Rate Limit Reached:** I'm handling too many drone requests right now. Please wait about 60 seconds before trying again."
        )
    except Exception as e:
        print(f"Gemini Error: {e}")
        return ChatResponse(text="I'm having trouble connecting to HQ. Please try again later.")
@app.get("/csv")
async def get_csv():
    headers = ['project_id', 'client', 'location', 'start_date', 'end_date', 'pilot_id', 'drone_id', 'budget', 'booking_token']
    csv_rows = [",".join(headers)]
    
    for m in MISSIONS:
        row = [
            str(m.get("id")),
            str(m.get("client")),
            str(m.get("location")),
            str(m.get("start")),
            str(m.get("end")),
            str(m.get("assigned_pilot") or 'Unassigned'),
            str(m.get("assigned_drone") or 'Unassigned'),
            str(m.get("budget")),
            str(m.get("bookingToken") or 'LEGACY')
        ]
        csv_rows.append(",".join(row))
    
    return {"csv_content": "\n".join(csv_rows)}

@app.get("/status")
async def get_status():
    return {
        "missions": len(MISSIONS),
        "available_pilots": len([p for p in PILOTS if p["status"] == "Available"]),
        "pilots": PILOTS,
        "drones": DRONES
    }