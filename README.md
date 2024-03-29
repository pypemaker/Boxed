# Boxed
Two-Player Python implementation of the Dots and Boxes game.

 - Dots and Boxes Wikipedia Page: https://en.wikipedia.org/wiki/Dots_and_Boxes

## Proof of concept - not final ##


Regarding TOTAL_PLAYERS:
Maximum amount of players is theoretically limitless,
though sync issues have been observed around five or more players.
Logic best be moved to the server, but as a POC this is more than enough.
Note: the maximum number of players is directly tied to the number of
colours available in the Player class 'P_COLOURS' list.
Also, server and client need to be update manually, a function has not
been implemented for that yet. Nor is there any off-board GUI support
for len(players) greater than two, mainly labels placement.

Regarding Connectivity:
Socket capabilities have been added in retrospect.
Auto re-join is not supported in case of a disconnect, and timeout
is virtually none. Server and client changes need to take place
for that to happen.

Server robustness:
The server as it stands is not sufficient in handling temporary
issues with connectivity. Doesn't resume sessions.
Client handle management can be improved.

Client design:
The client side leaves dormant threads under very specific circumstances,
issue needs addressing.
Refactoring of the client has been deemed viable and necessary
but not in the near future.
