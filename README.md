# OAuth Implementation with FastAPI

A simple OAuth implementation using FastAPI backend and basic HTML frontend.

## Project Summary
- Implemented Google OAuth2 authentication.
- Created a FastAPI backend with token management and user info retrieval.
- Developed a simple HTML frontend for user interaction.

## Installation Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/Nakuyu/Oauth_Implementation_Basic.git
   cd Oauth_Implementation_Basic
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the `backend` directory with your Google OAuth credentials:
   ```
   CLIENT_ID=your_google_client_id
   CLIENT_SECRET=your_google_client_secret
   REDIRECT_URI=http://localhost:8000/auth/callback
   SECRET_KEY=12345678901234567890123456789012
   ```

5. Run the backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   
6. Open `frontend/index.html` in your browser to test the application.
