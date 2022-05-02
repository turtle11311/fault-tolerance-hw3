#!/usr/bin/env python3

from common.server import eVotingServer
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    srv = eVotingServer(
        addr='[::]:50001', 
        election_loc='primary/election.json',
        result_loc='primary/result.json',
        replicas=['[::]:50002']
        )
    srv.serve()