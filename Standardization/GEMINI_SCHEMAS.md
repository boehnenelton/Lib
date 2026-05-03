# Gemini BEJSON Standardization
Version: 1.0.0
Date: 2026-04-27

This document defines the standardized BEJSON schemas for the Gemini AI ecosystem within the project. These schemas are used by the **BEJSON Unified Editor** and associated automation tools.

---

## 1. Gemini Profile Schema (v104)
**File:** `gemini_profile_template.bejson`  
**Purpose:** Defines the persona, system instructions, and behavioral parameters for a Gemini-based AI agent.

### Example
```json
{
  "Format": "BEJSON",
  "Format_Version": "104",
  "Format_Creator": "Elton Boehnen",
  "Records_Type": ["AI_Profile"],
  "Parent_Hierarchy": "/LLM_Configuration",
  "Fields": [
    {"name": "Record_Type_Parent", "type": "string"},
    {"name": "Name", "type": "string"},
    {"name": "Archetype", "type": "string"},
    {"name": "Persona", "type": "string"},
    {"name": "SystemInstruction", "type": "string"},
    {"name": "ForbiddenTopics", "type": "array"},
    {"name": "Avatar_Type", "type": "string"},
    {"name": "Avatar_sourceUrl", "type": "string"},
    {"name": "Avatar_Data", "type": "string"},
    {"name": "MaxResponseTokens", "type": "integer"},
    {"name": "Creativity", "type": "number"},
    {"name": "Tone", "type": "array"},
    {"name": "Formality", "type": "string"},
    {"name": "Verbosity", "type": "string"},
    {"name": "EmotionalExpression_Enabled", "type": "boolean"},
    {"name": "EmotionalExpression_Intensity", "type": "number"},
    {"name": "GoogleSearch_Enabled", "type": "boolean"},
    {"name": "CodeInterpreter_Enabled", "type": "boolean"},
    {"name": "EphemeralMemory", "type": "boolean"},
    {"name": "CodeParsing_Mode", "type": "string"},
    {"name": "CodeParsing_Languages", "type": "array"},
    {"name": "CodeParsing_StructureValidation", "type": "boolean"},
    {"name": "CodeParsing_VersionControl", "type": "boolean"}
  ],
  "Values": [
    [
      "AI_Profile",
      "Gemini_Assistant",
      "Tutor",
      "Short description of the AI persona.",
      "System instructions here...",
      [],
      "Emoji",
      "",
      "🤖",
      65536,
      0.2,
      ["Professional", "Helpful"],
      "Formal",
      "Normal",
      false,
      0.0,
      true,
      true,
      true,
      "complete",
      ["python", "javascript"],
      true,
      true
    ]
  ]
}
```

---

## 2. Gemini Key Registry Schema (v104a)
**File:** `gemini_key_template.104a.bejson`  
**Purpose:** Stores a pool of Gemini API keys for Round Robin rotation and fail-over logic. Supports up to 10 slots.

### Example
```json
{
  "Format": "BEJSON",
  "Format_Version": "104a",
  "Format_Creator": "Elton Boehnen",
  "Schema_Name": "GeminiKeyTemplate",
  "Records_Type": ["ApiKey"],
  "Fields": [
    {"name": "key_slot", "type": "integer"},
    {"name": "key", "type": "string"}
  ],
  "Values": [
    [1, "YOUR_GEMINI_KEY_1_HERE"],
    [2, "YOUR_GEMINI_KEY_2_HERE"],
    [3, "YOUR_GEMINI_KEY_3_HERE"],
    [4, "YOUR_GEMINI_KEY_4_HERE"],
    [5, "YOUR_GEMINI_KEY_5_HERE"],
    [6, "YOUR_GEMINI_KEY_6_HERE"],
    [7, "YOUR_GEMINI_KEY_7_HERE"],
    [8, "YOUR_GEMINI_KEY_8_HERE"],
    [9, "YOUR_GEMINI_KEY_9_HERE"],
    [10, "YOUR_GEMINI_KEY_10_HERE"]
  ]
}
```

---

## 3. Gemini Model Registry Schema (v104a)
**File:** `gemini_model_template.104a.bejson`  
**Purpose:** Lists available Gemini models for the current year (2026) and tracks which model is currently active globally.

### Example
```json
{
  "Format": "BEJSON",
  "Format_Version": "104a",
  "Format_Creator": "Elton Boehnen",
  "Schema_Name": "GeminiModelTemplate",
  "Records_Type": ["GeminiModel"],
  "Fields": [
    {"name": "model_name", "type": "string"},
    {"name": "model_id", "type": "string"},
    {"name": "currently_active", "type": "boolean"}
  ],
  "Values": [
    ["Gemini 3.1 Pro (Preview)", "gemini-3.1-pro-preview", false],
    ["Gemini 3 Flash (Preview)", "gemini-3-flash-preview", true],
    ["Gemini 3.1 Flash-Lite (Preview)", "gemini-3.1-flash-lite-preview", false],
    ["Gemini Flash-Lite (Latest)", "gemini-flash-lite-latest", false],
    ["Gemini 2.5 Flash", "gemini-2.5-flash", false]
  ]
}
```
