/**
 * Library:     lib_bejson_parse.js
 * Jurisdiction: ["JAVASCRIPT", "CORE_COMMAND"]
 * Status:      OFFICIAL — Core-Command/Lib (v1.1)
 * Author:      Elton Boehnen
 * Version:     1.1 (OFFICIAL)
 * Date:        2026-04-23
 * Description: BEJSON structured parser — extracts files from BEJSON 104 / 104a / 104db schemas.
Sources lib_bejson_core.js and lib_bejson_validator.js.
Author:      Elton Boehnen
Version:     2.0.0 (OFFICIAL)
Date:        2026-04-16
Requires:    adm-zip (Node.js) → npm install adm-zip
* Changelog v2.0.0:
[NEW] Decoupled ecosystem imports — sources OFFICIAL lib/js/ runtimes.
 */
'use strict';

// ------------------------------------------------------------------
// BEJSON ecosystem — core + validator sourced here
// ------------------------------------------------------------------
const {
  BEJSONCoreError,
  bejson_core_is_valid,
  bejson_core_get_version,
  bejson_core_get_stats,
} = require('./lib_bejson_core.js');

const {
  BEJSONValidationError,
  bejson_validator_validate_string,
  bejson_validator_get_report,
} = require('./lib_bejson_validator.js');

// ------------------------------------------------------------------
// PARSER CORE  — methods mirrored verbatim from the Python lib
// ------------------------------------------------------------------


function parse_json(text) {
  const match = text.match(/(\{[\s\S]*\})/);
  const clean = match ? match[1] : text;
  return JSON.parse(clean);
}


function extract_data(data) {
  const fields = data.Fields || [];
  const values = data.Values || [];
  if (!values.length) return ['My_Project', []];

  const fMap = {};
  fields.forEach((f, i) => {
    const key = f.name.toLowerCase().replace(/[^a-z0-9]/g, '');
    fMap[key] = i;
  });

  function getVal(row, key) {
    const idx = fMap[key];
    if (idx !== undefined && idx < row.length) {
      const v = row[idx];
      if (v !== null && v !== undefined) return String(v).trim();
    }
    return null;
  }

  let projectName = 'My_Project';
  for (const row of values) {
    for (const key of ['projectname', 'zipfilename', 'containername']) {
      const v = getVal(row, key);
      if (v) { projectName = v; break; }
    }
    if (projectName !== 'My_Project') break;
  }

  projectName = projectName.replace(/[<>:"/\\|?*]/g, '_');

  const files = [];
  for (const row of values) {
    for (let i = 1; i <= 50; i++) {
      const fname = getVal(row, 'file' + i + 'name');
      const fcont = getVal(row, 'file' + i + 'content');
      if (fname && fcont) files.push({ name: fname, content: fcont });
    }
  }

  return [projectName, files];
}


function save_files(proj, files, cfg) {
  const fs      = require('fs');
  const path    = require('path');
  const AdmZip  = require('adm-zip');

  const scriptDir  = path.dirname(path.resolve(__filename || __dirname));
  const DEFAULT_OUT = path.join(scriptDir, 'output');

  const baseDir   = (cfg.output_path || DEFAULT_OUT).trim() || DEFAULT_OUT;
  const overwrite = !!cfg.overwrite_enabled;

  if (!fs.existsSync(baseDir)) {
    try { fs.mkdirSync(baseDir, { recursive: true }); }
    catch (e) { return { success: false, message: 'Cannot create output dir: ' + e.message }; }
  }

  let target;
  if (overwrite) {
    target = path.join(baseDir, proj);
    const bakTarget = path.join(baseDir, proj + '_BACKUP');
    if (fs.existsSync(target)) {
      if (fs.existsSync(bakTarget)) _rmrf(bakTarget);
      try { _cpdirSync(target, bakTarget); }
      catch (e) { console.warn('Backup warning: ' + e.message); }
    }
  } else {
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');
    const ts  = `${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}` +
                `_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
    target = path.join(baseDir, ts + '_' + proj);
  }

  try {
    fs.mkdirSync(target, { recursive: true });

    for (const f of files) {
      const fpath = path.join(target, f.name);
      const fdir  = path.dirname(fpath);
      if (!fs.existsSync(fdir)) fs.mkdirSync(fdir, { recursive: true });
      fs.writeFileSync(fpath, f.content, 'utf8');
    }

    // Build report
    const now     = new Date();
    const tsNow   = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-` +
                    `${String(now.getDate()).padStart(2,'0')} ` +
                    `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:` +
                    `${String(now.getSeconds()).padStart(2,'0')}`;
    const modeStr = overwrite ? 'Merge/Update (overwrite)' : 'Timestamped (new folder)';
    const sep52   = '='.repeat(52);
    const dash52  = '-'.repeat(52);

    const lines = [
      sep52,
      '  STRUCTURED PARSER — BUILD REPORT',
      sep52,
      'Project    : ' + proj,
      'Generated  : ' + tsNow,
      'Mode       : ' + modeStr,
      'Output Dir : ' + target,
      'Files      : ' + files.length,
      dash52,
      'FILE LIST',
      dash52,
    ];

    files.forEach((f, idx) => {
      const sizeB = Buffer.byteLength(f.content, 'utf8');
      const sizeS = sizeB >= 1024 ? (sizeB / 1024).toFixed(1) + ' KB' : sizeB + ' B';
      lines.push('  [' + String(idx + 1).padStart(2, '0') + '] ' + f.name + '  (' + sizeS + ')');
    });

    lines.push(dash52);
    lines.push('Zip        : ' + proj + '_update.zip');
    lines.push(sep52);
    const reportText = lines.join('\n') + '\n';

    // Write report to disk
    fs.writeFileSync(path.join(target, '_REPORT.txt'), reportText, 'utf8');

    // Build zip (files + report)
    const zip = new AdmZip();
    for (const f of files) zip.addFile(f.name, Buffer.from(f.content, 'utf8'));
    zip.addFile('_REPORT.txt', Buffer.from(reportText, 'utf8'));
    zip.writeZip(path.join(target, proj + '_update.zip'));

    return {
      success:    true,
      message:    'Saved ' + files.length + ' file(s)',
      path:       target,
      file_count: files.length,
    };

  } catch (e) {
    return { success: false, message: e.message };
  }
}

// ------------------------------------------------------------------
// Internal helpers
// ------------------------------------------------------------------

function _rmrf(dir) {
  const fs   = require('fs');
  const path = require('path');
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir)) {
    const full = path.join(dir, entry);
    if (fs.lstatSync(full).isDirectory()) _rmrf(full);
    else fs.unlinkSync(full);
  }
  fs.rmdirSync(dir);
}

function _cpdirSync(src, dest) {
  const fs   = require('fs');
  const path = require('path');
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src)) {
    const srcPath  = path.join(src,  entry);
    const destPath = path.join(dest, entry);
    if (fs.lstatSync(srcPath).isDirectory()) _cpdirSync(srcPath, destPath);
    else fs.copyFileSync(srcPath, destPath);
  }
}

// ------------------------------------------------------------------
// Exports
// ------------------------------------------------------------------

module.exports = {
  parse_json,
  extract_data,
  save_files,
};
