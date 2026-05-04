/**
 * Library:     test_bejson_validator.js
 * Jurisdiction: ["JAVASCRIPT", "CORE_COMMAND"]
 * Status:      OFFICIAL — Core-Command/Lib (v1.1)
 * Author:      Elton Boehnen
 * Version:     1.3 OFFICIAL
 * Date:        2026-05-01
 * Description: Core-Command library component.
 */
const {
  bejson_validator_reset_state,
  bejson_validator_get_errors,
  bejson_validator_get_warnings,
  bejson_validator_has_errors,
  bejson_validator_has_warnings,
  bejson_validator_error_count,
  bejson_validator_warning_count,
  bejson_validator_check_json_syntax,
  bejson_validator_check_mandatory_keys,
  bejson_validator_check_fields_structure,
  bejson_validator_check_records_type,
  bejson_validator_check_values,
  bejson_validator_validate_string,
  bejson_validator_get_report,
  BEJSONValidationError
} = require('../../js/lib_bejson_validator.js');

const assert = require('assert');

function runTests() {
  console.log('Running JavaScript Validator Tests...');
  let passed = 0;
  let failed = 0;

  const valid104 = {
    Format: 'BEJSON',
    Format_Version: '104',
    Format_Creator: 'Elton Boehnen',
    Records_Type: ['Test'],
    Fields: [{ name: 'id', type: 'string' }],
    Values: [['a']]
  };

  function test(name, fn) {
    try {
      bejson_validator_reset_state();
      fn();
      passed++;
      // console.log(`[PASS] ${name}`);
    } catch (err) {
      failed++;
      console.error(`[FAIL] ${name}: ${err.message}`);
      if (err.stack) console.error(err.stack);
    }
  }

  test('State Management', () => {
    assert.strictEqual(bejson_validator_has_errors(), false);
    try { bejson_validator_validate_string('invalid'); } catch (e) {}
    assert.strictEqual(bejson_validator_has_errors(), true);
    bejson_validator_reset_state();
    assert.strictEqual(bejson_validator_has_errors(), false);
  });

  test('JSON Syntax', () => {
    assert.deepStrictEqual(bejson_validator_check_json_syntax('{"a":1}'), { a: 1 });
    assert.throws(() => bejson_validator_check_json_syntax('{"a":1'), { name: 'BEJSONValidationError' });
  });

  test('Mandatory Keys', () => {
    assert.strictEqual(bejson_validator_check_mandatory_keys(valid104), '104');
    const bad = { ...valid104 };
    delete bad.Format;
    assert.throws(() => bejson_validator_check_mandatory_keys(bad), { name: 'BEJSONValidationError' });
  });

  test('Fields Structure', () => {
    assert.strictEqual(bejson_validator_check_fields_structure(valid104, '104'), 1);
    const bad = { ...valid104, Fields: [{ no_name: 'x' }] };
    assert.throws(() => bejson_validator_check_fields_structure(bad, '104'), { name: 'BEJSONValidationError' });
  });

  test('Records Type', () => {
    bejson_validator_check_records_type(valid104, '104');
    const bad = { ...valid104, Records_Type: [] };
    assert.throws(() => bejson_validator_check_records_type(bad, '104'), { name: 'BEJSONValidationError' });
  });

  test('Values Validation', () => {
    bejson_validator_check_values(valid104, '104', 1);
    const bad = { ...valid104, Values: [[123]] }; // type mismatch (expected string)
    assert.throws(() => bejson_validator_check_values(bad, '104', 1), { name: 'BEJSONValidationError' });
  });

  test('Full Validation', () => {
    assert.strictEqual(bejson_validator_validate_string(JSON.stringify(valid104)), true);
  });

  test('Report Generation', () => {
    const report = bejson_validator_get_report(JSON.stringify(valid104));
    assert.ok(report.includes('Status: VALID'));
    const badReport = bejson_validator_get_report('{}');
    assert.ok(badReport.includes('Status: INVALID'));
  });

  console.log(`---------------------------------------`);
  console.log(`JS Validator Results: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

runTests();
