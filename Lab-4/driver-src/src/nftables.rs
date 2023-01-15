/// 这是driver部分的源代码。不得改动！
use std::io::Write;
use std::process::{Command, Output, Stdio};

use anyhow::Result;

pub struct NftGuard {}

impl NftGuard {
    pub fn new(all: bool) -> NftGuard {
        // 如果没添加ip规则，就添加
        if get_command("ip rule list fwmark 84").output().unwrap().stdout.len() == 0 {
            run_command("ip rule add fwmark 84 lookup 84");
            println!("已配置ip rule规则")
        }
        if get_command("ip route list table 84").output().unwrap().stdout.len() == 0 {
            run_command("ip route add 0.0.0.0/0 dev lo table 84");
            println!("已配置ip route规则")
        }
        let nft_conf = include_str!("nftables.conf");
        // patch nft的规则
        let (name, match_cidr) = if all { ("all", "0.0.0.0/0") } else { ("partial", "127.84.0.0/16") };
        let patched_conf = nft_conf.replace("$MATCH_CIDR", match_cidr);

        let mut child = get_command("nft -f -").stdin(Stdio::piped()).spawn().unwrap();
        child.stdin.as_mut().unwrap().write_all(patched_conf.as_bytes()).unwrap();
        if !child.wait().unwrap().success() { panic!("配置nft规则失败！") }
        println!("已配置nftables规则，类型为{}({})", name, match_cidr);
        NftGuard {}
    }
}

impl Drop for NftGuard {
    fn drop(&mut self) {
        clear_nft();
        println!("已清除nftables规则");
    }
}

fn get_command(command: &str) -> Command {
    let components: Vec<&str> = command.split(" ").collect();
    let mut command = Command::new(components[0]);
    for i in 1..components.len() {
        command.arg(components[i]);
    }
    command
}

fn run_command(command: &str) -> Output {
    let output = get_command(command).output().unwrap();
    if !output.status.success() { panic!("执行命令{}失败！", command) }
    output
}

fn clear_nft() {
    get_command("nft delete table ip exp4").output().unwrap();
}

// 连同ip rule一起清掉
pub fn clear_all() {
    clear_nft();
    // 清除ip配置
    while get_command("ip rule list fwmark 84").output().unwrap().stdout.len() > 0 {
        get_command("ip rule delete fwmark 84").output().unwrap();
    }
    get_command("ip route flush table 84").output().unwrap();
    println!("所有配置(nftables, ip rule, ip route)已清除！")
}

fn print_one(command_str: &str) -> Result<()> {
    println!("$ {}", command_str);
    let mut command = get_command(command_str);
    println!("{}", std::str::from_utf8(&command.output()?.stdout)?);
    Ok(())
}

pub fn print_all() {
    let commands = ["ip rule list fwmark 84", "ip route list table 84", "nft list table ip exp4"];
    for command in commands {
        if let Err(_) = print_one(command) {
            println!("执行命令并获取结果的过程中发生错误！")
        }
    }
}