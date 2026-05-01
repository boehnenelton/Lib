"""
Library:     BEJSON_CMS_Gen_Lib.py
Jurisdiction: ["PYTHON", "CORE_COMMAND"]
Status:      OFFICIAL — Core-Command/Lib (v1.1)
Author:      Elton Boehnen
Version:     1.1 (OFFICIAL)
Date:        2026-04-23
Description: Core-Command library component.
"""
import os
import json
import random
import urllib.request
import urllib.error
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------

MODELS = [
    "gemini-flash-lite-latest",
    "gemini-2.0-flash",
    "gemini-2.0-pro-exp-02-05",
]

# Shared API Keys Pool (from Template)
API_KEYS = [
    "AIzaSyDSigPdinl_SvWfo3-Z9-VdgSfXJ8ack8M",
    "AIzaSyBwfXvW9ld0I5LYI4MjUlV00sBTH6oBw58",
    "AIzaSyBTrZqRcAEnePAxQc4zKAKgnDvfQuyQcmc",
    "AIzaSyB4ts9QPQVmjWaEdr_9UyJK92BnJ3a0crg",
    "AIzaSyCrLMVq_L1MyoXTDa0-Z2Fmh2jWBtKOckM",
    "AIzaSyD28Dl-_EwkmIzPD-eqiJm-dxKzafFplNI",
    "AIzaSyDX8byingeNjrUJ0xzXPTm3hCJ6TJHkXIw",
    "AIzaSyA65bO8Oc0lb8e_VogwSctfYzR0QLC1X7s",
    "AIzaSyAWIgqwD577T3CJ3etppWyzQze-7AQlVwo",
    "AIzaSyCxfebB2La0gJqxHpyzneCk4Z8UYbEtQ2s",
    "AIzaSyDiddjT8GK8-CONBllYX3qfn3FUBpIM7pM",
    "AIzaSyASTr7NE1VJaTl6RVMbp_A53sQ9S8Yy2To",
]

# ==============================================================================
# CONTENT GENERATOR ENGINE
# ==============================================================================

class ContentGenerator:
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model
        self.current_key = random.choice(API_KEYS)
        
    def rotate_key(self):
        self.current_key = random.choice(API_KEYS)

    def _call_gemini(self, prompt: str, system_instruction: str = "") -> Optional[str]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.current_key}"
        
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192}
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={'Content-Type': 'application/json'})
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.load(response)
                if "candidates" in result and result["candidates"]:
                    return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[GenLib] API Error: {e}")
            self.rotate_key()
            return None
        return None

    # --------------------------------------------------------------------------
    # HIGH-LEVEL GENERATION METHODS
    # --------------------------------------------------------------------------

    def generate_page_content(self, topic: str, persona: str = "Technical Writer") -> Dict[str, str]:
        """Generates structured HTML and Markdown content for a CMS page."""
        sys_inst = f"You are a {persona} for the boehnenelton2024 CMS. Output strictly valid HTML for the body and a separate Markdown version."
        prompt = f"Write a comprehensive article about: {topic}. Return your response as a JSON object with keys 'html' and 'markdown'. Do not use markdown code fences in the JSON values."
        
        raw_resp = self._call_gemini(prompt, system_instruction=sys_inst)
        if not raw_resp: return {"html": "", "markdown": ""}
        
        # Clean potential markdown fences from the JSON response
        clean_json = re.sub(r'^```json\s*|\s*```$', '', raw_resp.strip(), flags=re.M)
        try:
            data = json.loads(clean_json)
            return data
        except:
            return {"html": f"<p>{raw_resp}</p>", "markdown": raw_resp}

    def generate_seo_meta(self, content: str) -> Dict[str, str]:
        """Generates Title and Description for SEO based on content."""
        prompt = f"Based on the following content, generate a SEO title (max 60 chars) and a meta description (max 160 chars). Return as JSON with 'title' and 'description' keys:\n\n{content[:2000]}"
        raw_resp = self._call_gemini(prompt)
        if not raw_resp: return {"title": "", "description": ""}
        
        clean_json = re.sub(r'^```json\s*|\s*```$', '', raw_resp.strip(), flags=re.M)
        try:
            return json.loads(clean_json)
        except:
            return {"title": "New Page", "description": ""}

    def generate_and_save_page(self, cms_db, topic: str, category: str = "News", persona: str = "Expert Blogger", title: str = None):
        """
        End-to-end workflow: Generate content -> Generate SEO -> Save to CMS DB.
        """
        print(f"[GenLib] Generating content for: {topic[:50]}...")
        content = self.generate_page_content(topic, persona)
        
        print(f"[GenLib] Optimizing SEO...")
        seo = self.generate_seo_meta(content['markdown'] or content['html'])
        
        final_title = title or seo.get('title') or topic
        pid = cms_db.create_page(final_title, category=category, author=persona)
        
        if pid:
            cms_db.save_page_content(
                pid, 
                html=content['html'], 
                markdown=content['markdown'],
                meta_description=seo.get('description', '')
            )
            print(f"[GenLib] Page Created: {title} (UUID: {pid})")
            return pid
        return None
