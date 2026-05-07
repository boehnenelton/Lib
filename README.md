# BEJSON Ecosystem Libraries
**Version: 1.4 OFFICIAL** | **MFDB Spec: v1.3.1** | **Date: May 2026**

A unified, multi-language suite of libraries designed for the **BEJSON (Boehnen Elton JSON)** data format and **MFDB (Multifile Database)** architecture. This repository serves as the foundational "Management Layer" for all development and operational nodes in the 2026 federated environment.

---

## 🚀 Core Philosophy: Structural Integrity
BEJSON is a tabular data format that enforces **positional integrity**. By decoupling field definitions from record values, it achieves high-performance parsing and strict schema validation while remaining human-readable for AI agents.

### Key Standards
- **BEJSON 104/104a/104db:** Supports single-entity, metadata-heavy, and relational multi-entity formats.
- **MFDB v1.3.1:** A "Mount-Commit" federated database pattern that enables "Structural Blindness" in AI context windows.
- **2026 Gemini Standards:** Native support for the Gemini 3.1 Pro/Flash lineup and the Interactions API.

---

## 📦 Module Breakdown

### 🤖 AI (Artificial Intelligence)
Found in `py/AI/`.
- **`lib_bejson_genai.py`**: Integration for the latest `google-genai` SDK. Supports round-robin key rotation across pools of 2026-standardized models.
- **`lib_bejson_gemini.py`**: Unified prompter engine with embedded schemas for Key Registries, Model Registries, and AI Profiles.
- **Key Support:** Supports Gemini 3.1, Gemma 4, Groq, and OpenRouter with unified status feedback.

### 🏛️ Core & CMS
Found in `py/Core/` and `py/CMS/`.
- **`lib_bejson_core.py`**: The definitive implementation of BEJSON. Handles document creation, mutation, and **atomic file I/O** (os.rename + fsync).
- **`lib_mfdb_core.py`**: Orchestrates manifest-entity relationships across the file system.
- **`lib_cms_orchestrator.py`**: High-level API for modular content management, taxonomies, and site configuration.

### 🎨 HTML2 (Visual Components)
Found in `py/HTML/`.
- **Terminal Aesthetics:** Features like `html_code_box` provide interactive, high-contrast code snippets with copy-to-clipboard functionality.
- **Modular Components:** Layout skeletons, animations, metrics, and diagrammers designed for high-signal technical reports.
- **Diagramming:** Native support for BEJSON-to-SVG and BEJSON-to-HTML diagram generation.

### 🛠️ System & Tools
Found in `py/System/`.
- **`lib_be_project_service.py`**: Manages repository state and system-wide synchronization.
- **`lib_book_builder.py`**: Automated pipeline for document and ebook generation.
- **`lib_av_manager.py`**: Standardized presets for audio/video processing in Termux.

---

## 🌐 Multi-Language Support
The ecosystem is built to be language-agnostic. Implementations are kept in sync across:
- **Python (`py/`)**: The primary reference implementation.
- **TypeScript/JS (`ts/`, `js/`)**: Support for browser-based diagrammers and Node.js services.
- **Shell (`sh/`)**: Critical for Termux initialization and low-level system hooks.
- **Rust (`rs/`)**: High-performance implementations for core parsing and validation.

---

## 🛠 Installation

```bash
# Clone the repository
git clone https://github.com/boehnenelton/Lib.git

# Link to your local project
ln -s /path/to/Lib/py/Core lib_core
```

---

## 📜 Engineering Standards (POL001-POL004)
1. **Atomic Safety:** Every write operation must use `bejson_core_atomic_write`.
2. **Human Readability:** All records and logs must be written in human-readable BEJSON.
3. **UTC Mandate:** All timestamps must use ISO 8601 UTC.
4. **Standardization:** All field names use `snake_case`; all entities use `PascalCase`.

---

**© 2026 Elton Boehnen** | [boehnenelton2024.pages.dev](https://boehnenelton2024.pages.dev)
*"Structure defines Intelligence."*
