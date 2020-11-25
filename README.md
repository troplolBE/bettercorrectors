# BetterCorrectors

_**!!! PROJECT IS NOT FINISHED YET, IT IS STILL WIP !!!**_

BetterCorrectors is a python project coded to find 'bad students' who made 'bad evaluations' during specified period of time.
The script returns a timestamp of when the evaluation took place and the login of the users who are responsible for this correction.
The definition of a bad evaluation is strictly personnal and could not fit your requirements, for more information about that, please read [pedagody](PEDAGO.md) 

## Installation

Download the repo using git.
```bash
git clone https://gihub.com/troplolBE/bettercorrectors.git
```

Go inside of the directory.
```bash
cd bettercorrectors
```

## Usage

You can use the program with or without docker.

### With docker

First build the container.
```bash
docker build --tag bettercorrimg .
```

If everything went well you can now run the container.
```bash
docker run --rm --name bettercorrectors -v ~/result:/result bettercorrimg <params_for_program>
```

### Without docker

In case you don't want to run the program in a container, you can perfectly run it on your normal computer.

Install all packages using pip.

```bash
pip install -r requirements.txt
```

Run the program like this.
```bash
python3 main.py <params_for_program>
```

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

### Documentation samples

#### Sample 1

_Note: information in this sample has been redacted_ [(go back)](#scale-team)

```json
{
      "id":0,
      "scale_id":0,
      "comment":"Beau projet, dommage pour l'affichage de SHA256.",
      "created_at":"2020-10-29T12:36:59.459Z",
      "updated_at":"2020-10-30T15:48:16.908Z",
      "feedback":"Correcteur impliqué et intéressé. Merci pour la correction :)",
      "final_mark":101,
      "flag":{
         "id":1,
         "name":"Ok",
         "positive":true,
         "icon":"check-4",
         "created_at":"2015-09-14T23:06:52.000Z",
         "updated_at":"2015-09-14T23:06:52.000Z"
      },
      "begin_at":"2020-10-29T13:15:00.000Z",
      "correcteds":[
         {
            "id":0,
            "login":"nope",
            "url":"https://api.intra.42.fr/v2/users/nope"
         }
      ],
      "corrector":{
         "id":0,
         "login":"nope",
         "url":"https://api.intra.42.fr/v2/users/nope"
      },
      "truant":{
         
      },
      "filled_at":"2020-10-29T14:16:28.641Z",
      "questions_with_answers":[
         {
            "id":34813,
            "name":"Are they a perfectionist?",
            "guidelines":"\nDid they set up their executable to read commands from the STDIN\nand not just args?\n",
            "rating":"bool",
            "kind":"bonus",
            "answers":[
               {
                  "value":1,
                  "answer":null
               }
            ]
         },
         {
            "id":34805,
            "name":"Does FT_SSL handle commands correctly?",
            "guidelines":"\nIt doesn't have to match OpenSSL perfectly here, but it must\nmeet a few basic requirements.\n\nDoes ft_ssl handle invalid commands correctly? Does it output an\nappropriate error message?\n\nDoes ft_ssl provide a usage if no arguments are provided OR does\nit read the command from standard input?\n",
            "rating":"bool",
            "kind":"standard",
            "answers":[
               {
                  "value":1,
                  "answer":null
               }
            ]
         },
         {
            "id":34814,
            "name":"Are they prepared to out-hash the Hash Slinging Slasher?",
            "guidelines":"\nDid they add bonus hash functions? Can they prove they\naccurately hash identical to their counterpart? Are they\nconsidered stronger than MD5?\n\n(If you're unsure what to rate, the SHA family are similar and\naround 2 points each, while whirlpool is more oouah and 5 points\n;)\n",
            "rating":"multi",
            "kind":"bonus",
            "answers":[
               {
                  "value":0,
                  "answer":null
               }
            ]
         },
         {
            "id":34806,
            "name":"Did they implement a function dispatcher?",
            "guidelines":"\nYou're going to have to actually look at the code for this one.\nHow do they determine which command should be run?\n\nDo they set up a function pointer array and have a clever way of\ndispatching their commands? Or a hideous if/else monstrosity?\n\nAward no points for this question if it's only if/else\nstatments.\n\nAward only 4 points if they have to make a change in more than\ntwo places in the code every time they add a new command. Reduce\na point for each place they must make a change.\n\n(Example:: a NUM_COMMANDS macro in includes, an extra if/else,\nor adding another line to their setup_commands or equivalent\nfunction)\n",
            "rating":"multi",
            "kind":"standard",
            "answers":[
               {
                  "value":3,
                  "answer":null
               }
            ]
         },
         {
            "id":34815,
            "name":"Are they a Memer? Do they look like someone who memes?",
            "guidelines":"\nThis question has no effect on your grade, we're just starting\nour own data-mining personality quiz for the Zucc.\n",
            "rating":"bool",
            "kind":"bonus",
            "answers":[
               {
                  "value":0,
                  "answer":null
               }
            ]
         },
         {
            "id":34807,
            "name":"Can they MD5 a file?",
            "guidelines":"\nCheck that the ft_ssl md5 hashing algorithm implementation is\n100% correct. Nothing less than perfect will be accepted.\n\necho 'is md5(\"salt\") a salted hash? :thonking_face:' \u003e /tmp/file\n./ft_ssl md5 /tmp/file md5 /tmp/file openssl md5 /tmp/file\n\nThe spacing of the output does not matter as long as it matches\neither openssl or the md5 standalone.\n",
            "rating":"bool",
            "kind":"standard",
            "answers":[
               {
                  "value":1,
                  "answer":null
               }
            ]
         },
         {
            "id":34808,
            "name":"Can they do it quietly?",
            "guidelines":"\nThe following command should have no output::\n\ndiff \u003c(md5 -q /tmp/file) \u003c(./ft_ssl md5 -q /tmp/file)\n",
            "rating":"bool",
            "kind":"standard",
            "answers":[
               {
                  "value":1,
                  "answer":null
               }
            ]
         },
         {
            "id":34809,
            "name":"REVERSE REVERSE!",
            "guidelines":"\nNow you have to test that they implemented the -r flag\ncorrectly!\n\nmd5 -r /tmp/file ./ft_ssl md5 -r /tmp/file\n",
            "rating":"bool",
            "kind":"standard",
            "answers":[
               {
                  "value":1,
                  "answer":null
               }
            ]
         },
         {
            "id":34810,
            "name":"Print it back now, Y'all!",
            "guidelines":"\nThey had better be able to do this. It's just 1 write() call,\nseriously.\n\necho \"Magic mirror on the wall, think I wanna smash them all?\" |\nmd5 -p echo \"Speed up now, Gas Pedal??\" | ./ft_ssl md5 -p\n\nMy mashup skills are nowhere near as good as MD5's.\n",
            "rating":"multi",
            "kind":"standard",
            "answers":[
               {
                  "value":5,
                  "answer":null
               }
            ]
         },
         {
            "id":34811,
            "name":"SHA (Some Hipster Algorithm)",
            "guidelines":"\nEnough playing around with the suits let's do something fresh\nand hip, yeah?\n\necho \"Lorem ipsum dolor amet thundercats letterpress cray\nportland cornhole coloring book twee prism hexagon mixtape pork\nbelly hell of four dollar toast disrupt. Hammock PBR\u0026B bicycle\nrights selvage street art, lumbersexual gochujang vegan hot\nchicken. Meggings drinking vinegar biodiesel poke roof party\ntote bag cloud bread ethical. Glossier flannel 8-bit hexagon\nselvage adaptogen farm-to-table offal knausgaard pickled.\" \u003e\nsome_hipster_ipsum shasum -a 256 some_hipster_ipsum \u003e\nsome_hipster_ipsum_sum ./ft_ssl sha256 some_hipster_ipsum \u003e\nflip_some_hipsum diff some_hipster_ipsum_sum flip_some_hipsum\n",
            "rating":"bool",
            "kind":"standard",
            "answers":[
               {
                  "value":1,
                  "answer":null
               }
            ]
         },
         {
            "id":34812,
            "name":"Nigel Thornberry",
            "guidelines":"\nYou better be SMASHING the Sha Hashing flags like our favorite\ndocumentary filmmaker.\n\nYou know what flags need to be tested so I'm going to\nconsolidate all the tests into a single slider and save us both\n(mostly me) some time.\n",
            "rating":"multi",
            "kind":"standard",
            "answers":[
               {
                  "value":5,
                  "answer":null
               }
            ]
         }
      ],
      "scale":{
         "id":0,
         "evaluation_id":0,
         "name":"scale 1\n",
         "is_primary":true,
         "comment":"",
         "introduction_md":"\nIn order to maintain high evaluation standards, you are expected\nto::\n\nStay polite, courteous, respectful and constructive at every moment\nof the discussion. Trust between you and our community depends on\nyour behaviour.\n\nHighlight the flaws and issues you uncover in the turned-in work to\nthe evaluated student or team, and take the time to discuss every\naspect extensively.\n\nPlease take into account that discrepancies regarding the expected\nwork or functionnalities definitions might occur. Keep an open mind\ntowards the opposite party (is he or she right or wrong?), and grade\nas honestly as possible. 42's pedagogy only makes sense if peer-\nevaluations are carried out seriously.\n",
         "disclaimer_md":"",
         "guidelines_md":"\nYou must grade only what exists in the GiT repository of the student\nor team.\n\nBe careful to check the GiT repository's ownership:: is it the\nstudent's or team's repository, and for the right project?\n\nCheck thoroughly that no wicked aliases have been used to trick you\ninto grading something other than the genuine repository.\n\nAny script supposed to ease the evaluation provided by one party\nmust be thoroughly checked by the other party in order to avoid\nunpleasant situations.\n\nIf the student in charge of the grading hasn't done the project yet,\nit is mandatory that he or she reads it before starting the\nevaluation.\n\nUse the available flags on this scale to tag an empty work, a non\nfunctional work, a coding style (\"norm\") error if applicable,\ncheating, and so on. If a flag is set, the grade is 0 (or -42 in\ncase of cheating). However, cheating case excluded, you are\nencouraged to carry on discussing what went wrong, why, and how to\naddress it, even if the grading itself is over.\n",
         "created_at":"2020-09-16T13:20:35.964Z",
         "correction_number":5,
         "duration":1800,
         "manual_subscription":true,
         "languages":[
            {
               "id":2,
               "name":"English",
               "identifier":"en",
               "created_at":"2015-04-14T16:07:38.122Z",
               "updated_at":"2020-11-20T12:01:38.650Z"
            }
         ],
         "flags":[
            {
               "id":1,
               "name":"Ok",
               "positive":true,
               "icon":"check-4",
               "created_at":"2015-09-14T23:06:52.000Z",
               "updated_at":"2015-09-14T23:06:52.000Z"
            },
            {
               "id":2,
               "name":"Empty work",
               "positive":false,
               "icon":"file-1",
               "created_at":"2015-09-14T23:06:52.000Z",
               "updated_at":"2015-09-14T23:06:52.000Z"
            },
            {
               "id":3,
               "name":"Incomplete work",
               "positive":false,
               "icon":"file-attention",
               "created_at":"2015-09-14T23:06:52.000Z",
               "updated_at":"2015-09-14T23:06:52.000Z"
            },
            {
               "id":4,
               "name":"No author file",
               "positive":false,
               "icon":"bubble-attention-4",
               "created_at":"2015-09-14T23:06:52.000Z",
               "updated_at":"2015-09-14T23:06:52.000Z"
            },
            {
               "id":5,
               "name":"Invalid compilation",
               "positive":false,
               "icon":"skull-2",
               "created_at":"2015-09-14T23:06:52.000Z",
               "updated_at":"2015-09-14T23:06:52.000Z"
            },
            {
               "id":6,
               "name":"Norme",
               "positive":false,
               "icon":"receipt-1",
               "created_at":"2015-09-14T23:06:52.000Z",
               "updated_at":"2015-09-14T23:06:52.000Z"
            },
            {
               "id":7,
               "name":"Cheat",
               "positive":false,
               "icon":"layers",
               "created_at":"2015-09-14T23:06:52.000Z",
               "updated_at":"2015-09-14T23:06:52.000Z"
            },
            {
               "id":8,
               "name":"Crash",
               "positive":false,
               "icon":"bomb",
               "created_at":"2015-09-14T23:06:52.000Z",
               "updated_at":"2015-09-14T23:06:52.000Z"
            },
            {
               "id":9,
               "name":"Outstanding project",
               "positive":true,
               "icon":"star-1",
               "created_at":"2017-05-18T14:07:37.380Z",
               "updated_at":"2017-05-18T14:12:07.415Z"
            },
            {
               "id":13,
               "name":"Forbidden Function",
               "positive":false,
               "icon":"delete-2",
               "created_at":"2018-05-15T12:44:59.600Z",
               "updated_at":"2018-05-15T12:44:59.600Z"
            }
         ],
         "free":false
      },
      "team":{
         "id":0,
         "name":"nope's group",
         "url":"https://api.intra.42.fr/v2/teams/nope",
         "final_mark":103,
         "project_id":0,
         "created_at":"2020-09-17T16:24:39.653Z",
         "updated_at":"2020-10-30T16:43:35.536Z",
         "status":"finished",
         "terminating_at":null,
         "users":[
            {
               "id":0,
               "login":"nope",
               "url":"https://api.intra.42.fr/v2/users/nope",
               "leader":true,
               "occurrence":0,
               "validated":true,
               "projects_user_id":0
            }
         ],
         "locked?":true,
         "validated?":true,
         "closed?":true,
         "repo_url":"nope",
         "repo_uuid":"nope",
         "locked_at":"2020-09-17T16:24:39.700Z",
         "closed_at":"2020-10-29T12:30:34.454Z",
         "project_session_id":0,
         "project_gitlab_path":"nope"
      },
      "feedbacks":[
         {
            "id":0,
            "user":{
               "login":"nope",
               "id":0,
               "url":"https://profile.intra.42.fr/users/nope"
            },
            "feedbackable_type":"ScaleTeam",
            "feedbackable_id":0,
            "comment":"Correcteur impliqué et intéressé. Merci pour la correction :)",
            "rating":5,
            "created_at":"2020-10-30T15:48:16.787Z"
         }
      ]
   }
```
