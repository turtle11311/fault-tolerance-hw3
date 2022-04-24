#!/usr/bin/env python3
from __future__ import annotations
import logging
import grpc
from concurrent import futures
from proto.voting_pb2_grpc import eVotingServicer, add_eVotingServicer_to_server
from proto.voting_pb2 import Challenge, AuthToken
from authenticator.authenticate import Authenticator

class eVotingRPCDispatcher(eVotingServicer):
    def __init__(self) -> None:
        self.authenticator = Authenticator('voters.json')
    def PreAuth(self, request, context):
        name = request.name
        try: 
            challange = self.authenticator.raise_challange(name)
            return Challenge(value=challange)
        except KeyError:
            logging.warning('voter[{}] is not registed in server'.format(name))
            return Challenge(value=b'')
    def Auth(self, request, context):
        name = request.name.name
        signature = request.response.value
        try:
            authorized, token = self.authenticator.authorize(name, signature)
            if authorized:
                logging.info('voter[{}] is authorize with token'.format(name))
                return AuthToken(value=token)
            else:
                logging.warning('voter[{}] is authentication failed'.format(name))
                return AuthToken(value=b'')
        except KeyError:
            logging.warning('voter[{}] is not registed in server'.format(name))
            return AuthToken(value=b'')
    def CreateElection(self, request, context):
        pass
    def CastVote(self, request, context):
        pass
    def GetResult(self,request, context):
        pass
    
    def serve(self):
        try:
            self._grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            add_eVotingServicer_to_server(self, self._grpc_server)
            self._grpc_server.add_insecure_port('[::]:50051')
            self._grpc_server.start()
            self._grpc_server.wait_for_termination()
        except KeyboardInterrupt:
            pass
