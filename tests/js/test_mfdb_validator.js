/**
 * Library:     test_mfdb_validator.js
 * Jurisdiction: ["JAVASCRIPT", "CORE_COMMAND"]
 * Status:      OFFICIAL — Core-Command/Lib (v1.1)
 * Author:      Elton Boehnen
 * Version:     1.3 OFFICIAL
 * Date:        2026-05-01
 * Description: Core-Command library component.
 */
const {
  mfdb_validator_validate_manifest,
} = require('../../js/lib_mfdb_validator.js');

const {
  mfdb_core_create_database,
} = require('../../js/lib_mfdb_core.js');

const fs = require('fs');
const path = require('path');
const assert = require('assert');

function runTests() {
  console.log('Running JavaScript MFDB Validator Tests...');
  let passed = 0;
  let failed = 0;

  const testDir = path.join(__dirname, 'tmp_mfdb_val');
  if (!fs.existsSync(testDir)) fs.mkdirSync(testDir);

  const entities = [
    {
      name: 'User',
      fields: [{ name: 'id', type: 'string' }, { name: 'name', type: 'string' }],
      primary_key: 'id'
    }
  ];

  function test(name, fn) {
    try {
      fn();
      passed++;
    } catch (err) {
      failed++;
      console.error(`[FAIL] ${name}: ${err.message}`);
    }
  }

  test('Manifest Validation', () => {
    const manifestPath = mfdb_core_create_database(testDir, 'TestDB', entities, 'A test db');
    assert.ok(mfdb_validator_validate_manifest(manifestPath));
  });

  // Cleanup
  try {
    const rm = (p) => {
      if (fs.statSync(p).isDirectory()) {
        fs.readdirSync(p).forEach(f => rm(path.join(p, f)));
        fs.rmdirSync(p);
      } else {
        fs.unlinkSync(p);
      }
    };
    rm(testDir);
  } catch (e) {}

  console.log(`---------------------------------------`);
  console.log(`JS MFDB Validator Results: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

runTests();
