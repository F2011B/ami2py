#[derive(Debug, Clone, Default)]
pub struct Date {
    pub year: u16,
    pub month: u8,
    pub day: u8,
    pub hour: u8,
    pub minute: u8,
    pub second: u8,
    pub milli_sec: u16,
    pub micro_sec: u16,
    pub reserved: u8,
    pub is_future: u8,
}

pub fn reverse_bits(byte: u8) -> u8 {
    byte.reverse_bits()
}

pub fn read_date(bytes: &[u8]) -> Option<Date> {
    if bytes.len() < 8 { return None; }
    let mut arr = [0u8;8];
    arr.copy_from_slice(&bytes[..8]);
    let value = u64::from_le_bytes(arr);
    Some(Date{
        year: (value >> 52) as u16,
        month: ((value >> 48) & 0x0F) as u8,
        day: ((value >> 43) & 0x1F) as u8,
        hour: ((value >> 38) & 0x1F) as u8,
        minute: ((value >> 32) & 0x3F) as u8,
        second: ((value >> 26) & 0x3F) as u8,
        milli_sec: ((value >> 16) & 0x3FF) as u16,
        micro_sec: ((value >> 6) & 0x3FF) as u16,
        reserved: ((value & 0xE) >> 1) as u8,
        is_future: (value & 0x1) as u8,
    })
}

pub fn create_float(bytes: &[u8]) -> Option<f32> {
    if bytes.len() < 4 { return None; }
    let mut arr = [0u8;4];
    arr.copy_from_slice(&bytes[..4]);
    Some(f32::from_le_bytes(arr))
}

pub fn float_to_bin(value: f32) -> [u8;4] {
    value.to_le_bytes()
}

pub fn date_to_bin(day: u8, month: u8, year: u16, hour: u8, minute: u8, second: u8, micro_sec: u16, milli_sec: u16) -> [u8;8] {
    let val: u64 = ((year as u64) << 52)
        | ((month as u64) << 48)
        | ((day as u64) << 43)
        | ((hour as u64) << 38)
        | ((minute as u64) << 32)
        | ((second as u64) << 26)
        | ((milli_sec as u64) << 16)
        | ((micro_sec as u64) << 6);
    val.to_le_bytes()
}
