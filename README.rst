Overview
========
This Napp allows a user to create a point to point L2 circuit.

It provides a REST API to create/modify/delete circuits. For now, the list of installed circuits is kept in memory,
but it should be later kept in a permanent storage.
Circuits can be installed at the time of request or at a predefined time, and can also have a time to be deleted.
The Napp also listens for PortStatus events, modifying circuits that use a port that went down.

Requirements
============
- sortedcontainers
- Napps:

  - kytos/flow_manager
  - kytos/pathfinder
