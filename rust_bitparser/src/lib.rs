#![allow(unsafe_op_in_unsafe_fn)]

use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::types::PyByteArray;

#[pyfunction]
fn reverse_bits(byte_data: u8) -> u8 {
    byte_data.reverse_bits()
}

#[pyfunction]
fn read_date(date_tuple: Vec<u8>) -> PyResult<PyObject> {
    if date_tuple.len() < 8 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("expected 8 bytes"));
    }
    let mut bytes = [0u8; 8];
    bytes.copy_from_slice(&date_tuple[..8]);
    let value = u64::from_le_bytes(bytes);
    Python::with_gil(|py| {
        let dict = PyDict::new_bound(py);
        dict.set_item("Year", value >> 52)?;
        dict.set_item("Month", (value >> 48) & 0x0Fu64)?;
        dict.set_item("Day", (value >> 43) & 0x1Fu64)?;
        dict.set_item("Hour", (value >> 38) & 0x1Fu64)?;
        dict.set_item("Minute", (value >> 32) & 0x3Fu64)?;
        dict.set_item("Second", (value >> 26) & 0x3Fu64)?;
        dict.set_item("MilliSec", (value >> 16) & 0x3FFu64)?;
        dict.set_item("MicroSec", (value >> 6) & 0x3FFu64)?;
        dict.set_item("Reserved", value & 0xEu64)?;
        dict.set_item("Isfut", value & 0x1u64)?;
        Ok(dict.to_object(py))
    })
}

#[pyfunction]
fn create_float(float_tuple: Vec<u8>) -> PyResult<f32> {
    if float_tuple.len() < 4 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("expected 4 bytes"));
    }
    let mut bytes = [0u8; 4];
    bytes.copy_from_slice(&float_tuple[..4]);
    Ok(f32::from_le_bytes(bytes))
}

#[pyfunction]
fn float_to_bin(py: Python<'_>, value: f32) -> PyResult<PyObject> {
    let bytes = value.to_le_bytes();
    Ok(PyByteArray::new_bound(py, &bytes).to_object(py))
}

#[pyfunction(signature = (day, month, year, hour=0u8, minute=0u8, second=0u8, mic_sec=0u16, milli_sec=0u16))]
fn date_to_bin(
    py: Python<'_>,
    day: u8,
    month: u8,
    year: u16,
    hour: u8,
    minute: u8,
    second: u8,
    mic_sec: u16,
    milli_sec: u16,
) -> PyResult<PyObject> {
    let mut result = [0u8; 8];
    result[7] = (year >> 4) as u8;
    result[6] = (result[6] & 0x0F) + (((year << 4) as u8) & 0xF0);
    result[6] = (result[6] & 0xF0) + (month & 0x0F);
    result[5] = ((day << 3) as u8) + (result[5] & 0xF8);
    Ok(PyByteArray::new_bound(py, &result).to_object(py))
}

#[pymodule]
fn rust_bitparser(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(reverse_bits, m)?)?;
    m.add_function(wrap_pyfunction!(read_date, m)?)?;
    m.add_function(wrap_pyfunction!(create_float, m)?)?;
    m.add_function(wrap_pyfunction!(float_to_bin, m)?)?;
    m.add_function(wrap_pyfunction!(date_to_bin, m)?)?;
    Ok(())
}
