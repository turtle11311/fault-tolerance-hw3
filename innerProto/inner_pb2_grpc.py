# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from innerProto import inner_pb2 as inner__pb2


class eVotingReplicaStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateElection = channel.unary_unary(
                '/voting.eVotingReplica/CreateElection',
                request_serializer=inner__pb2.Election.SerializeToString,
                response_deserializer=inner__pb2.Status.FromString,
                )
        self.CastVote = channel.unary_unary(
                '/voting.eVotingReplica/CastVote',
                request_serializer=inner__pb2.Vote.SerializeToString,
                response_deserializer=inner__pb2.Status.FromString,
                )
        self.GetResult = channel.unary_unary(
                '/voting.eVotingReplica/GetResult',
                request_serializer=inner__pb2.ElectionName.SerializeToString,
                response_deserializer=inner__pb2.ElectionResult.FromString,
                )
        self.ElectionRecovery = channel.unary_unary(
                '/voting.eVotingReplica/ElectionRecovery',
                request_serializer=inner__pb2.Elections.SerializeToString,
                response_deserializer=inner__pb2.Status.FromString,
                )


class eVotingReplicaServicer(object):
    """Missing associated documentation comment in .proto file."""

    def CreateElection(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CastVote(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetResult(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ElectionRecovery(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_eVotingReplicaServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateElection': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateElection,
                    request_deserializer=inner__pb2.Election.FromString,
                    response_serializer=inner__pb2.Status.SerializeToString,
            ),
            'CastVote': grpc.unary_unary_rpc_method_handler(
                    servicer.CastVote,
                    request_deserializer=inner__pb2.Vote.FromString,
                    response_serializer=inner__pb2.Status.SerializeToString,
            ),
            'GetResult': grpc.unary_unary_rpc_method_handler(
                    servicer.GetResult,
                    request_deserializer=inner__pb2.ElectionName.FromString,
                    response_serializer=inner__pb2.ElectionResult.SerializeToString,
            ),
            'ElectionRecovery': grpc.unary_unary_rpc_method_handler(
                    servicer.ElectionRecovery,
                    request_deserializer=inner__pb2.Elections.FromString,
                    response_serializer=inner__pb2.Status.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'voting.eVotingReplica', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class eVotingReplica(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def CreateElection(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/voting.eVotingReplica/CreateElection',
            inner__pb2.Election.SerializeToString,
            inner__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CastVote(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/voting.eVotingReplica/CastVote',
            inner__pb2.Vote.SerializeToString,
            inner__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetResult(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/voting.eVotingReplica/GetResult',
            inner__pb2.ElectionName.SerializeToString,
            inner__pb2.ElectionResult.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ElectionRecovery(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/voting.eVotingReplica/ElectionRecovery',
            inner__pb2.Elections.SerializeToString,
            inner__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
