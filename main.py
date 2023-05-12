from fastapi import FastAPI, Request, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import firebase_admin
from firebase_admin import credentials, firestore

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("Service.json")
firebase_admin.initialize_app(cred)

# Get a Firestore client
db = firestore.client()

@app.get("/")
async def root():
    return {"messages": "Halo kawan"}

@app.post("/tweets")
async def add_tweets(request: Request, data: dict = Body(...)):
    try:
        search_term = data["search_term"]
        tweet = data["tweets"][0]["text"]

        # Generate a unique ID for the document
        doc_id = str(uuid.uuid4())

        # Set the document in Firestore with the generated ID
        doc_ref = db.collection("tweets").document(doc_id)
        doc_ref.set({"search_term": search_term, "tweets": [{"text": tweet}]})

        return {"message": f"Tweets for {search_term} added successfully with ID {doc_id}"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/tweets")
async def get_tweets(search_term: str = None):
    try:
        # Get all the tweets documents from Firestore
        tweets_ref = db.collection("tweets")

        if search_term is not None:
            # Search for tweets with the given search term
            query = tweets_ref.where("search_term", "==", search_term)
            tweets_docs = query.stream()
        else:
            # Get all tweets
            tweets_docs = tweets_ref.stream()

        # Loop through all the documents and append the data to a list
        tweets = []
        for doc in tweets_docs:
            doc_data = doc.to_dict()
            tweets.append(doc_data)

        return {"tweets": tweets}
    except Exception as e:
        return {"error": str(e)}

@app.get("/set_cookie")
async def set_cookie(response: Response):
    response.set_cookie(key="my_cookie", value="cookie_value")
    return {"message": "Cookie set successfully."}

@app.post("/login")
async def login(request: Request, username: str = Body(...), password: str = Body(...), email: str = Body(...)):
    try:
        # Authenticate user
        # ...

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Store session data in Firestore
        doc_ref = db.collection("sessions").document(session_id)
        doc_ref.set({"username": username, "email": email})

        # Set session ID in response header
        response = JSONResponse({"message": "Login successful."})
        response.set_cookie(key="session_id", value=session_id)
        return response
    except Exception as e:
        return {"error": str(e)}


@app.get("/protected")
async def protected(request: Request):
    try:
        # Get session ID from cookie
        session_id = request.cookies.get("session_id")
        if not session_id:
            return {"error": "No session ID found."}

        # Check if session ID exists in Firestore
        doc_ref = db.collection("sessions").document(session_id)
        doc = doc_ref.get()
        if not doc.exists:
            return {"error": "Session ID not found."}

        # Session exists, retrieve session data
        session_data = doc.to_dict()

        # Return protected data, along with session data
        return {"protected_data": "This is protected data.", "session_data": session_data}
    except Exception as e:
        return {"error": str(e)}
