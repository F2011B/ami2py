use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList};
use std::fs;
use std::path::Path;
use rust_ami::amireader as base;

const MASTER_ENTRY_SIZE: usize = 1172;
const SYMBOL_HEADER_SIZE: usize = 0x4A0; // 1184
const SYMBOL_ENTRY_SIZE: usize = 40;

#[pyclass]
pub struct AmiReader {
    inner: base::AmiReader,
    master: Py<PyAny>,
}

#[pymethods]
impl AmiReader {
    #[new]
    #[pyo3(signature = (folder, use_compiled=false))]
    fn new(py: Python<'_>, folder: &str, use_compiled: bool) -> PyResult<Self> {
        let inner = base::AmiReader::new(folder).map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        let path = Path::new(folder).join("broker.master");
        let data = fs::read(&path).map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        let (master, _symbols) = parse_master(py, &data)?;
        Ok(AmiReader { inner, master })
    }

    fn get_master(&self, py: Python<'_>) -> PyResult<PyObject> {
        Ok(self.master.to_object(py))
    }

    fn get_symbols(&self) -> Vec<String> {
        self.inner.symbols.clone()
    }

    fn get_fast_symbol_data(&self, py: Python<'_>, symbol_name: &str) -> PyResult<PyObject> {
        let data = self.inner.read_symbol_bytes(symbol_name).map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        let module = PyModule::import_bound(py, "ami2py.ami_symbol_facade")?;
        let cls = module.getattr("AmiSymbolDataFacade")?;
        let obj = cls.call1((PyBytes::new_bound(py, &data),))?;
        Ok(obj.into())
    }

    fn get_symbol_data_dictionary(&self, py: Python<'_>, symbol_name: &str) -> PyResult<PyObject> {
        let data = self.inner.read_symbol_bytes(symbol_name).map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        let entries = parse_symbol_entries(&data[SYMBOL_HEADER_SIZE..]);
        let dict = entries_to_dict(py, &entries)?;
        Ok(dict.to_object(py))
    }

    fn get_symbol_data(&self, py: Python<'_>, symbol_name: &str) -> PyResult<PyObject> {
        let data = self.inner.read_symbol_bytes(symbol_name).map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        parse_symbol_dataclass(py, &data)
    }
}

#[pymodule]
fn rust_amireader(_py: Python<'_>, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<AmiReader>()?;
    Ok(())
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

fn parse_master(py: Python<'_>, data: &[u8]) -> PyResult<(Py<PyAny>, Vec<String>)> {
    if data.len() < 12 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("master file too small"));
    }
    let header = &data[..8];
    let num = u32::from_le_bytes(data[8..12].try_into().unwrap()) as usize;
    let dc = PyModule::import_bound(py, "ami2py.ami_dataclasses")?;
    let master_data_cls = dc.getattr("MasterData")?;
    let master_entry_cls = dc.getattr("MasterEntry")?;
    let py_entries = PyList::empty_bound(py);
    let mut symbols = Vec::with_capacity(num);
    let mut offset = 12;
    for _ in 0..num {
        if offset + MASTER_ENTRY_SIZE > data.len() {
            break;
        }
        let entry = &data[offset..offset + MASTER_ENTRY_SIZE];
        let symbol_bytes = &entry[..492];
        let end = symbol_bytes.iter().position(|&b| b == 0).unwrap_or(symbol_bytes.len());
        let symbol = String::from_utf8_lossy(&symbol_bytes[..end]).to_string();
        let rest = &entry[492 + 16..];
        let rest_obj = PyBytes::new_bound(py, rest);
        let kwargs = PyDict::new_bound(py);
        kwargs.set_item("Symbol", symbol.clone())?;
        kwargs.set_item("Rest", rest_obj)?;
        let entry_obj = master_entry_cls.call((), Some(&kwargs))?;
        py_entries.append(entry_obj)?;
        symbols.push(symbol);
        offset += MASTER_ENTRY_SIZE;
    }
    let kwargs = PyDict::new_bound(py);
    kwargs.set_item("Header", PyBytes::new_bound(py, header))?;
    kwargs.set_item("NumSymbols", symbols.len())?;
    kwargs.set_item("Symbols", py_entries)?;
    let master = master_data_cls.call((), Some(&kwargs))?;
    Ok((master.into(), symbols))
}

struct Entry {
    day: u8,
    month: u8,
    year: u16,
    hour: u8,
    minute: u8,
    second: u8,
    milli_sec: u16,
    micro_sec: u16,
    reserved: u8,
    future: u8,
    close: f32,
    open: f32,
    high: f32,
    low: f32,
    volume: f32,
    aux1: f32,
    aux2: f32,
    terminator: f32,
}

fn parse_symbol_entries(data: &[u8]) -> Vec<Entry> {
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
        entries.push(Entry { day, month, year, hour, minute, second, milli_sec, micro_sec, reserved, future, close, open, high, low, volume, aux1, aux2, terminator });
        offset += SYMBOL_ENTRY_SIZE;
    }
    entries
}

fn entries_to_dict<'py>(py: Python<'py>, entries: &[Entry]) -> PyResult<Bound<'py, PyDict>> {
    let dict = PyDict::new_bound(py);
    let day: Vec<u8> = entries.iter().map(|e| e.day).collect();
    let month: Vec<u8> = entries.iter().map(|e| e.month).collect();
    let year: Vec<u16> = entries.iter().map(|e| e.year).collect();
    let open: Vec<f32> = entries.iter().map(|e| e.open).collect();
    let high: Vec<f32> = entries.iter().map(|e| e.high).collect();
    let low: Vec<f32> = entries.iter().map(|e| e.low).collect();
    let close: Vec<f32> = entries.iter().map(|e| e.close).collect();
    let volume: Vec<f32> = entries.iter().map(|e| e.volume).collect();
    dict.set_item("Day", PyList::new_bound(py, day))?;
    dict.set_item("Month", PyList::new_bound(py, month))?;
    dict.set_item("Year", PyList::new_bound(py, year))?;
    dict.set_item("Open", PyList::new_bound(py, open))?;
    dict.set_item("High", PyList::new_bound(py, high))?;
    dict.set_item("Low", PyList::new_bound(py, low))?;
    dict.set_item("Close", PyList::new_bound(py, close))?;
    dict.set_item("Volume", PyList::new_bound(py, volume))?;
    Ok(dict)
}

fn parse_symbol_dataclass(py: Python<'_>, data: &[u8]) -> PyResult<PyObject> {
    let dc = PyModule::import_bound(py, "ami2py.ami_dataclasses")?;
    let symbol_entry_cls = dc.getattr("SymbolEntry")?;
    let symbol_data_cls = dc.getattr("SymbolData")?;
    let entries = parse_symbol_entries(&data[SYMBOL_HEADER_SIZE..]);
    let py_entries = PyList::empty_bound(py);
    for e in entries {
        let obj = symbol_entry_cls.call0()?;
        obj.setattr("Month", e.month)?;
        obj.setattr("Year", e.year)?;
        obj.setattr("Close", e.close)?;
        obj.setattr("Open", e.open)?;
        obj.setattr("Low", e.low)?;
        obj.setattr("High", e.high)?;
        obj.setattr("Volume", e.volume)?;
        obj.setattr("Future", e.future)?;
        obj.setattr("Reserved", e.reserved)?;
        obj.setattr("Micro_second", e.micro_sec)?;
        obj.setattr("Milli_sec", e.milli_sec)?;
        obj.setattr("Second", e.second)?;
        obj.setattr("Minute", e.minute)?;
        obj.setattr("Hour", e.hour)?;
        obj.setattr("Day", e.day)?;
        obj.setattr("Aux_1", e.aux1)?;
        obj.setattr("Aux_2", e.aux2)?;
        obj.setattr("Terminator", e.terminator)?;
        py_entries.append(obj)?;
    }
    let kwargs = PyDict::new_bound(py);
    kwargs.set_item("Header", PyBytes::new_bound(py, &data[..SYMBOL_HEADER_SIZE]))?;
    kwargs.set_item("Entries", py_entries)?;
    let obj = symbol_data_cls.call((), Some(&kwargs))?;
    Ok(obj.into())
}

