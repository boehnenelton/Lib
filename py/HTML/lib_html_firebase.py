"""
Library:     lib_html_firebase.py
Family:      HTML
Jurisdiction: ["PYTHON", "WEB_SDK"]
Status:      EXPERIMENTAL
Author:      Elton Boehnen / Gemini
Version:     1.3 OFFICIAL
Date:        2026-05-01
Description: Firebase SDK integration for HTML2 projects.
"""

FIREBASE_CONFIG = {
    "apiKey": "AIzaSyBA1It3XFoPFZh4Ns75ySH4f4PDjcS3Bnk",
    "authDomain": "html2integration.firebaseapp.com",
    "projectId": "html2integration",
    "storageBucket": "html2integration.firebasestorage.app",
    "messagingSenderId": "998275183580",
    "appId": "1:998275183580:web:0d390eee5072acec661519"
}

def get_firebase_init_script(config=None):
    """
    Returns a <script type="module"> tag with Firebase initialization.
    Uses the CDN-based Modular SDK.
    """
    cfg = config or FIREBASE_CONFIG
    import json
    cfg_json = json.dumps(cfg, indent=2)
    
    script = f"""
<script type="module">
  // Import the functions you need from the SDKs you need
  import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/12.12.1/firebase-app.js";
  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries

  // Your web app's Firebase configuration
  const firebaseConfig = {cfg_json};

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  console.log("Firebase initialized successfully:", app.name);
  
  // Expose status to UI if badge exists
  const badge = document.getElementById('status-badge');
  if (badge) {{
      badge.textContent = "INITIALIZED";
      badge.style.backgroundColor = "#4CAF50";
      badge.style.color = "white";
  }}
</script>
"""
    return script
