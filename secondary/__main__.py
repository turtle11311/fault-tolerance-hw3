#!/usr/bin/env python3

from audioop import add
from common.server import eVotingServer
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    srv = eVotingServer(
        addr='[::]:50002',
        election_loc='secondary/election.json',
        result_loc='secondary/result.json',
    )
    srv.serve()