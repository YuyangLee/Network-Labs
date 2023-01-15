#!/bin/bash
set -e

cargo build --release
cp target/release/network_exp4_driver ../driver
