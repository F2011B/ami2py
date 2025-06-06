use pyo3::prelude::*;

pub mod amireader;
pub mod amidatabase;
pub mod bitparser;

#[pymodule]
fn rust_amireader(py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    amireader::rust_amireader(py, m)
}

#[pymodule]
fn rust_amidatabase(py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    amidatabase::rust_amidatabase(py, m)
}

#[pymodule]
fn rust_bitparser(py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    bitparser::rust_bitparser(py, m)
}
