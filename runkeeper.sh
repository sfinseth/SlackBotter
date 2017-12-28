#!/bin/sh

if ! screen -list | grep -q "ExampleBot"
then
    screen -d -m -S ExampleBot python3 /home/ubuntu/ChatOps/SlackBotter/bin/example.py
fi
