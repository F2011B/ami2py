use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::env;

fn usage() {
    eprintln!("ami_cli <command> [args]");
    eprintln!("Commands:");
    eprintln!("  create <db_path> <symbol1> [symbol2 ...]");
    eprintln!("  add-symbol <db_path> <symbol1> [symbol2 ...]");
    eprintln!("  list-symbols <db_path>");
    eprintln!("  list-quotes <db_path> <symbol> [start YYYY-MM-DD end YYYY-MM-DD]");
    eprintln!("  add-quotes <db_path> <symbol> <csv_file>");
}

fn parse_date(s: &str) -> Option<(i32,i32,i32)> {
    let parts: Vec<&str> = s.split('-').collect();
    if parts.len() != 3 { return None; }
    Some((parts[0].parse().ok()?, parts[1].parse().ok()?, parts[2].parse().ok()?))
}

fn print_quotes(dict: &PyDict, start: Option<(i32,i32,i32)>, end: Option<(i32,i32,i32)>) -> PyResult<()> {
    let days: Vec<i32> = dict.get_item("Day")?.unwrap().extract::<Vec<i32>>()?;
    let months: Vec<i32> = dict.get_item("Month")?.unwrap().extract::<Vec<i32>>()?;
    let years: Vec<i32> = dict.get_item("Year")?.unwrap().extract::<Vec<i32>>()?;
    let open: Vec<f64> = dict.get_item("Open")?.unwrap().extract::<Vec<f64>>()?;
    let high: Vec<f64> = dict.get_item("High")?.unwrap().extract::<Vec<f64>>()?;
    let low: Vec<f64> = dict.get_item("Low")?.unwrap().extract::<Vec<f64>>()?;
    let close: Vec<f64> = dict.get_item("Close")?.unwrap().extract::<Vec<f64>>()?;
    let volume: Vec<f64> = dict.get_item("Volume")?.unwrap().extract::<Vec<f64>>()?;

    for i in 0..days.len() {
        let date = (years[i], months[i], days[i]);
        if let Some(s) = start { if date < s { continue; } }
        if let Some(e) = end { if date > e { continue; } }
        println!("{year:04}-{month:02}-{day:02} O={open:.2} H={high:.2} L={low:.2} C={close:.2} V={volume}",
                 year=years[i], month=months[i], day=days[i],
                 open=open[i], high=high[i], low=low[i], close=close[i], volume=volume[i]);
    }
    Ok(())
}

fn main() -> PyResult<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 { usage(); return Ok(()); }
    let command = args[1].as_str();
    Python::with_gil(|py| {
        let ami2py = PyModule::import(py, "ami2py")?;
        let cls = ami2py.getattr("AmiDataBase")?;
        match command {
            "create" => {
                if args.len() < 4 { usage(); return Ok(()); }
                let db = cls.call1((&args[2],))?;
                for s in &args[3..] { db.call_method1("add_symbol", (s,))?; }
                db.call_method0("write_database")?;
            }
            "add-symbol" => {
                if args.len() < 4 { usage(); return Ok(()); }
                let db = cls.call1((&args[2],))?;
                for s in &args[3..] { db.call_method1("add_symbol", (s,))?; }
                db.call_method0("write_database")?;
            }
            "list-symbols" => {
                if args.len() != 3 { usage(); return Ok(()); }
                let db = cls.call1((&args[2],))?;
                let syms: Vec<String> = db.call_method0("get_symbols")?.extract()?;
                for s in syms { println!("{}", s); }
            }
            "list-quotes" => {
                if args.len() < 4 { usage(); return Ok(()); }
                let start = if args.len() >=5 { parse_date(&args[4]) } else { None };
                let end = if args.len() >=6 { parse_date(&args[5]) } else { None };
                let db = cls.call1((&args[2],))?;
                let dict: &PyDict = db.call_method1("get_dict_for_symbol", (&args[3],))?.downcast()?;
                print_quotes(dict, start, end)?;
            }
            "add-quotes" => {
                if args.len() != 5 { usage(); return Ok(()); }
                let db = cls.call1((&args[2],))?;
                let locals = PyDict::new(py);
                locals.set_item("path", &args[4])?;
                py.run(r#"
import csv
rows = []
with open(path, newline='') as f:
    r = csv.DictReader(f)
    for row in r:
        y,m,d = [int(x) for x in row['Date'].split('-')]
        rows.append({'Day':d,'Month':m,'Year':y,'Open':float(row['Open']),'High':float(row['High']),
                     'Low':float(row['Low']),'Close':float(row['Close']),'Volume':float(row['Volume'])})
"#, None, Some(locals))?;
                let rows = locals.get_item("rows").unwrap();
                db.call_method1("append_to_symbol", (&args[3], rows))?;
                db.call_method0("write_database")?;
            }
            _ => usage(),
        }
        Ok(())
    })
}
