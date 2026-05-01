# lib-bejson_core.sh Documentation

## Overview

The `lib-bejson_core.sh` library provides comprehensive manipulation capabilities for BEJSON (Boehnen Elton JSON) documents in Bash/Termux environments. It enables creation, loading, querying, modification, and management of all three BEJSON format versions: 104, 104a, and 104db.

## Table of Contents

1. [Installation & Dependencies](#installation--dependencies)
2. [Error Codes](#error-codes)
3. [Atomic File Operations](#atomic-file-operations)
4. [Document Creation](#document-creation)
5. [Document Loading & Parsing](#document-loading--parsing)
6. [Position-Based Indexing & Querying](#position-based-indexing--querying)
7. [104DB Specific Operations](#104db-specific-operations)
8. [Data Modification](#data-modification)
9. [Table Operations (Column/Row Manipulation)](#table-operations-columnrow-manipulation)
10. [Utility Functions](#utility-functions)
11. [Usage Examples](#usage-examples)

---

## Installation & Dependencies

### Prerequisites

- Bash 4.0 or higher
- `jq` command-line JSON processor
- `lib-bejson_validator.sh` (in same directory)
- Termux/Android compatibility

### Installation

```bash
# Copy both libraries to your project directory
cp lib-bejson_validator.sh lib-bejson_core.sh /path/to/your/project/

# Source the core library (automatically sources validator)
source /path/to/your/project/lib-bejson_core.sh
