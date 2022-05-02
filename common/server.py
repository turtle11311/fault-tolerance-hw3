from __future__ import annotations
from array import array
from concurrent import futures
import logging
import json
import time
import jsonschema
from typing import Dict, List
import time
from google.protobuf.timestamp_pb2 import Timestamp

import grpc
from proto import inner_pb2_grpc
from proto import inner_pb2
from proto import voting_pb2

class ElectionSpecError(Exception):
    def __init__(self, election_name: str) -> None:
        super().__init__()
        self.election_name = election_name
    def __str__(self) -> str:
        return "Election[{}] provide wrong parameters".format(self.election_name)

class InvalidElecitonNameError(Exception):
    def __init__(self, election_name: str) -> None:
        super().__init__()
        self.election_name = election_name
    def __str__(self) -> str:
        return "Election[{}] not exists".format(self.election_name)

class ElectionOngoingException(Exception):
    def __init__(self, election_name: str) -> None:
        super().__init__()
        self.election_name = election_name
    def __str__(self) -> str:
        return "Election[{}] still ongoing. election result is not available yet.".format(self.voter_name, self.election_name)

class VoterGroupError(Exception):
    def __init__(self, election_name: str, voter_name: str) -> None:
        super().__init__()
        self.election_name = election_name
        self.voter_name = voter_name
    def __str__(self) -> str:
        return "Voter[{}] isn't allow for election {}".format(self.voter_name, self.election_name)

class HasBeenVotedError(Exception):
    def __init__(self, election_name: str, voter_name: str) -> None:
        super().__init__()
        self.election_name = election_name
        self.voter_name = voter_name
    def __str__(self) -> str:
        return "Voter[{}] is casted before in election {}".format(self.voter_name, self.election_name)

class Voter():
    def __init__(self, name: str, group: str) -> None:
        self.name = name
        self.group = group

class Election():
    def __init__(self, name: str, groups: array, choices: array, end_date: str) -> None:
        self.name = name
        self.groups = groups
        self.choices = choices
        self.end_date = end_date
        
    class JSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Election):
                return {'name': obj.name, 'groups': obj.groups, 'choices': obj.choices, 'end_date': obj.end_date}
            # Let the base class default method raise the TypeError
            return json.JSONEncoder.default(self, obj)

class ElectDataLoader():
    def __init__(self, election_loc: str = './election.json', result_loc: str = './result.json'):
        self.election_loc = election_loc
        self.result_loc = result_loc
        self.elections: Dict[str, Election] = dict()
        self.schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "ElectDB",
            "type": "array",
            "items": {
                "$ref": "#/definitions/election"
            },
            "definitions": {
                "election": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "groups": {
                            "type": "array"
                        },
                        "choices": {
                            "type": "array"
                        },
                        "end_date": {
                            "type": "string"
                        }
                    }
                }
            }
        }
        try:
            with open(self.election_loc, 'r') as elect_dbs:
                elect_collections = json.load(elect_dbs)
                jsonschema.validate( elect_collections, schema=self.schema)
                for elect_data in elect_collections:
                    name = elect_data['name']
                    groups = elect_data['groups']
                    choices = elect_data['choices']
                    end_date = elect_data['end_date']
                    self.elections[name] = Election(name=name, groups=groups, choices=choices ,end_date=end_date)
        except FileNotFoundError:
            with open(self.election_loc, 'w') as elect_dbs:
                json.dump([], elect_dbs)
                elect_dbs.close()
                logging.warning('{} not exist, create it'.format(self.election_loc))
            with open(self.result_loc, 'w') as electResult_dbs:
                json.dump([], electResult_dbs)
                electResult_dbs.close()
                logging.warning('{} not exist, create it'.format(self.result_loc))
        except jsonschema.ValidationError as e:
            logging.error('db file is corrupted: {}'.format(e))
            exit(1)

    def CreateResultList(self, name: str, choices: array):
        with open(self.result_loc, 'r') as electResult_dbs:
            data = json.load(electResult_dbs)
            electResult_dbs.close()
        with open(self.result_loc, 'w') as electResult_dbs:
            dict_choices = dict.fromkeys(choices,0) # list convert to dict
            data.append({ \
                'name': name, \
                'choices': dict_choices, \
                'voters' : []
            })
            json.dump(data, fp=electResult_dbs)
            electResult_dbs.close()

    def CreateElect(self, name: str, groups: array, choices: array, end_date: array):
        # election is existing error
        if name in self.elections:
            raise ElectionSpecError(name)
        # at least one group and one choice 
        if not len(groups) or not len(choices):
            raise ElectionSpecError(name)
        self.elections[name] = Election(name=name, groups=list(groups), choices=list(choices) ,end_date=str(end_date.ToJsonString()))
        with open(self.election_loc, 'w') as elect_dbs:
            json.dump(list(map(lambda v: v[1],self.elections.items())),fp=elect_dbs,cls=Election.JSONEncoder)
            elect_dbs.close()
        self.CreateResultList(name=name, choices=list(choices))
    
    def UpdateResultList(self, voter: Voter, election_name: str, choice_name: str):
        try:
            election = self.elections[election_name]
        except KeyError:
            raise InvalidElecitonNameError(election_name)
        if voter.group not in election.groups:
            raise VoterGroupError(election_name, voter)
        election_index = list(self.elections).index(election_name)
        with open(self.result_loc, 'r') as electResult_dbs:
            data = json.load(electResult_dbs)
            electResult_dbs.close()
        if voter.name in data[election_index]['voters']:
            raise HasBeenVotedError(election_name, voter.name)
        with open(self.result_loc, 'w') as electResult_dbs:
            data[election_index]['choices'][choice_name]+=1
            data[election_index]['voters'].append(voter.name)
            json.dump(data, fp=electResult_dbs)
            electResult_dbs.close()
            
    def GetResultList(self, election_name: str) -> List[Election]:
        if election_name not in self.elections:
            raise InvalidElecitonNameError(election_name)
        election_index = list(self.elections).index(election_name)
        elecTime = Timestamp()
        CurrentTime = time.time()
        elecTime.FromJsonString(self.elections[election_name].end_date)
        if int(elecTime.seconds) > int(CurrentTime): 
            # The election is still ongoing. Election result is not available yet.
            return 1,[]
        with open(self.result_loc, 'r') as electResult_dbs:
            data = json.load(electResult_dbs)
            electResult_dbs.close()
        return data[election_index]['choices']

    def retrieveData(self):
        with open(self.result_loc, 'r') as electResult_dbs:
            ResultData = json.load(electResult_dbs)
            electResult_dbs.close()
        with open(self.election_loc, 'r') as elect_dbs:
            ElectionData = json.load(elect_dbs)
            elect_dbs.close()
        return ResultData, ElectionData
    
    def recoverData(self, rsp: inner_pb2.Elections):
        ElectionData = []
        ResultData = []
        for election in rsp.elections:
            ElectionData.append({
                "name": election.name,
                "groups": list(election.groups),
                "choices": list(election.choices),
                "end_date": str(election.end_date.ToJsonString())
            })
            choices = dict()
            for count in election.count:
                choices[count.choice_name] = count.count
            ResultData.append({
                "name": election.name,
                "choices": choices,
                "voters": list(election.voters)
            })
        with open(self.result_loc, 'w') as electResult_dbs:
            json.dump(obj=ResultData, fp=electResult_dbs)
            electResult_dbs.close()
        with open(self.election_loc, 'w') as elect_dbs:
            json.dump(obj=ElectionData, fp=elect_dbs)
            elect_dbs.close()
        

class eVotingServer(inner_pb2_grpc.eVotingReplicaServicer):
    def __init__(self, addr: str, election_loc: str, result_loc: str, replicas: List[str] = []) -> None:
        self.electDB = ElectDataLoader(election_loc, result_loc)
        self.srv_addr = addr
        if replicas != []:
            for replica_addr in replicas:
                self.recoverFromReplica(replica_addr)
                
    def recoverFromReplica(self, replica_addr: str):
        try:
            with grpc.insecure_channel(replica_addr) as channel:
                recovery_stub = inner_pb2_grpc.eVotingReplicaStub(channel)
                rsp = recovery_stub.ElectionRecovery(inner_pb2.ElectionRecoveryRequest())
                self.electDB.recoverData(rsp)
        except grpc.RpcError as e:
            pass

    def CreateElection(self, request, context):
        status = 0
        logging.info("Create election [{}]".format(request.name))
        try:
            self.electDB.CreateElect(request.name, request.groups, request.choices, request.end_date)
        except ElectionSpecError as e:
            logging.warning(e)
            status = 2
        except Exception as e:
            logging.warning(e)
            # Unknown error
            status = 3
        finally:
            return voting_pb2.Status(code=status)

    def CastVote(self, request, context):
        logging.info("Voter[{}] cast election [{}]".format(request.voter.name, request.election_name))
        status = 0
        try:
            self.electDB.UpdateResultList(Voter(request.voter.name, request.voter.group), request.election_name, request.choice_name)
            return voting_pb2.Status(code=0)
        except InvalidElecitonNameError as e:
            logging.warning(e)
            status = 2
        except VoterGroupError as e:
            logging.warning(e)
            status = 3
        except HasBeenVotedError as e:
            logging.warning(e)
            status = 4
        except Exception as e:
            logging.warning(e.with_traceback())
            # Unknown error
            status = 5
        finally:
            return voting_pb2.Status(code=status)

    def GetResult(self,request, context):
        logging.info("get result")
        status = 0
        try:
            GetResult_dic = self.electDB.GetResultList(request.name)
            count = []
            #logging.info(GetResult_dic)
            for key in GetResult_dic:
                count.append(inner_pb2.VoteCount(choice_name=key, count=GetResult_dic[key]))
        except InvalidElecitonNameError as e:
            logging.warning(e)
            status = 1
            count = []
        finally:
            return inner_pb2.ElectionResult( \
                status = status, \
                count = count)
    def ElectionRecovery(self, request, context):
        logging.info("primary recovery election data")
        try:
            ResultData, ElectionData = self.electDB.retrieveData()
            election = []
            for i in range(len(ResultData)):
                count = []
                end_time = Timestamp()
                end_time.FromJsonString(ElectionData[i]['end_date'])
                choice_list = ResultData[i]['choices']
                for key in choice_list:
                    count.append(voting_pb2.VoteCount(choice_name=key, count=choice_list[key]))
                
                election.append(inner_pb2.ElectionStatus(
                    name = ResultData[i]['name'],
                    groups = ElectionData[i]['groups'],
                    choices = ElectionData[i]['choices'],
                    count = count,
                    voters = ResultData[i]['voters'],
                    end_date = end_time
                ))
        except grpc.RpcError as e:
            logging.error(e)
        except Exception as e:
            logging.error(e)
        finally:
            return inner_pb2.Elections(elections = election)
    def serve(self):
        try:
            self._grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
            inner_pb2_grpc.add_eVotingReplicaServicer_to_server(self, self._grpc_server)
            self._grpc_server.add_insecure_port(self.srv_addr)
            self._grpc_server.start()
            self._grpc_server.wait_for_termination()
        except KeyboardInterrupt:
            pass