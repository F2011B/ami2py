use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::Path;

#[derive(Debug)]
pub struct AmiReader {
    pub folder: String,
    pub symbols: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct Quote {
    pub day: u8,
    pub month: u8,
    pub year: u16,
    pub hour: u8,
    pub minute: u8,
    pub second: u8,
    pub milli_sec: u16,
    pub micro_sec: u16,
    pub reserved: u8,
    pub future: u8,
    pub close: f32,
    pub open: f32,
    pub high: f32,
    pub low: f32,
    pub volume: f32,
    pub aux1: f32,
    pub aux2: f32,
    pub terminator: f32,
}

const SYMBOL_HEADER_SIZE: usize = 0x4A0;
pub const SYMBOL_ENTRY_SIZE: usize = 40;
impl AmiReader {
    pub fn new(folder: &str) -> std::io::Result<Self> {
        let path = Path::new(folder).join("broker.master");
        let data = match fs::read(&path) {
            Ok(d) => d,
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => Vec::new(),
            Err(e) => return Err(e),
        };
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

    pub fn read_quotes(&self, symbol: &str) -> std::io::Result<Vec<Quote>> {
        let data = self.read_symbol_bytes(symbol)?;
        Ok(parse_symbol_entries(&data[SYMBOL_HEADER_SIZE..]))
    }

    pub fn last_time_stamp(&self, symbol: &str) -> std::io::Result<Option<(u16, u8, u8)>> {
        let quotes = self.read_quotes(symbol)?;
        Ok(quotes.last().map(|q| (q.year, q.month, q.day)))
    }

    pub fn append_quotes(&self, symbol: &str, quotes: &[Quote]) -> std::io::Result<()> {
        let p = symbol_path(&self.folder, symbol);
        let mut file = OpenOptions::new().append(true).create(true).open(p)?;
        for q in quotes {
            let bytes = quote_to_bytes(q);
            file.write_all(&bytes)?;
        }
        Ok(())
    }
}

const MASTER_ENTRY_SIZE: usize = 1172;

fn parse_symbol_entries(data: &[u8]) -> Vec<Quote> {
    let mut entries = Vec::new();
    let mut offset = 0;
    while offset + SYMBOL_ENTRY_SIZE <= data.len() {
        let chunk = &data[offset..offset + SYMBOL_ENTRY_SIZE];
        let val = u64::from_le_bytes(chunk[..8].try_into().unwrap());
        let year = (val >> 52) as u16;
        let month = ((val >> 48) & 0x0F) as u8;
        let day = ((val >> 43) & 0x1F) as u8;
        let hour = ((val >> 38) & 0x1F) as u8;
        let minute = ((val >> 32) & 0x3F) as u8;
        let second = ((val >> 26) & 0x3F) as u8;
        let milli_sec = ((val >> 16) & 0x3FF) as u16;
        let micro_sec = ((val >> 6) & 0x3FF) as u16;
        let reserved = ((val & 0xE) >> 1) as u8;
        let future = (val & 0x1) as u8;
        let close = f32::from_le_bytes(chunk[8..12].try_into().unwrap());
        let open = f32::from_le_bytes(chunk[12..16].try_into().unwrap());
        let high = f32::from_le_bytes(chunk[16..20].try_into().unwrap());
        let low = f32::from_le_bytes(chunk[20..24].try_into().unwrap());
        let volume = f32::from_le_bytes(chunk[24..28].try_into().unwrap());
        let aux1 = f32::from_le_bytes(chunk[28..32].try_into().unwrap());
        let aux2 = f32::from_le_bytes(chunk[32..36].try_into().unwrap());
        let terminator = f32::from_le_bytes(chunk[36..40].try_into().unwrap());
        entries.push(Quote { day, month, year, hour, minute, second, milli_sec, micro_sec, reserved, future, close, open, high, low, volume, aux1, aux2, terminator });
        offset += SYMBOL_ENTRY_SIZE;
    }
    entries
}

fn quote_to_bytes(q: &Quote) -> [u8; SYMBOL_ENTRY_SIZE] {
    let mut out = [0u8; SYMBOL_ENTRY_SIZE];
    let val: u64 = ((q.year as u64) << 52)
        | ((q.month as u64) << 48)
        | ((q.day as u64) << 43)
        | ((q.hour as u64) << 38)
        | ((q.minute as u64) << 32)
        | ((q.second as u64) << 26)
        | ((q.milli_sec as u64) << 16)
        | ((q.micro_sec as u64) << 6)
        | ((q.reserved as u64) << 1)
        | (q.future as u64);
    out[..8].copy_from_slice(&val.to_le_bytes());
    out[8..12].copy_from_slice(&q.close.to_le_bytes());
    out[12..16].copy_from_slice(&q.open.to_le_bytes());
    out[16..20].copy_from_slice(&q.high.to_le_bytes());
    out[20..24].copy_from_slice(&q.low.to_le_bytes());
    out[24..28].copy_from_slice(&q.volume.to_le_bytes());
    out[28..32].copy_from_slice(&q.aux1.to_le_bytes());
    out[32..36].copy_from_slice(&q.aux2.to_le_bytes());
    out[36..40].copy_from_slice(&q.terminator.to_le_bytes());
    out
}

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
