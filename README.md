# Boxed
Two-Player Python implementation of the Dots and Boxes game.

## Proof of concept - not final ##


Regarding TOTAL_PLAYERS:
Maximum amount of players is theoretically limitless,
though sync issues have been observed around five or more players.
logic best be moved to the server, but as a POC this is more than enough.
Note: the maximum number of players is directly tied to the number of
colours available in the Player class list. Also, server and client
need to be update manually a function has not been implemented for that yet.
Nor is there any off-board GUI support for len(players) > 2,
mainly labels placement.

Regarding Connectivity:
Socket capabilities have been added in retrospect.
Auto re-join is not supported in case of a dissconect, and timeout
is virtually none. Server and client changes need to take place
for that to happen.

Server robustness:
The server as it stands is not sufficient in handeling temporary
issues with connectivity. Doesn't resume sessions.
Client handel management can be improved.

Client design:
The client side leaves dormant threads under specific circumstances,
issue needs addressing.
Refactoring of the client has been deemed viable and necessary
but not in the near future.
