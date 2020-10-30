shlyuz/шлюз = gateway

# шлюз features
Shlyuz is the main component of the c2 that the operator interacts with. It provides the console for the operator to connect to, as well as interaction with the listening posts, and thus the implants, as well as issuing of commants to the artifact factory.

# Listening Post Interaction
Shlyuz is both a consumer and producer with the listening post(s). Once started, listening posts will constantly be attempting to contact Shlyuz though whatever their configured transport mechanizm is. Once connected, a listening post provides Shlyuz with a manifest outlining the following details:

- Listening post verison
- Transport Version
- Configuration
- Connected implants
    - Implant configuration
    - Implant identifier
    - Implant transport mechanism
    - Implant transport version
    
Using received manifests, Shlyuz will know how to interact with the listening post, and thus interact with the implants connected to the listening post, providing the operator control over the implants.
 
This architecture allows for modularization and attribution reduction 