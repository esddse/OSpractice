#! /usr/bin/expect -f

spawn su - root
expect "Password:"
send "root\r"
interact