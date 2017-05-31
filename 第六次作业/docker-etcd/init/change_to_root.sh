#! /usr/bin/expect -f

spawn su - root
expect "Password:"
send "pkucloud\r"
interact