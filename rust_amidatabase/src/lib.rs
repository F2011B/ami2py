use std::path::Path;
use std::fs::{self, OpenOptions};
use std::io::Write;
use rust_amireader::AmiReader;

pub mod reader {
    pub use rust_amireader::AmiReader;
}

pub struct AmiDataBase {
    pub folder: String,
    reader: AmiReader,
}

impl AmiDataBase {
    pub fn new(folder: &str) -> std::io::Result<Self> {
        if !Path::new(folder).exists() {
            fs::create_dir_all(folder)?;
        }
        let reader = AmiReader::new(folder)?;
        Ok(AmiDataBase { folder: folder.to_string(), reader })
    }

    pub fn get_symbols(&self) -> &[String] {
        self.reader.get_symbols()
    }

    pub fn add_symbol(&mut self, symbol: &str) -> std::io::Result<()> {
        let folder = Path::new(&self.folder);
        let symbol_file = folder.join(symbol_root_folder(symbol)).join(symbol);
        if !symbol_file.exists() {
            if let Some(parent) = symbol_file.parent() {
                fs::create_dir_all(parent)?;
            }
            // do not create an empty file here; file will be created when data is written
            self.reader.symbols.push(symbol.to_string());
        }
        Ok(())
    }

    pub fn write_database(&self) -> std::io::Result<()> {
        // simplistic implementation: touch master file
        let path = Path::new(&self.folder).join("broker.master");
        if !path.exists() {
            if let Some(parent) = path.parent() { fs::create_dir_all(parent)?; }
            let mut f = OpenOptions::new().create(true).write(true).open(path)?;
            f.write_all(b"AMI2PY")?; // placeholder
        }
        Ok(())
    }
}

fn symbol_root_folder(symbol: &str) -> String {
    if symbol.starts_with('^') || symbol.starts_with('~') || symbol.starts_with('@') {
        "_".to_string()
    } else {
        symbol.chars().next().unwrap_or(' ').to_ascii_lowercase().to_string()
    }
}
