pub mod types;

use std::fs;
use std::io::{Write, Read};
use std::path::{Path, PathBuf};
use chrono::{Local, Utc};
use serde_json::{Value};
use types::*;
use zip::write::FileOptions;
use walkdir::WalkDir;

/// Load a BEJSON file from disk.
pub fn load_file<P: AsRef<Path>>(path: P) -> Result<BEJSONDocument> {
    let content = fs::read_to_string(path)
        .map_err(|e| BEJSONError::FieldNotFound(e.to_string()))?;
    let doc: BEJSONDocument = serde_json::from_str(&content)
        .map_err(|e| BEJSONError::InvalidOperation(format!("Parse error: {}", e)))?;
    Ok(doc)
}

/// Return the index of a field by name.
pub fn get_field_index(doc: &BEJSONDocument, field_name: &str) -> Result<usize> {
    doc.fields.iter().position(|f| f.name == field_name)
        .ok_or_else(|| BEJSONError::FieldNotFound(field_name.to_string()))
}

/// MFDBArchive support (v1.2 Feature)
pub struct MFDBArchive;

impl MFDBArchive {
    /// Extract .mfdb.zip to workspace.
    pub fn mount<P: AsRef<Path>>(archive_path: P, target_dir: P) -> Result<PathBuf> {
        let arc_p = archive_path.as_ref();
        let target_p = target_dir.as_ref();
        
        if !arc_p.exists() {
            return Err(BEJSONError::ArchiveError(format!("Archive not found: {:?}", arc_p)));
        }

        let lock_file = target_p.join(".mfdb_lock");
        if lock_file.exists() {
            let lock_content = fs::read_to_string(&lock_file).unwrap_or_default();
            return Err(BEJSONError::MountConflict(format!("Workspace already locked: {}", lock_content)));
        }

        fs::create_dir_all(target_p).map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;
        
        let file = fs::File::open(arc_p).map_err(|e| BEJSONError::ArchiveError(e.to_string()))?;
        let mut archive = zip::ZipArchive::new(file).map_err(|e| BEJSONError::ArchiveError(e.to_string()))?;

        for i in 0..archive.len() {
            let mut file = archive.by_index(i).map_err(|e| BEJSONError::ArchiveError(e.to_string()))?;
            let outpath = match file.enclosed_name() {
                Some(path) => target_p.join(path),
                None => continue,
            };

            if (*file.name()).ends_with('/') {
                fs::create_dir_all(&outpath).map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;
            } else {
                if let Some(p) = outpath.parent() {
                    if !p.exists() {
                        fs::create_dir_all(&p).map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;
                    }
                }
                let mut outfile = fs::File::create(&outpath).map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;
                std::io::copy(&mut file, &mut outfile).map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;
            }
        }

        let manifest_path = target_p.join("104a.mfdb.bejson");
        if !manifest_path.exists() {
            return Err(BEJSONError::ArchiveError("Invalid MFDB Archive: manifest missing".to_string()));
        }

        // Create lock
        let lock_data = format!("PID: {}, Mounted: {}", std::process::id(), Utc::now());
        fs::write(lock_file, lock_data).map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;

        Ok(manifest_path)
    }

    /// Repack workspace to .mfdb.zip atomically.
    pub fn commit<P: AsRef<Path>>(mount_dir: P, archive_path: P) -> Result<()> {
        let mount_p = mount_dir.as_ref();
        let dest_p = archive_path.as_ref();
        
        let temp_arc = dest_p.with_extension("zip.tmp");
        let file = fs::File::create(&temp_arc).map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;
        let mut zip = zip::ZipWriter::new(file);
        let options = FileOptions::default()
            .compression_method(zip::CompressionMethod::Deflated)
            .unix_permissions(0o755);

        for entry in WalkDir::new(mount_p) {
            let entry = entry.map_err(|e| BEJSONError::ArchiveError(e.to_string()))?;
            let path = entry.path();
            let name = path.strip_prefix(mount_p).unwrap();

            if name.to_str() == Some(".mfdb_lock") { continue; }
            if name.as_os_str().is_empty() { continue; }

            if path.is_file() {
                zip.start_file(name.to_str().unwrap(), options).map_err(|e| BEJSONError::ArchiveError(e.to_string()))?;
                let mut f = fs::File::open(path).map_err(|e| BEJSONError::ArchiveError(e.to_string()))?;
                let mut buffer = Vec::new();
                f.read_to_end(&mut buffer).map_err(|e| BEJSONError::ArchiveError(e.to_string()))?;
                zip.write_all(&buffer).map_err(|e| BEJSONError::ArchiveError(e.to_string()))?;
            } else if !name.as_os_str().is_empty() {
                zip.add_directory(name.to_str().unwrap(), options).map_err(|e| BEJSONError::ArchiveError(e.to_string()))?;
            }
        }

        zip.finish().map_err(|e| BEJSONError::ArchiveError(e.to_string()))?;
        
        fs::rename(temp_arc, dest_p).map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;
        Ok(())
    }
}

/// Atomic write with directory fsync parity.
pub fn atomic_write<P: AsRef<Path>>(path: P, doc: &BEJSONDocument, create_backup: bool) -> Result<()> {
    let path = path.as_ref();
    let target_dir = path.parent().ok_or_else(|| BEJSONError::WriteFailed("Invalid path".to_string()))?;
    
    if create_backup && path.exists() {
        let ts = Local::now().format("%Y%m%d_%H%M%S").to_string();
        let backup_path = target_dir.join(format!("{}.backup.{}", path.file_name().unwrap().to_str().unwrap(), ts));
        fs::copy(path, backup_path).map_err(|e| BEJSONError::BackupFailed(e.to_string()))?;
    }

    let json_text = serde_json::to_string_pretty(doc)
        .map_err(|e| BEJSONError::InvalidOperation(e.to_string()))?;

    // Create temp file as sibling
    let mut temp_file = tempfile::NamedTempFile::new_in(target_dir)
        .map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;
    
    temp_file.write_all(json_text.as_bytes()).map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;
    temp_file.flush().map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;
    temp_file.as_file().sync_all().map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;

    // Rename and fsync directory
    temp_file.persist(path).map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;
    
    // Sync parent directory
    let dir = fs::File::open(target_dir).map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;
    dir.sync_all().map_err(|e| BEJSONError::WriteFailed(e.to_string()))?;

    Ok(())
}

/// Coerce and validate a raw JSON value to the declared field type.
pub fn _coerce_value(value: &Value, field_type: &str) -> Result<Value> {
    match field_type {
        "string" => Ok(Value::String(value.to_string().replace("\"", ""))),
        "integer" | "number" => {
            if field_type == "integer" {
                if let Some(i) = value.as_i64() { return Ok(Value::Number(i.into())); }
                if let Ok(i) = value.to_string().replace("\"", "").parse::<i64>() { return Ok(Value::Number(i.into())); }
            } else {
                if let Some(f) = value.as_f64() { return Ok(Value::from(f)); }
                if let Ok(f) = value.to_string().replace("\"", "").parse::<f64>() { return Ok(Value::from(f)); }
            }
            Err(BEJSONError::TypeConversionFailed(format!("Cannot convert '{}' to {}", value, field_type)))
        },
        "boolean" => {
            if let Some(b) = value.as_bool() { return Ok(Value::Bool(b)); }
            let s = value.to_string().replace("\"", "").to_lowercase();
            if s == "true" { return Ok(Value::Bool(true)); }
            if s == "false" { return Ok(Value::Bool(false)); }
            Err(BEJSONError::TypeConversionFailed(format!("Cannot convert '{}' to boolean", value)))
        },
        _ => Ok(value.clone()),
    }
}
