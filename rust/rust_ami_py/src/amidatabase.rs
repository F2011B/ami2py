use pyo3::prelude::*;
use pyo3::types::{PyDict, PyModule};
use rust_ami::amidatabase as base;

#[pyclass]
pub struct AmiDataBase {
    inner: base::AmiDataBase,
    py_api: Py<PyAny>,
}

#[pymethods]
impl AmiDataBase {
    #[new]
    #[pyo3(signature = (folder, use_compiled=false, avoid_windows_file=true))]
    fn new(
        py: Python,
        folder: &PyAny,
        use_compiled: bool,
        avoid_windows_file: bool,
    ) -> PyResult<Self> {
        let folder_str: String = folder.str()?.to_string();
        let inner = base::AmiDataBase::new(&folder_str).map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        let ami_module = PyModule::import_bound(py, "ami2py.ami_database")?;
        let class = ami_module.getattr("AmiDataBase")?;
        let obj = class.call1((folder_str, use_compiled, avoid_windows_file))?;
        Ok(AmiDataBase { inner, py_api: obj.into() })
    }

    fn get_symbols(&self, py: Python) -> PyResult<PyObject> {
        self.py_api.call_method0(py, "get_symbols")
    }

    fn add_symbol(&mut self, py: Python, symbol_name: &str) -> PyResult<()> {
        self.inner.add_symbol(symbol_name).map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        self.py_api.call_method1(py, "add_symbol", (symbol_name,))?;
        Ok(())
    }

    fn add_new_symbol(&self, py: Python, symbol_name: &str, symboldata: Option<PyObject>) -> PyResult<()> {
        match symboldata {
            Some(data) => { self.py_api.call_method1(py, "add_new_symbol", (symbol_name, data))?; },
            None => { self.py_api.call_method1(py, "add_new_symbol", (symbol_name,))?; }
        }
        Ok(())
    }

    fn append_symbol_entry(&self, py: Python, symbol: &str, data: PyObject) -> PyResult<()> {
        self.py_api.call_method1(py, "append_symbol_entry", (symbol, data))?;
        Ok(())
    }

    fn append_symbol_data(&self, py: Python, data: PyObject) -> PyResult<()> {
        self.py_api.call_method1(py, "append_symbol_data", (data,))?;
        Ok(())
    }

    fn add_symbol_data_dict(&self, py: Python, data: PyObject) -> PyResult<()> {
        self.py_api.call_method1(py, "add_symbol_data_dict", (data,))?;
        Ok(())
    }

    fn append_to_symbol(&self, py: Python, symbol: &str, data: PyObject) -> PyResult<()> {
        self.py_api.call_method1(py, "append_to_symbol", (symbol, data))?;
        Ok(())
    }

    #[pyo3(name = "_get_dict_for_symbol", signature = (symbol_name, force_refresh=false))]
    fn get_dict_for_symbol_inner(
        &self,
        py: Python,
        symbol_name: &str,
        force_refresh: bool,
    ) -> PyResult<PyObject> {
        self.py_api.call_method1(py, "get_dict_for_symbol", (symbol_name, force_refresh))
    }

    #[pyo3(name = "_get_fast_symbol_data", signature = (symbol_name, force_refresh=false))]
    fn get_fast_symbol_data_inner(
        &self,
        py: Python,
        symbol_name: &str,
        force_refresh: bool,
    ) -> PyResult<PyObject> {
        self.py_api.call_method1(py, "get_fast_symbol_data", (symbol_name, force_refresh))
    }

    fn write_database(&self, py: Python) -> PyResult<()> {
        self.inner.write_database().map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;
        self.py_api.call_method0(py, "write_database")?;
        Ok(())
    }
}

pub fn rust_amidatabase(py: Python<'_>, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<AmiDataBase>()?;

    let cls = m.getattr("AmiDataBase")?;
    let locals = PyDict::new(py);
    locals.set_item("cls", cls.clone())?;
    let code = r#"
def add_wrappers(cls):
    def get_dict_for_symbol(self, symbol_name, force_refresh=False):
        return self._get_dict_for_symbol(symbol_name, force_refresh)
    def get_fast_symbol_data(self, symbol_name, force_refresh=False):
        return self._get_fast_symbol_data(symbol_name, force_refresh)
    cls.get_dict_for_symbol = get_dict_for_symbol
    cls.get_fast_symbol_data = get_fast_symbol_data
"#;
    py.run(code, None, Some(locals))?;
    py.run("add_wrappers(cls)", None, Some(locals))?;
    Ok(())
}
