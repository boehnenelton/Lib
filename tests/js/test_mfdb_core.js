/**
 * Library:     test_mfdb_core.js
 * Jurisdiction: ["JAVASCRIPT", "CORE_COMMAND"]
 * Status:      OFFICIAL — Core-Command/Lib (v1.1)
 * Author:      Elton Boehnen
 * Version:     1.1 (OFFICIAL)
 * Date:        2026-04-23
 * Description: Core-Command library component.
 */
const {
  mfdb_core_create_database,
  mfdb_core_load_manifest,
  mfdb_core_load_entity,
  mfdb_core_add_entity_record,
  mfdb_core_discover,
} = require('../../js/lib_mfdb_core.js');

const fs = require('fs');
const path = require('path');
const assert = require('assert');

function runTests() {
  console.log('Running JavaScript MFDB Core Tests...');
  let passed = 0;
  let failed = 0;

  const testDir = path.join(__dirname, 'tmp_mfdb');
  if (!fs.existsSync(testDir)) fs.mkdirSync(testDir);

  const entities = [
    {
      name: 'User',
      fields: [{ name: 'id', type: 'string' }, { name: 'name', type: 'string' }],
      primary_key: 'id'
    }
  ];

  let manifestPath;

  function test(name, fn) {
    try {
      fn();
      passed++;
    } catch (err) {
      failed++;
      console.error(`[FAIL] ${name}: ${err.message}`);
    }
  }

  test('Database Creation', () => {
    manifestPath = mfdb_core_create_database(testDir, 'TestDB', entities, 'A test db');
    assert.ok(fs.existsSync(manifestPath));
    const manifest = mfdb_core_load_manifest(manifestPath);
    assert.strictEqual(manifest.length, 1);
    assert.strictEqual(manifest[0].entity_name, 'User');
  });

  test('Discovery', () => {
    assert.strictEqual(mfdb_core_discover(manifestPath), 'manifest');
    const userPath = path.join(testDir, 'data', 'user.bejson');
    assert.strictEqual(mfdb_core_discover(userPath), 'entity');
  });

  test('Entity Operations', () => {
    mfdb_core_add_entity_record(manifestPath, 'User', ['u1', 'Alice']);
    const users = mfdb_core_load_entity(manifestPath, 'User');
    assert.strictEqual(users.length, 1);
    assert.strictEqual(users[0].name, 'Alice');
    
    // Verify sync
    const manifest = mfdb_core_load_manifest(manifestPath);
    assert.strictEqual(manifest[0].record_count, 1);
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
  console.log(`JS MFDB Core Results: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

runTests();
