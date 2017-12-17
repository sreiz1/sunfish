#!/usr/bin/pypy -u
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division
import importlib
import re
import sys
import time

import tools
import sunfish

from tools import WHITE, BLACK
from xboard import Unbuffered, sunfish, input
sys.stdout = Unbuffered(sys.stdout)

logf=None

def eprint(*args, **kwargs):
    global logf
    if logf==None:
	logf=open("logf.txt", "w")
    print(*args, file=logf, **kwargs)
    logf.flush()

def main():
    pos = tools.parseFEN(tools.FEN_INITIAL)
    searcher = sunfish.Searcher()
    forced = False
    color = WHITE
    our_time, opp_time = 1000, 1000 # time in centi-seconds
    show_thinking = True

    # print name of chess engine
    print('Sunfish')

    while True:
        smove = input()

        if smove == 'quit' or smove=='stop':
            break

        elif smove == 'uci':
	    print('id name Sunfish')
            print('uciok')

        elif smove == 'isready':
            print('readyok')

        elif smove == 'ucinewgame':
            pos=tools.parseFEN(tools.FEN_INITIAL)
	    searcher = sunfish.Searcher()
            forced = False
            color = WHITE
            our_time, opp_time = 1000, 1000 # time in centi-seconds
            show_thinking = True

        elif smove.startswith('position'):
            params = smove.split(' ', 2)
            if params[1] == 'fen':
                fen = params[2]
                pos = tools.parseFEN(fen)
                color = WHITE if fen.split()[1] == 'w' else BLACK
	    else:
		params = smove.split(' ')
		if len(params) == 1: continue
		i = 1
                while i < len(params):
                    param = params[i]
                    if param == 'startpos':
		    	pos=tools.parseFEN(tools.FEN_INITIAL)
			color = WHITE
                    elif param == 'moves':
                        i += 1
			# rest are moves
			while i < len(params):
			    m0=params[i]
			    m = tools.mparse(color, m0)
		            pos = pos.move(m)
		            color = 1-color
			    i+=1
                    i += 1

        elif smove.startswith('go'):
            #  default options
            depth = 1000
            movetime = -1
            moves_remain = 40
	    tc=0

            # parse parameters
            params = smove.split(' ')
            if len(params) == 1: continue

            i = 0
            while i < len(params):
                param = params[i]
                if param == 'depth':
                    i += 1
                    depth = int(params[i])
                elif param == 'movetime':
                    i += 1
                    movetime = int(params[i])
		elif param == 'wtime':
                    i += 1
                    if color==WHITE:
			movetime = int(params[i])
		    tc=1
		elif param == 'btime':
                    i += 1
                    if color==BLACK:
                        movetime = int(params[i])
		    tc=1
		elif param == 'movestogo':
                    i += 1
		    moves_remain = int(params[i])
                i += 1

	    if tc==1 and moves_remain>0:
		movetime = movetime / moves_remain
            forced = False

            start = time.time()
            ponder = None
            for _ in searcher._search(pos):
                moves = tools.pv(searcher, pos, include_scores=False)

                if show_thinking:
                    entry = searcher.tp_score.get((pos, searcher.depth, True))
                    score = int(round((entry.lower + entry.upper)/2))
                    usedtime = int((time.time() - start) * 1000)
                    moves_str = moves if len(moves) < 15 else ''
                    print('info depth {} score {} time {} nodes {} {}'.format(searcher.depth, score, usedtime, searcher.nodes, moves_str))

                if len(moves) > 5:
                    ponder = moves[1]

                if movetime > 0 and (time.time() - start) * 1000 > movetime:
                    break

                if searcher.depth >= depth:
                    break

            entry = searcher.tp_score.get((pos, searcher.depth, True))
            m, s = searcher.tp_move.get(pos), entry.lower
            moves = moves.split(' ')
            if len(moves) > 1:
                print('bestmove ' + moves[0] + ' ponder ' + moves[1])
            else:
                print('bestmove ' + moves[0])

        elif smove.startswith('time'):
            our_time = int(smove.split()[1])

        elif smove.startswith('otim'):
            opp_time = int(smove.split()[1])

        else:
            pass

if __name__ == '__main__':
    main()
