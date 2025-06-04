use rust_amidatabase::AmiDataBase;
use std::env;

fn usage() {
    eprintln!("ami_cli <command> [args]");
    eprintln!("Commands:");
    eprintln!("  create <db_path> <symbol1> [symbol2 ...]");
    eprintln!("  add-symbol <db_path> <symbol1> [symbol2 ...]");
    eprintln!("  list-symbols <db_path>");
    eprintln!("\n<db_path> should point to the AmiBroker database folder containing broker.master.");
    eprintln!("If the path contains spaces, wrap it in quotes.");
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
            if args.len() != 3 {
                eprintln!("Error: 'list-symbols' expects a single <db_path> argument pointing to the database folder containing broker.master.");
                usage();
                return;
            }
            let db = AmiDataBase::new(&args[2]).expect("open db");
            for s in db.get_symbols() { println!("{}", s); }
        }
        _ => usage(),
    }
}
