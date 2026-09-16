% planner.pl
% CS F407 -- Laboratory: Logical Reasoning for Planning
% Optional Extension, Tasks 6 and 7: Prolog as a logical verifier.
%
% This file is the INDEPENDENT knowledge base.  It knows the layout of the
% warehouse.  It does not know anything about the Python planner, and the
% Python planner does not consult it.  That independence is the whole point:
%
%       Python generates a candidate plan  ->  Prolog checks it.
%
% Loads unchanged in SWI-Prolog:   swipl planner.pl
% (In this laboratory it was executed by prolog_engine.py -- see LAB_REPORT.md.)

% ---------------------------------------------------------------------------
% Task 6 -- the warehouse as facts
% ---------------------------------------------------------------------------
%
% The warehouse is a corridor:   a --- b --- c
% There is no direct link between a and c.

connected(a,b).
connected(b,a).
connected(b,c).
connected(c,b).

% A rule.  The clause  head :- body  is the definite clause  body -> head,
% i.e.  forall X,Y. Connected(X,Y) -> CanMove(X,Y).

can_move(X,Y) :-
    connected(X,Y).

% ---------------------------------------------------------------------------
% Task 7 -- checking a single proposed action
% ---------------------------------------------------------------------------

valid_move(X,Y) :-
    connected(X,Y).

% ---------------------------------------------------------------------------
% Extension -- checking a whole proposed plan
% ---------------------------------------------------------------------------
%
% A route is valid from location X if every move starts where the previous one
% ended and every individual move is supported by the connectivity facts.
% This catches two different kinds of bad plan: illegal moves, and moves that
% are individually legal but do not join up.

valid_route(_, []).
valid_route(X, [move(X,Y)|Rest]) :-
    connected(X,Y),
    valid_route(Y, Rest).

% ---------------------------------------------------------------------------
% Extension -- reachability, to show what the non-recursive rule cannot do
% ---------------------------------------------------------------------------
%
% can_move/2 is one step and is deliberately NOT transitive: can_move(a,c)
% fails.  Reachability is the transitive closure, and needs recursion.
% (visited-list bookkeeping keeps the search from cycling a -> b -> a -> ...)

reachable(X,Y) :-
    route(X, Y, [X], _).

route(X, X, Visited, Visited).
route(X, Y, Visited, Out) :-
    connected(X, Z),
    \+ member(Z, Visited),
    route(Z, Y, [Z|Visited], Out).

member(H, [H|_]).
member(H, [_|T]) :-
    member(H, T).
