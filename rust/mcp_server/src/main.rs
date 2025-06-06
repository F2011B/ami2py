use anyhow::Result;
use mcpr::{
    schema::common::ToolInputSchema,
    server::{Server, ServerConfig},
    transport::stdio::StdioTransport,
    Tool,
};
use ami2rs::amidatabase::AmiDataBase;
use serde::Serialize;
use serde_json::Value;
use std::sync::Arc;

#[derive(Serialize)]
struct QuoteRow {
    year: u16,
    month: u8,
    day: u8,
    open: f32,
    high: f32,
    low: f32,
    close: f32,
    volume: f32,
}

fn main() -> Result<()> {
    let cfg = ServerConfig::new()
        .with_name("ami2py MCP Server")
        .with_version(env!("CARGO_PKG_VERSION"))
        .with_tool(Tool {
            name: "list_symbols".into(),
            description: Some("Return all symbols in an AmiBroker DB".into()),
            input_schema: ToolInputSchema {
                r#type: "object".into(),
                properties: None,
                required: None,
            },
        })
        .with_tool(Tool {
            name: "get_ohlc".into(),
            description: Some("Return OHLCV rows for a symbol".into()),
            input_schema: ToolInputSchema {
                r#type: "object".into(),
                properties: None,
                required: None,
            },
        });

    let mut srv: Server<StdioTransport> = Server::new(cfg);
    let db = Arc::new(AmiDataBase::new("./db")?);

    {
        let db = db.clone();
        srv.register_tool_handler("list_symbols", move |_params: Value| {
            let vec = db.get_symbols().to_vec();
            Ok(serde_json::to_value(vec)?)
        })?;
    }

    {
        let db = db.clone();
        srv.register_tool_handler("get_ohlc", move |params: Value| {
            let sym: String = params["symbol"].as_str().unwrap_or("").into();
            let quotes = db.list_quotes(&sym)?;
            let rows: Vec<QuoteRow> = quotes.into_iter().map(|q| QuoteRow {
                year: q.year,
                month: q.month,
                day: q.day,
                open: q.open,
                high: q.high,
                low: q.low,
                close: q.close,
                volume: q.volume,
            }).collect();
            Ok(serde_json::to_value(rows)?)
        })?;
    }

    srv.start(StdioTransport::new())?;
    Ok(())
}
