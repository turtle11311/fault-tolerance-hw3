#!/usr/bin/env python3
from __future__ import annotations
import logging
import grpc
from concurrent import futures
from proto import inner_pb2
from proto.voting_pb2_grpc import eVotingServicer, add_eVotingServicer_to_server
from proto.voting_pb2 import Challenge, AuthToken, ElectionResult, Status
from proto.inner_pb2_grpc import eVotingReplicaStub
from authenticator.authenticate import Authenticator, TokenInvalidError

class eVotingRPCDispatcher(eVotingServicer):
    def __init__(self) -> None:
        self.authenticator = Authenticator('voters.json')
        self.server_list = ['[::]:50001', '[::]:50002']
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
        status = 0
        try:
            token = request.token.value
            self.authenticator.verify_token(token)
        except TokenInvalidError as e:
            logging.warning(e)
            status = 1
            return Status(code=status)
        for addr in self.server_list:
            channel = grpc.insecure_channel(addr)
            stub = eVotingReplicaStub(channel=channel)
            try:
                rsp = stub.CreateElection(request)
            except grpc.RpcError as e:
                pass
        if rsp == None:
            return Status(code=5)
        return Status(code=rsp.code)
    def CastVote(self, request, context):
        status = 0
        try:
            token = request.token.value
            voter = self.authenticator.verify_token(token)
        except TokenInvalidError as e:
            logging.warning(e)
            status = 1
            return Status(code=status)
        
        for addr in self.server_list:
            channel = grpc.insecure_channel(addr)
            stub = eVotingReplicaStub(channel=channel)
            try:
                rsp = stub.CastVote(inner_pb2.Vote(
                    election_name=request.election_name,
                    choice_name=request.choice_name,
                    voter=inner_pb2.Voter(name=voter.name, group=voter.group))
                )
            except grpc.RpcError as e:
                continue
        if rsp == None:
            return Status(code=5)
        return Status(code=rsp.code)
    def GetResult(self, request, context):
        status = 0
        try:
            token = request.token.value
            self.authenticator.verify_token(token)
        except TokenInvalidError as e:
            logging.warning(e)
            status = 1
            return Status(code=status)
        
        for addr in self.server_list:
            channel = grpc.insecure_channel(addr)
            stub = eVotingReplicaStub(channel=channel)
            try:
                rsp = stub.GetResult(request)
            except grpc.RpcError as e:
                logging.warn("{}".format(e))
                continue
        if rsp == None:
            return ElectionResult(status=Status(code=3))
        return rsp
    
    def serve(self):
        try:
            self._grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            add_eVotingServicer_to_server(self, self._grpc_server)
            self._grpc_server.add_insecure_port('[::]:8000')
            self._grpc_server.start()
            self._grpc_server.wait_for_termination()
        except KeyboardInterrupt:
            pass
