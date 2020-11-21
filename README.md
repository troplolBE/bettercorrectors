# BetterCorrectors

_**!!! PROJECT IS NOT FINISHED YET, IT IS STILL WIP !!!**_

BetterCorrectors is a python project coded to find 'bad students' who made 'bad evaluations' during specified period of time.
The script returns a timestamp of when the evaluation took place and the login of the users who are responsible for this correction.
The definition of a bad evaluation is strictly personnal and could not fit your requirements, for more information about that, please read [pedagody](PEDAGO.md) 

## Installation

Download the repo using git.

```bash
git clone https://gihub.com/troplolBE/ThePunisher.git
```

Use pip to install the requirements
```bash
pip install -r requirements.txt
```

## Usage

## Documentation
Document containing all the references and links to docs I used for the project.
All documentation will be listed and referenced by type or by subject.

### API-42

The 42 api is a REST api that works with OAuth2. You need to have a 42 account to be able to generate a token to access 
the api. The api gives you access to all the data of the students and much more. Thanks to this api we can retrieve the 
needed data for 'bad evaluations'.

To gather a bearer token via curl use following command:
```bash
curl -X POST --data "grant_type=client_credentials&client_id=MY_AWESOME_UID&client_secret=MY_AWESOME_SECRET" https://api.intra.42.fr/oauth/token
```

All data from the api is in json format and is paged. If you use the parameters `page[number]` and `page[size]` you can 
define how many results you have on one page and which page you would like to consult.

Multiple endpoints are available for us to use in this project. The most intresting one is the _Scale Team_ endpoit.

For more info read [api documentiation](https://api.intra.42.fr/apidoc/guides/specification)

#### Scale Team

The scale team endpoint is the endpoint for an evaluation. It contains all the information of an evaluation. We can even
see at what time the evaluation started and when the evaluation stopped. We can gather all the necessary information to 
make sure that an evaluation is bad or not. (to be verified by a human, always)

Sample of complete returned data [sample 1](#sample-1)

Here is a non-exhaustive list of intresting data for detection:
- final_mark
- begin_at
- filled_at
- flag
- comment
- feedback

### Pyhton