/// 这是SDK内置的代码，主要是与driver进行通信的逻辑。
/// 正常情况下，你应该也不需要阅读本文件的代码，只要读api文件，然后完成outgoing文件就好。
/// 此文件通常不用改动。但如果你有确切的理由，也可以自行改动，但请务必确保你清楚自己在做什么！
/// 助教评阅时，会使用你上传的版本。
use std::fs::remove_file;
use std::os::unix::net::UnixDatagram;
use std::time::Duration;

use anyhow::{anyhow, Result};
use bson::spec::BinarySubtype;
use lazy_static::lazy_static;
use serde::{Deserialize, Serialize};

use crate::api::{ConnectionIdentifier, IpAndPort};

mod api;
mod outgoing;

fn main() {
    // 向服务器发送初次连接的通告
    sdk_event(&ConnectionIdentifier { src: IpAndPort { ip: String::from("127.84.0.1"), port: 8484 }, dst: IpAndPort { ip: String::new(), port: 0 } }, "network_exp4".as_bytes(), 0xa0);
    let mut buf = [0u8; 500000];
    println!("已启动！");
    loop {
        if let Err(e) = unix_socket_recv(&mut buf) {
            eprintln!("unix_socket_recv FAILED: {e}")
        }
    }
}

lazy_static! {
    static ref UNIX_SOCK: UnixDatagram = (|| {
        remove_file("/tmp/network-exp4-sdk.socket").ok();
        let sock = UnixDatagram::bind("/tmp/network-exp4-sdk.socket").unwrap();
        loop {
            if let Err(e) = sock.connect("/tmp/network-exp4-driver.socket") {
                if e.raw_os_error() == Some(1) { // Operation not permitted
                    println!("等待服务端UnixSocket资源释放(约500ms)...(若持续出现此信息，请检查自己是否开着另一个SDK进程)");
                    std::thread::sleep(Duration::from_millis(500));
                    continue;
                } else { Err::<(), std::io::Error>(e).unwrap(); }
            }
            break;
        }
        sock
    })();
}

#[derive(Clone, Serialize, Deserialize)]
struct Event<'a> {
    conn: ConnectionIdentifier,
    bytes: &'a [u8],
    flags: u32,
}

pub(crate) fn sdk_event(conn: &ConnectionIdentifier, bytes: &[u8], flags: u32) {
    let event = Event { conn: conn.clone(), bytes: bytes, flags };
    if let Err(e) = unix_socket_send(event) {
        eprintln!("unix_socket_send FAILED: {e}")
    }
}

fn unix_socket_send(event: Event) -> Result<()> {
    // 不能直接对event使用to_vec，否则字符串数组会被序列化成sequence<i32>。必须手动声明其为Binary的
    let mut bson_obj = bson::to_document(&event)?;
    bson_obj.insert("bytes", bson::Binary { subtype: BinarySubtype::Generic, bytes: Vec::from(event.bytes) });
    let data = bson::to_vec(&bson_obj)?;
    UNIX_SOCK.send(&data[..])?;
    Ok(())
}

fn unix_socket_recv(buf: &mut [u8]) -> Result<()> {
    let size = UNIX_SOCK.recv(buf)?;
    if size == 1 { // 是保活报文
        outgoing::tick();
        return Ok(());
    }
    if size >= buf.len() { return Err(anyhow!("WARNING: 收到了超过接收buffer大小({})的unix domain socket报文！该报文并未被完整接收！", buf.len())); }
    let event = bson::from_slice::<Event>(&buf[0..size])?;
    if event.flags == 0x0 {
        outgoing::app_send(&event.conn, event.bytes);
    } else if event.flags == 0x1 {
        outgoing::app_fin(&event.conn);
    } else if event.flags == 0x2 {
        outgoing::app_connect(&event.conn);
    } else if event.flags == 0x4 {
        outgoing::app_rst(&event.conn);
    } else if event.flags == 0x40 {
        outgoing::tcp_rx(&event.conn, event.bytes)
    }
    Ok(())
}