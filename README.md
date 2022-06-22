shlyuz/шлюз = gateway

# шлюз features
Shlyuz teamserver is the main component of the c2 that the operator interacts with. It provides interaction with the listening posts, and thus the implants, as well as issuing of commands to the artifact factory.

# Listening Post Interaction
Shlyuz teamserver is both a consumer and producer with the listening post(s). Once started, listening posts will constantly be attempting to contact Shlyuz though whatever their configured transport mechanizm is. Once connected, a listening post provides Shlyuz teamserver with a manifest outlining the following details:

- Listening post verison
- Transport Version
- Configuration
- Connected implants
    - Implant configuration
    - Implant identifier
    - Implant transport mechanism
    - Implant transport version
    
Using received manifests, Shlyuz teamserver will know how to interact with the listening post, and thus interact with the implants connected to the listening post, providing the operator control over the implants.
 
This architecture allows for modularization and attribution reduction.

# Setup
Ensure that the directory `setup_configs` does not exist prior to continuing:

```sh
rm -rf setup_configs/
```

It is recommended you create a `venv` for each component:

```python
python -m venv venv
source venv/bin/activate
```

The teamserver requires 2 ports to operate correctly, a `management` port, which provides the flask server to interact with the various components (default: `0.0.0.0:8080`), and a `listener` port (default: `0.0.0.0:8081`), which provides a socket for listening posts to interact with.

The default setup assumes you will be running the listening post (`0.0.0.0:8084`) on the same server as the teamserver. This is not a requirement, but you will need to do some tweaking if that's not what you want.

These settings can be modified by editing [setup.py](setup.py). 

## Generating Configurations
Using [setup.py](setup.py) will bootstrap configurations for each component of the Shlyuz PoC; one teamserver, one listening post, and one implant.

You can generate these configs by executing:

```sh
python3 setup.py
```

This will create the following directory structure:

```
 setup_configs
├──  implant
│   └──  {$implant_id}
│       ├──  shlyuz.conf
│       └──  shlyuz.conf.unencrypted
├──  listening_post
│   └──  {$listening_post_id}
│       └──  shlyuz.conf
└──  teamserver
    └──  shlyuz.conf
```

You should use the appropriate `shlyuz.conf` configuration for each component and place the configuration in its relevant location. An unencrypted (`shlyuz.conf.unencrypted`) and encrypted configuration is provided for the implant. The encrypted configuration is what the implant code is anticipating. Should you wish to modify the the implant configuration, you will have to ensure that you constuct an encrypted version in the same manner.

For the most part, this configuration should work with the provided [tests](https://github.com/shlyuz/tests) repo, allowing interaction with the temserver, but will require some modification to work correctly. This is left as an exercise to the reader.

# Notes
This PoC has intentional cryptographic weaknesses. Most obviously, key rotation is not implemented. It is possible to implement key rotation. If you are pursuing a key rotation implementation, it is recommened that both asymmetric and symmetric keys are rotated during each transaction. 


