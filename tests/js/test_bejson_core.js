/**
 * Library:     test_bejson_core.js
 * Jurisdiction: ["JAVASCRIPT", "CORE_COMMAND"]
 * Status:      OFFICIAL — Core-Command/Lib (v1.1)
 * Author:      Elton Boehnen
 * Version:     1.3 OFFICIAL
 * Date:        2026-05-01
 * Description: Core-Command library component.
 */
const {
  bejson_core_atomic_write,
  bejson_core_create_104,
  bejson_core_load_file,
  bejson_core_get_version,
  bejson_core_get_record_count,
} = require('../../js/lib_bejson_core.js');

const fs = require('fs');
const path = require('path');
const assert = require('assert');

function runTests() {
  console.log('Running JavaScript Core Tests...');
  let passed = 0;
  let failed = 0;

  const testDir = path.join(__dirname, 'tmp_core');
  if (!fs.existsSync(testDir)) fs.mkdirSync(testDir);

  const sample104 = bejson_core_create_104(
    'Test',
    [{ name: 'f1', type: 'string' }],
    [['v1']]
  );

  function test(name, fn) {
    try {
      fn();
      passed++;
    } catch (err) {
      failed++;
      console.error(`[FAIL] ${name}: ${err.message}`);
      if (err.stack) console.error(err.stack);
    }
  }

  test('Document Creation', () => {
    assert.strictEqual(sample104.Format_Version, '104');
    assert.strictEqual(sample104.Records_Type[0], 'Test');
  });

  test('Atomic Write', () => {
    const filePath = path.join(testDir, 'test.bejson');
    bejson_core_atomic_write(filePath, sample104);
    assert.ok(fs.existsSync(filePath));
    
    const loaded = bejson_core_load_file(filePath);
    assert.deepStrictEqual(loaded.Values, sample104.Values);
  });

  test('Accessors', () => {
    assert.strictEqual(bejson_core_get_version(sample104), '104');
    assert.strictEqual(bejson_core_get_record_count(sample104), 1);
  });

  // Cleanup
  try {
    fs.readdirSync(testDir).forEach(f => fs.unlinkSync(path.join(testDir, f)));
    fs.rmdirSync(testDir);
  } catch (e) {}

  console.log(`---------------------------------------`);
  console.log(`JS Core Results: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

runTests();
