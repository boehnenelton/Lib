"""
Library:     lib_html_firebase.py
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Status:      OFFICIAL - v1.4.0
Date:        2026-05-07
"""
"""
Library:     lib_html_firebase.py
Family:      HTML
Jurisdiction: ["PYTHON", "WEB_SDK"]
Status:      OFFICIAL
Author:      Elton Boehnen / Gemini
Version:     1.4 OFFICIAL
Date:        2026-05-07
Description: Firebase SDK integration with 2026 Pipeline standards.
"""

import json

FIREBASE_CONFIG = {
    "apiKey": "REDACTED_API_KEY",
    "authDomain": "html2integration.firebaseapp.com",
    "projectId": "html2integration",
    "storageBucket": "html2integration.firebasestorage.app",
    "messagingSenderId": "998275183580",
    "appId": "1:998275183580:web:0d390eee5072acec661519"
}

SDK_VERSION = "12.12.1"

def get_firebase_init_script(config=None, services=None):
    """
    Returns a <script type="module"> tag with Firebase initialization.
    services: list of strings ['auth', 'firestore', 'analytics', 'performance']
    """
    cfg = config or FIREBASE_CONFIG
    services = services or []
    cfg_json = json.dumps(cfg, indent=2)
    
    imports = [f'import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/{SDK_VERSION}/firebase-app.js";']
    
    init_logic = []
    
    if "auth" in services:
        imports.append(f'import {{ getAuth }} from "https://www.gstatic.com/firebasejs/{SDK_VERSION}/firebase-auth.js";')
        init_logic.append("  const auth = getAuth(app);")
        init_logic.append("  window.firebaseAuth = auth;")

    if "firestore" in services:
        imports.append(f'import {{ getFirestore }} from "https://www.gstatic.com/firebasejs/{SDK_VERSION}/firebase-firestore.js";')
        imports.append(f'import * as pipelines from "https://www.gstatic.com/firebasejs/{SDK_VERSION}/firebase-firestore-pipelines.js";')
        init_logic.append("  const db = getFirestore(app);")
        init_logic.append("  window.firestoreDb = db;")
        init_logic.append("  window.firestorePipelines = pipelines;")
        init_logic.append("  console.log('Firestore Pipelines (2026 Standard) loaded.');")

    imports_str = "\n  ".join(imports)
    init_logic_str = "\n".join(init_logic)

    script = f\"\"\"
<script type="module">
  {imports_str}

  const firebaseConfig = {cfg_json};

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  console.log("Firebase initialized successfully:", app.name);
  
{init_logic_str}

  // Expose status to UI if badge exists
  const badge = document.getElementById('status-badge');
  if (badge) {{
      badge.textContent = "INITIALIZED";
      badge.style.backgroundColor = "#4CAF50";
      badge.style.color = "white";
  }}
</script>
\"\"\"
    return script

def get_firestore_pipeline_example():
    \"\"\"
    Returns a string containing a 2026 standard Firestore Pipeline example.
    \"\"\"
    return \"\"\"
// 2026 Standard: Relational Join via Pipeline
const {{ field, variable }} = window.firestorePipelines;
const db = window.firestoreDb;

const articlesWithAuthProfile = db.pipeline().collection(\"articles\")
  .define(field(\"authorUid\").as(\"author_id\"))
  .addFields(
    db.pipeline().collection(\"users\")
      .where(field(\"__name__\").documentId().equal(variable(\"author_id\")))
      .select(field(\"displayName\"), field(\"avatarUrl\"), field(\"handle\"))
      .toScalarExpression()
      .as(\"author\")
  );
\"\"\"
