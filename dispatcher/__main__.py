#!/usr/bin/env python3

from dispatcher.dispatcher import eVotingRPCDispatcher
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    srv = eVotingRPCDispatcher()
    srv.serve()