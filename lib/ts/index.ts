/*
Library:     index.ts
MFDB Version: 1.3.1
Format_Creator: Elton Boehnen
Status:      OFFICIAL - v1.3.1
Date:        2026-05-06
*/

/**
 * Library:     index.ts
 * Jurisdiction: ["TYPESCRIPT", "CORE_COMMAND"]
 * Status:      OFFICIAL — Core-Command/Lib (v1.1)
 * Author:      Elton Boehnen
 * Version:     1.1 (OFFICIAL)
 * Date:        2026-04-23
 * Description: Core-Command library component.
 */
// Types & error classes
export * from "./bejson_types";

// Core operations (parse, serialize, record CRUD)
export * from "./bejson_core";

// BEJSON validators (104, 104a, 104db)
export {
  validateDocument,
  validate104,
  validate104a,
  validate104db,
  assertValid,
  isValid,
} from "./bejson_validators";

// MFDB validators
export {
  discoverRole,
  validateManifest,
  validateEntityFile,
  validateDatabase,
  decodeManifestRecords,
  decodeDatabaseMeta,
} from "./mfdb_validators";

// MFDB core
export {
  createManifest,
  registerEntity,
  unregisterEntity,
  syncRecordCount,
} from "./mfdb_core";

export type { EntityValidationOptions, DatabaseValidationOptions } from "./mfdb_validators";
export type { CreateManifestOptions as MFDBCreateManifestOptions } from "./mfdb_core";

export * from "./bejson_assets";
export * from "./bejson_engine";
export * from "./bejson_events";
export * from "./bejson_grid";
export * from "./bejson_input";
export * from "./bejson_physics";
export * from "./bejson_renderer";
