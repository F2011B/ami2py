use std::fs;
use std::path::Path;

#[derive(Debug)]
pub struct AmiReader {
    pub folder: String,
    pub symbols: Vec<String>,
}

impl AmiReader {
    pub fn new(folder: &str) -> std::io::Result<Self> {
        let path = Path::new(folder).join("broker.master");
        let data = fs::read(&path)?;
        let (_, symbols) = parse_master(&data);
        Ok(AmiReader { folder: folder.to_string(), symbols })
    }

    pub fn get_symbols(&self) -> &[String] {
        &self.symbols
    }

    pub fn read_symbol_bytes(&self, symbol: &str) -> std::io::Result<Vec<u8>> {
        let p = symbol_path(&self.folder, symbol);
        fs::read(p)
    }
}

const MASTER_ENTRY_SIZE: usize = 1172;

fn parse_master(data: &[u8]) -> (Vec<u8>, Vec<String>) {
    if data.len() < 12 { return (Vec::new(), Vec::new()); }
    let header = data[..8].to_vec();
    let num = u32::from_le_bytes(data[8..12].try_into().unwrap()) as usize;
    let mut symbols = Vec::with_capacity(num);
    let mut offset = 12;
    while offset + MASTER_ENTRY_SIZE <= data.len() {
        let entry = &data[offset..offset + MASTER_ENTRY_SIZE];
        let symbol_bytes = &entry[..492];
        let end = symbol_bytes.iter().position(|&b| b == 0).unwrap_or(symbol_bytes.len());
        let symbol = String::from_utf8_lossy(&symbol_bytes[..end]).to_string();
        symbols.push(symbol);
        offset += MASTER_ENTRY_SIZE;
    }
    (header, symbols)
}

fn symbol_root_folder(symbol: &str) -> String {
    if symbol.starts_with('^') || symbol.starts_with('~') || symbol.starts_with('@') {
        "_".to_string()
    } else {
        symbol.chars().next().unwrap_or(' ').to_ascii_lowercase().to_string()
    }
}

fn symbol_path(root: &str, symbol: &str) -> String {
    if symbol.eq_ignore_ascii_case("broker.master") {
        Path::new(root).join(symbol).to_string_lossy().into_owned()
    } else {
        let folder = symbol_root_folder(symbol);
        Path::new(root).join(folder).join(symbol).to_string_lossy().into_owned()
    }
}
