use serde::{Deserialize, Serialize};
use serde_json::Value;
use thiserror::Error;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum BEJSONVersion {
    #[serde(rename = "104")]
    V104,
    #[serde(rename = "104a")]
    V104a,
    #[serde(rename = "104db")]
    V104db,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BEJSONField {
    pub name: String,
    #[serde(rename = "type")]
    pub field_type: String,
    #[serde(rename = "Record_Type_Parent")]
    pub record_type_parent: Option<String>,
    #[serde(flatten)]
    pub extra: serde_json::Map<String, Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BEJSONDocument {
    #[serde(rename = "Format")]
    pub format: String,
    #[serde(rename = "Format_Version")]
    pub format_version: BEJSONVersion,
    #[serde(rename = "Format_Creator")]
    pub format_creator: String,
    #[serde(rename = "Records_Type")]
    pub records_type: Vec<String>,
    #[serde(rename = "Fields")]
    pub fields: Vec<BEJSONField>,
    #[serde(rename = "Values")]
    pub values: Vec<Vec<Value>>,
    #[serde(flatten)]
    pub extra_headers: serde_json::Map<String, Value>,
}

#[derive(Error, Debug)]
pub enum BEJSONError {
    #[error("Invalid version ({0})")]
    InvalidVersion(u32),
    #[error("Invalid operation: {0}")]
    InvalidOperation(String),
    #[error("Index out of bounds: {0}")]
    IndexOutOfBounds(usize),
    #[error("Field not found: {0}")]
    FieldNotFound(String),
    #[error("Type conversion failed: {0}")]
    TypeConversionFailed(String),
    #[error("Backup failed: {0}")]
    BackupFailed(String),
    #[error("Write failed: {0}")]
    WriteFailed(String),
    #[error("Query failed: {0}")]
    QueryFailed(String),
    #[error("Archive error: {0}")]
    ArchiveError(String),
    #[error("Mount conflict: {0}")]
    MountConflict(String),
}

pub type Result<T> = std::result::Result<T, BEJSONError>;

// Official Error Codes
pub const E_CORE_INVALID_VERSION: u32 = 20;
pub const E_CORE_INVALID_OPERATION: u32 = 21;
pub const E_CORE_INDEX_OUT_OF_BOUNDS: u32 = 22;
pub const E_CORE_FIELD_NOT_FOUND: u32 = 23;
pub const E_CORE_TYPE_CONVERSION_FAILED: u32 = 24;
pub const E_CORE_BACKUP_FAILED: u32 = 25;
pub const E_CORE_WRITE_FAILED: u32 = 26;
pub const E_CORE_QUERY_FAILED: u32 = 27;
pub const E_CORE_ARCHIVE_ERROR: u32 = 70;
pub const E_CORE_MOUNT_CONFLICT: u32 = 71;
