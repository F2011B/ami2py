use pyo3::prelude::*;

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
    let gil = Python::acquire_gil();
    let py = gil.python();
    let dict = PyDict::new(py);
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
}

#[pymodule]
fn rust_bitparser(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(reverse_bits, m)?)?;
    m.add_function(wrap_pyfunction!(read_date, m)?)?;
    Ok(())
}
