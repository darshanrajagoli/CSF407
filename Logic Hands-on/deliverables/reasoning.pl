% reasoning.pl
% CS F407 -- Laboratory: Logical Reasoning for Planning
% Optional Extension, Task 8: connecting Prolog to logical reasoning.

% ---------------------------------------------------------------------------
% Task 8 -- the chain given in the handout
% ---------------------------------------------------------------------------

wet_road.

slippery :-
    wet_road.

reduce_speed :-
    slippery.

% Query:  ?- reduce_speed.
%
% Reading the clauses as implications:
%
%       WetRoad                                    (a fact)
%       WetRoad  -> Slippery                       (a rule)
%       Slippery -> ReduceSpeed                    (a rule)
%
% so, by two applications of modus ponens,
%
%       WetRoad => Slippery => ReduceSpeed.
%
% Prolog derives the same conclusion, but backwards: it starts from the goal
% reduce_speed, replaces it with slippery, replaces that with wet_road, and
% finds wet_road as a fact.  Forward reasoning proves the conclusion from the
% facts; SLD resolution reduces the goal to the facts.  Same theorem, opposite
% direction of travel.

% ---------------------------------------------------------------------------
% The example from section 7.1, for completeness
% ---------------------------------------------------------------------------

penguin(polly).

bird(X) :-
    penguin(X).

animal(X) :-
    bird(X).

% ?- animal(polly).      true.
%
%       Penguin(Polly) => Bird(Polly) => Animal(Polly).

% ---------------------------------------------------------------------------
% Where the analogy with classical logic stops
% ---------------------------------------------------------------------------
%
% ?- animal(rex).  fails -- not because Prolog has proved that rex is not an
% animal, but because it could not prove that he is.  Classical logic would
% say "unknown"; Prolog says "false".  That is negation as failure under the
% closed-world assumption, and it is the reason the Prolog verifier can reject
% Move(a,c): "not derivable" is treated as "not permitted".
