/**
 * Library:     test_bejson_parse.js
 * Jurisdiction: ["JAVASCRIPT", "CORE_COMMAND"]
 * Status:      OFFICIAL — Core-Command/Lib (v1.1)
 * Author:      Elton Boehnen
 * Version:     1.1 (OFFICIAL)
 * Date:        2026-04-23
 * Description: Core-Command library component.
 */
const {
  parse_json,
  extract_data,
  save_files,
} = require('../../js/lib_bejson_parse.js');

const fs = require('fs');
const path = require('path');
const assert = require('assert');

function runTests() {
  console.log('Running JavaScript Parser Tests...');
  let passed = 0;
  let failed = 0;

  const testDir = path.join(__dirname, 'tmp_parse');
  if (!fs.existsSync(testDir)) fs.mkdirSync(testDir);

  const sample104 = {
    Format: 'BEJSON',
    Format_Version: '104',
    Format_Creator: 'Elton',
    Records_Type: ['File'],
    Fields: [
      { name: 'file1name', type: 'string' },
      { name: 'file1content', type: 'string' }
    ],
    Values: [
      ['test.txt', 'Hello World']
    ]
  };

  function test(name, fn) {
    try {
      fn();
      passed++;
    } catch (err) {
      failed++;
      console.error(`[FAIL] ${name}: ${err.message}`);
    }
  }

  test('Parse JSON', () => {
    const res = parse_json(JSON.stringify(sample104));
    assert.strictEqual(res.Format, 'BEJSON');
  });

  test('Extract Data', () => {
    const [proj, files] = extract_data(sample104);
    assert.strictEqual(files.length, 1);
    assert.strictEqual(files[0].name, 'test.txt');
  });

  test('Save Files', () => {
    const [proj, files] = extract_data(sample104);
    const outPath = path.join(testDir, 'output');
    save_files(proj, files, { output_path: outPath, overwrite_enabled: true });
    assert.ok(fs.existsSync(path.join(outPath, proj, 'test.txt')));
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
  console.log(`JS Parser Results: ${passed} passed, ${failed} failed`);
  if (failed > 0) process.exit(1);
}

runTests();
