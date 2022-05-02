# fault-tolerance-hw3
## System Architecture
* Dispatcher
> Handle authentication from client and dispatch message to replica node
* Primary
> Primary node in our system, it will recover the data from secondary if it ocurrs crash error.
* Secondary
> Secondary node will store election and its result. 

## How to Run?

### Normal Case
```bash
python3 -m dispatcher
```

```bash
python3 -m primary
```

```bash
python3 -m secondary
```

```bash
python3 -m eVoter
```

Check `election.json` and `result.json` in secondary and primary

* election.json
```json
[
  {
    "name": "Election1", 
    "groups": ["student", "teacher"], 
    "choices": ["number1", "number2"], 
    "end_date": "2023-01-01T00:00:00Z"
  }
]
```

* result.json
```json
[
  {
    "name": "Election1",
    "choices": {
      "number1": 1,
      "number2": 0
    },
    "voters": ["Hello"]
  }
]
```

## Crush Case
```bash
python3 -m dispatcher
```

```bash
python3 -m primary
```

```bash
python3 -m secondary
```

```bash
python3 -m eVoter
```

Ctrl-C to stop **primary**, and continue Vote.
After cast the vote, then open **primary**.

Check `election.json` and `result.json` in secondary and primary