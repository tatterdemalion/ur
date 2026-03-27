import { P1_PATH, P2_PATH } from '../lib/board.js'
import { applyColors } from '../lib/colors.js'
import { SWATCHES } from '../lib/colors.js'

export const initialState = {
  // connection
  wsStatus: 'connecting',   // 'connecting' | 'connected' | 'disconnected' | 'error'

  // phase state machine
  phase: 'lobby',           // 'lobby' | 'waiting' | 'game' | 'gameover'

  // lobby
  games: [],
  lobbyStatus: '',
  lobbyDisabled: false,
  playerName: 'Player',
  colorIdx: 0,

  // game identity (set on 'matched')
  myIdx: -1,
  myName: '',
  oppName: '',
  myColor: SWATCHES[0],
  oppColor: SWATCHES[1],
  gameName: '',
  myPath: P2_PATH,
  oppPath: P1_PATH,
  myKey: 'p2_pieces',
  oppKey: 'p1_pieces',
  myScoreKey: 'p2_score',
  myWaitKey: 'p2_waiting',
  oppScoreKey: 'p1_score',
  oppWaitKey: 'p1_waiting',
  flipped: false,

  // game display
  board: null,
  dice: null,             // null | number
  validMoves: [],         // array of piece ids
  statusText: '',
  actionText: '',
  winnerIdx: null,
}

function handleMessage(state, msg) {
  switch (msg.type) {

    case 'lobby':
      return {
        ...state,
        wsStatus: 'connected',
        lobbyStatus: 'Connected. Choose a name and color.',
      }

    case 'games':
      return { ...state, games: msg.games }

    case 'waiting':
      return {
        ...state,
        phase: 'waiting',
        lobbyStatus: `Waiting for an opponent to join "${msg.game_name}"…`,
      }

    case 'error':
      return {
        ...state,
        lobbyStatus: msg.msg || 'Error',
        lobbyDisabled: false,
      }

    case 'matched': {
      const isP0 = msg.player_idx === 0
      // p2 class always = you (--c-*), p1 class always = opponent (--r-*)
      // regardless of which server index you are
      const myPath    = isP0 ? P1_PATH : P2_PATH
      const oppPath   = isP0 ? P2_PATH : P1_PATH
      const myKey     = isP0 ? 'p1_pieces' : 'p2_pieces'
      const oppKey    = isP0 ? 'p2_pieces' : 'p1_pieces'
      const myScoreKey  = isP0 ? 'p1_score'   : 'p2_score'
      const myWaitKey   = isP0 ? 'p1_waiting' : 'p2_waiting'
      const oppScoreKey = isP0 ? 'p2_score'   : 'p1_score'
      const oppWaitKey  = isP0 ? 'p2_waiting' : 'p1_waiting'

      applyColors(msg.you.color, msg.opponent.color)

      return {
        ...state,
        phase: 'game',
        myIdx: msg.player_idx,
        myName: msg.you.name,
        oppName: msg.opponent.name,
        myColor: msg.you.color,
        oppColor: msg.opponent.color,
        gameName: msg.game_name,
        myPath,
        oppPath,
        myKey,
        oppKey,
        myScoreKey,
        myWaitKey,
        oppScoreKey,
        oppWaitKey,
        flipped: isP0,
        statusText: `Game on!  ·  you are ${msg.you.name}`,
        actionText: '',
        dice: null,
        validMoves: [],
      }
    }

    case 'rolling':
      return {
        ...state,
        board: msg.board,
        dice: msg.roll,
        validMoves: [],
        statusText: `${state.oppName} rolled ${msg.roll}  ·  thinking…`,
        actionText: formatAction(msg.last_action, state.myIdx, state.myName, state.oppName),
      }

    case 'state':
      return {
        ...state,
        board: msg.board,
        dice: null,
        validMoves: [],
        statusText: `Waiting for ${state.oppName}…`,
        actionText: formatAction(msg.last_action, state.myIdx, state.myName, state.oppName),
      }

    case 'no_moves':
      return {
        ...state,
        board: msg.board,
        dice: null,
        validMoves: [],
        actionText: formatAction(msg.last_action, state.myIdx, state.myName, state.oppName),
      }

    case 'your_turn':
      return {
        ...state,
        board: msg.board,
        dice: msg.roll,
        validMoves: msg.valid_moves,
        statusText: `Your turn  ·  rolled ${msg.roll}  ·  pick a piece`,
        actionText: formatAction(msg.last_action, state.myIdx, state.myName, state.oppName),
      }

    case 'game_over':
      return {
        ...state,
        phase: 'gameover',
        board: msg.board,
        validMoves: [],
        winnerIdx: msg.winner_idx,
        actionText: formatAction(msg.last_action, state.myIdx, state.myName, state.oppName),
      }

    default:
      return state
  }
}

function formatAction(a, myIdx, myName, oppName) {
  if (!a) return ''
  const who = a.player_idx === myIdx ? myName : oppName
  if      (a.action_type === 'scored')  return `${who} scored ✦`
  else if (a.action_type === 'skipped') return `${who} had no valid moves`
  else if (a.hit)                       return `${who} captured a piece`
  else if (a.rosetta)                   return `${who} landed on ✿  — extra turn`
  else                                  return `${who} moved  ·  rolled ${a.roll}`
}

export function reducer(state, action) {
  switch (action.type) {
    case 'WS_MESSAGE':
      return handleMessage(state, action.payload)
    case 'WS_DISCONNECTED':
      return {
        ...state,
        wsStatus: 'disconnected',
        lobbyStatus: 'Connection lost. Refresh to reconnect.',
        lobbyDisabled: true,
      }
    case 'WS_ERROR':
      return { ...state, wsStatus: 'error' }
    case 'SET_NAME':
      return { ...state, playerName: action.value }
    case 'SET_COLOR_IDX':
      return { ...state, colorIdx: action.value }
    case 'LOBBY_DISABLE':
      return { ...state, lobbyDisabled: action.value }
    case 'MOVE_SENT':
      return { ...state, validMoves: [], statusText: 'Moving…' }
    default:
      return state
  }
}
