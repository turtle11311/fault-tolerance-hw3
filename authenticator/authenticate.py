from __future__ import annotations
import base64
import logging
import json
import time
import jsonschema
from random import Random
from typing import Dict, Tuple
import time
from nacl.signing import VerifyKey
from nacl.exceptions import ValueError, BadSignatureError

class TokenInvalidError(Exception):
    def __str__(self) -> str:
        return "token Invalid"

class Voter():
    def __init__(self, name: str, group: str, pub_key: bytes) -> None:
        self.name = name
        self.group = group
        self.pub_key = pub_key
        self._auth_state: AuthState = UnAuthenticatedState(self)
        
    class JSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Voter):
                return {'name': obj.name, 'group': obj.group, 'public_key': base64.b64encode(obj.pub_key).decode('utf-8')}
            # Let the base class default method raise the TypeError
            return json.JSONEncoder.default(self, obj)
    
class AuthState():
    def __init__(self, voter: Voter) -> None:
        self.context: Voter = voter
        self._state_name: str = "UNSPECIFY"
    def __str__(self) -> str:
        return self._state_name
    def set_state(self, state: AuthState) -> None:
        logging.debug('Voter[{}] from {} to {}'.format(self.context.name, self.context._auth_state, state))
        self.context._auth_state = state

class UnAuthenticatedState(AuthState):
    def __init__(self, voter: Voter) -> None:
        super().__init__(voter)
        self._state_name: str = "UNAUTHENTICATE"
    def raise_challange(self) -> bytes:
        challange = Random().randbytes(32)
        self.set_state(RaiseChallangeState(self.context, challange))
        return challange

class RaiseChallangeState(AuthState):
    def __init__(self, voter: Voter, challange: bytes) -> None:
        super().__init__(voter)
        self.challange: bytes = challange
        self._state_name: str = "CHALLANGING CLIENT"
    def check_response(self, response: bytes) -> Tuple[bool,bytes]:
        try:
            VerifyKey(self.context.pub_key).verify(smessage=self.challange, signature=response)
            authorized_token = Random().randbytes(32)
            self.set_state(AuthenticatedState(self.context, authorized_token))
            return True, authorized_token
        except ValueError as e:
            logging.warning("Voter[{}] authorize fail: {}".format(self.name, e))
            return False, b''
        except TypeError as e:
            logging.warning("Voter[{}] authorize fail: {}".format(self.name, e))
            return False, b''
        except BadSignatureError as e:
            logging.warning("Voter[{}] authorize fail: {}".format(self.name, e))
            return False, b''
        except:
            logging.warning("Voter[{}] authorize fail: UNSPECIFY".format(self.name))
            return False, b''

class AuthenticatedState(AuthState):
    def __init__(self, voter: Voter, token: bytes) -> None:
        super().__init__(voter)
        self._state_name: str = "AUTHENTICATE"
        self.token = token
        self.expiry_time = time.time() + (60 * 60)
    def verify_token(self, token: bytes) -> None:
        if self.expiry_time < time.time():
            self.set_state(UnAuthenticatedState(self.context))
            raise TokenInvalidError()
        if token != self.token:
            raise TokenInvalidError()

class Authenticator():
    def __init__(self, db_loc: str):
        self.db_loc = db_loc
        self.voters: Dict[str, Voter] = dict()
        self.token_owner: Dict[bytes, str] = dict()
        self.schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "VoterDB",
            "type": "array",
            "items": {
                "$ref": "#/definitions/voter"
            },
            "definitions": {
                "voter": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "group": {
                            "type": "string"
                        },
                        "public_key": {
                            "type": "string",
                            "pattern": "^(?:[A-Za-z0-9+/]{4}){10}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$"
                        }
                    }
                }
            }
        }
        try:
            with open(self.db_loc, 'r') as voter_dbs:
                voter_collections = json.load(voter_dbs)
                jsonschema.validate(voter_collections, schema=self.schema)
                for voter_data in voter_collections:
                    name = voter_data['name']
                    group = voter_data['group']
                    pub_key = base64.b64decode(voter_data['public_key'])
                    self.voters[name] = Voter(name=name, group=group, pub_key=pub_key)
        except FileNotFoundError:
            with open(self.db_loc, 'w') as voter_dbs:
                voter_dbs.close()
                logging.warning('{} not exist, create it'.format(self.db_loc))
        except jsonschema.ValidationError as e:
            logging.error('db file is corrupted: {}'.format(e))
            exit(1)
    def raise_challange(self, name: str) -> bytes:
        voter = self.voters[name]
        if not isinstance(voter._auth_state, UnAuthenticatedState):
            voter._auth_state.set_state(UnAuthenticatedState(voter))
        return voter._auth_state.raise_challange()
    def authorize(self, name: str, sign: bytes) -> Tuple[bool, bytes]:
        voter = self.voters[name]
        if isinstance(voter._auth_state, RaiseChallangeState):
            ok, token = voter._auth_state.check_response(sign)
            if ok:
                self.token_owner[token] = name
            return ok, token
        else:
            return False, b''
    def verify_token(self, token: bytes) -> Voter:
        try:
            name = self.token_owner[token]
            voter = self.voters[name]
        except KeyError:
            raise TokenInvalidError()

        if isinstance(voter._auth_state, AuthenticatedState):
            voter._auth_state.verify_token(token)
            return voter
        else:
            raise TokenInvalidError()
