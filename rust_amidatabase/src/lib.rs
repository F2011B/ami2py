use std::path::Path;
use std::fs::{self, OpenOptions};
use std::io::Write;
use rust_amireader::{AmiReader, Quote};

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

    pub fn get_last_time_stamp(&self, symbol: &str) -> std::io::Result<Option<(u16, u8, u8)>> {
        self.reader.last_time_stamp(symbol)
    }

    pub fn list_quotes(&self, symbol: &str) -> std::io::Result<Vec<Quote>> {
        self.reader.read_quotes(symbol)
    }

    pub fn add_quotes(&self, symbol: &str, quotes: &[Quote]) -> std::io::Result<()> {
        self.reader.append_quotes(symbol, quotes)
    }

    pub fn add_quotes_from_csv(&self, symbol: &str, csv_path: &str) -> std::io::Result<()> {
        let content = fs::read_to_string(csv_path)?;
        let mut quotes = Vec::new();
        for (i, line) in content.lines().enumerate() {
            if i == 0 { continue; }
            let parts: Vec<&str> = line.split(',').collect();
            if parts.len() < 6 { continue; }
            let date_parts: Vec<&str> = parts[0].split('-').collect();
            if date_parts.len() != 3 { continue; }
            let year: u16 = date_parts[0].parse().unwrap_or(0);
            let month: u8 = date_parts[1].parse().unwrap_or(0);
            let day: u8 = date_parts[2].parse().unwrap_or(0);
            let open: f32 = parts[1].parse().unwrap_or(0.0);
            let high: f32 = parts[2].parse().unwrap_or(0.0);
            let low: f32 = parts[3].parse().unwrap_or(0.0);
            let close: f32 = parts[4].parse().unwrap_or(0.0);
            let volume_idx = if parts.len() > 6 { 6 } else { 5 };
            let volume: f32 = parts[volume_idx].parse().unwrap_or(0.0);
            quotes.push(Quote {
                day,
                month,
                year,
                hour: 0,
                minute: 0,
                second: 0,
                milli_sec: 0,
                micro_sec: 0,
                reserved: 0,
                future: 0,
                close,
                open,
                high,
                low,
                volume,
                aux1: 0.0,
                aux2: 0.0,
                terminator: 0.0,
            });
        }
        self.add_quotes(symbol, &quotes)
    }
}

fn symbol_root_folder(symbol: &str) -> String {
    if symbol.starts_with('^') || symbol.starts_with('~') || symbol.starts_with('@') {
        "_".to_string()
    } else {
        symbol.chars().next().unwrap_or(' ').to_ascii_lowercase().to_string()
    }
}
