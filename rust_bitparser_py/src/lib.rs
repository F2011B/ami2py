#![allow(unsafe_op_in_unsafe_fn)]

use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyDict};
use rust_bitparser as base;

#[pyfunction]
fn reverse_bits(byte_data: u8) -> u8 {
    base::reverse_bits(byte_data)
}

#[pyfunction]
fn read_date(date_tuple: Vec<u8>) -> PyResult<PyObject> {
    if date_tuple.len() < 8 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("expected 8 bytes"));
    }
    let data = base::read_date(&date_tuple).ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("expected 8 bytes"))?;
    Python::with_gil(|py| {
        let dict = PyDict::new_bound(py);
        dict.set_item("Year", data.year)?;
        dict.set_item("Month", data.month)?;
        dict.set_item("Day", data.day)?;
        dict.set_item("Hour", data.hour)?;
        dict.set_item("Minute", data.minute)?;
        dict.set_item("Second", data.second)?;
        dict.set_item("MilliSec", data.milli_sec)?;
        dict.set_item("MicroSec", data.micro_sec)?;
        dict.set_item("Reserved", data.reserved)?;
        dict.set_item("Isfut", data.is_future)?;
        Ok(dict.to_object(py))
    })
}

#[pyfunction]
fn create_float(float_tuple: Vec<u8>) -> PyResult<f32> {
    if float_tuple.len() < 4 {
        return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("expected 4 bytes"));
    }
    base::create_float(&float_tuple).ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("expected 4 bytes"))
}

#[pyfunction]
fn float_to_bin(py: Python<'_>, value: f32) -> PyResult<PyObject> {
    let bytes = base::float_to_bin(value);
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
    let bytes = base::date_to_bin(day, month, year, hour, minute, second, mic_sec, milli_sec);
    Ok(PyByteArray::new_bound(py, &bytes).to_object(py))
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
