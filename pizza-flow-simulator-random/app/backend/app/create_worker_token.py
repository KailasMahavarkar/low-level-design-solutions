#!/usr/bin/env python3
import sys
from access_control.worker import create_worker_token

def generate_token(pop_id: str):
    return create_worker_token(pop_id)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <Worker ID>")
        sys.exit(1)
    pop_id = sys.argv[1]
    token = generate_token(pop_id)
    print(token)
    sys.exit(0)
