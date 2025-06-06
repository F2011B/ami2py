use rust_ami::amidatabase::AmiDataBase;
use std::env;

fn usage() {
    eprintln!("ami_cli <command> [args]");
    eprintln!("Commands:");
    eprintln!("  create <db_path> <symbol1> [symbol2 ...]");
    eprintln!("  add-symbol <db_path> <symbol1> [symbol2 ...]");
    eprintln!("  list-symbols <db_path>");
    eprintln!("  get_last_time_stamp <db_path> <symbol>");
    eprintln!("  list-quotes <db_path> <symbol> [start YYYY-MM-DD end YYYY-MM-DD]");
    eprintln!("  add-quotes <db_path> <symbol> <csv_file>");
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 { usage(); return; }
    let command = args[1].as_str();
    match command {
        "create" => {
            if args.len() < 4 { usage(); return; }
            let mut db = AmiDataBase::new(&args[2]).expect("create db");
            for s in &args[3..] { db.add_symbol(s).ok(); }
            db.write_database().ok();
        }
        "add-symbol" => {
            if args.len() < 4 { usage(); return; }
            let mut db = AmiDataBase::new(&args[2]).expect("open db");
            for s in &args[3..] { db.add_symbol(s).ok(); }
            db.write_database().ok();
        }
        "list-symbols" => {
            if args.len() != 3 { usage(); return; }
            let db = AmiDataBase::new(&args[2]).expect("open db");
            for s in db.get_symbols() { println!("{}", s); }
        }
        "get_last_time_stamp" => {
            if args.len() != 4 { usage(); return; }
            let db = AmiDataBase::new(&args[2]).expect("open db");
            match db.get_last_time_stamp(&args[3]).expect("read symbol") {
                Some((y,m,d)) => println!("{:04}-{:02}-{:02}", y, m, d),
                None => println!("no data"),
            }
        }
        "list-quotes" => {
            if args.len() != 4 && args.len() != 8 { usage(); return; }
            let db = AmiDataBase::new(&args[2]).expect("open db");
            let quotes = db.list_quotes(&args[3]).expect("read symbol");
            let mut start = None;
            let mut end = None;
            if args.len() == 8 {
                if args[4] == "start" { start = parse_date(&args[5]); }
                if args[6] == "end" { end = parse_date(&args[7]); }
            }
            for q in &quotes {
                let val = q.year as i32 * 10000 + q.month as i32 * 100 + q.day as i32;
                if start.map_or(true, |s| val >= s) && end.map_or(true, |e| val <= e) {
                    println!("{:04}-{:02}-{:02},{},{},{},{},{}", q.year, q.month, q.day, q.open, q.high, q.low, q.close, q.volume);
                }
            }
        }
        "add-quotes" => {
            if args.len() != 5 { usage(); return; }
            let db = AmiDataBase::new(&args[2]).expect("open db");
            db.add_quotes_from_csv(&args[3], &args[4]).expect("add quotes");
        }
        _ => usage(),
    }
}

fn parse_date(s: &str) -> Option<i32> {
    let parts: Vec<&str> = s.split('-').collect();
    if parts.len() != 3 { return None; }
    let y: i32 = parts[0].parse().ok()?;
    let m: i32 = parts[1].parse().ok()?;
    let d: i32 = parts[2].parse().ok()?;
    Some(y * 10000 + m * 100 + d)
}
