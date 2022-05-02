from __future__ import print_function
import base64
from os import path
from google.protobuf.timestamp_pb2 import Timestamp
from nacl.public import PrivateKey
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import Base64Encoder
from google.protobuf.timestamp_pb2 import Timestamp
import logging
import grpc
import proto.voting_pb2 as voting_pb2
import proto.voting_pb2_grpc as voting_pb2_grpc

voter_name = 'Hello'

"""
KeyLoader loads private key from file, and derived the signing key and verify key from private key.
"""
class KeyLoader():
    def __init__(self, key_path: str) -> None:
        sk: bytes = b''
        if path.exists(key_path):
            with open(key_path, 'r') as key_file:
                sk_b64 = key_file.read()
                sk = base64.b64decode(sk_b64)
                key_file.close()
        else:
            sk = PrivateKey.generate()
            with open(key_path, 'w') as key_file:
                sk_b64 = base64.b64encode(bytes(sk)).decode('utf-8')
                key_file.write(sk_b64)
                key_file.close()
        self._private_key = sk
        self._signing_key = SigningKey(seed=bytes(sk))
    @property
    def signing_key(self) -> SigningKey:
        return self._signing_key
    @property
    def verify_key(self) -> VerifyKey:
        return self._signing_key.verify_key

def run():
    key_loader = KeyLoader('voter_key')
    logging.debug('verifykey: {}'.format(key_loader.verify_key.encode(encoder=Base64Encoder).decode('utf-8')))

    with grpc.insecure_channel('localhost:8000') as channel:
        try:
            input('【Start Authentication】\nPress any key...')
            eVoting_stub = voting_pb2_grpc.eVotingStub(channel)
            rsp = eVoting_stub.PreAuth(voting_pb2.VoterName(name=voter_name))
            signature = key_loader.signing_key.sign(rsp.value)
            rsp = eVoting_stub.Auth(voting_pb2.AuthRequest(
                name=voting_pb2.VoterName(name=voter_name),
                response=voting_pb2.Response(value=signature.signature)
            ))
            token = rsp.value
            logging.debug('token[{}]'.format(token))
            if token != b'':
                logging.info('authorization successs')
        except grpc.RpcError as e:
            logging.error(e)

        input('【Start Create Elections\nPress any key...')
        try:
            Election_stub = voting_pb2_grpc.eVotingStub(channel)
            end_time = Timestamp()
            end_time.FromJsonString('2023-01-01T00:00:00Z')
            election_status = Election_stub.CreateElection(voting_pb2.Election(
                name='Election1',
                groups=['student','teacher'],
                choices=['number1','number2'],
                end_date=end_time,
                token=voting_pb2.AuthToken(value=token)))
            if election_status.code==0:
                logging.info('Election created successfully')

        except grpc.RpcError as e:
            logging.error(e)

        input('【Start CastVote\nPress any key...')

        try:
            CastVote_stub = voting_pb2_grpc.eVotingStub(channel)
            castVote_status = CastVote_stub.CastVote(voting_pb2.Vote(
                election_name='Election1',
                choice_name ='number1',
                token=voting_pb2.AuthToken(value=token)))
            if castVote_status.code==0:
                logging.info('Successful vote')
        except grpc.RpcError as e:
            logging.error(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    run()