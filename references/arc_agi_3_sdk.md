# ARC-AGI-3 官方 SDK 实核笔记（arc-agi Toolkit）

- 实核人：SDK 文档实核子代理
- 实核日期：2026-10-10（所有页面均于本日抓取）
- 文档站入口：https://docs.arcprize.org/（首页即 ARC-AGI-3 Quickstart）
- 完整页面索引：https://docs.arcprize.org/llms.txt
- 实核方式：WebFetch 逐页抓取官方文档 + PyPI JSON API + 官方 GitHub README 交叉验证

> 本笔记所有"原文摘录"保留英文原文；中文说明为实核者注解。凡文档未载明处均明确标注，无编造。

---

## a. SDK 包名与安装方式 —— 【已核实】

**来源：**
- https://docs.arcprize.org/toolkit/overview.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/index.md（抓取日期 2026-10-10）
- https://pypi.org/pypi/arc-agi/json（抓取日期 2026-10-10）
- https://pypi.org/pypi/arcengine/json（抓取日期 2026-10-10）

**原文摘录（toolkit/overview.md）：**

> Package name: `arc-agi` (open-source Python SDK for ARC-AGI-3 environments)
>
> ```bash
> uv add arc-agi
> # or
> pip install arc-agi
> ```

**原文摘录（docs 首页 Quickstart，index.md）：**

> ```python
> import arc_agi
> from arcengine import GameAction
>
> arc = arc_agi.Arcade()
> env = arc.make("ls20", render_mode="terminal")
> ```

**PyPI 实核（pypi.org/pypi/arc-agi/json）：**
- 最新版本：**0.9.9**，发布日期 **2026-06-10**
- 描述："ARC-AGI Toolkit" — "an open-source Python interface (API) for ARC-AGI-3 interactive environments, enabling agents to interact with them locally or via API"
- Requires-Python：**>=3.12**
- 依赖：`arcengine>=0.9.3`, `flask>=3.1.0`, `matplotlib>=3.7.0`, `pydantic>=2.0.0`, `python-dotenv>=1.0.0`, `pillow>=12.1.1`, `requests>=2.31.0`
- 项目页：https://pypi.org/project/arc-agi/

**PyPI 实核（arcengine）：**
- 最新版本 **0.9.3**（2026-01-29），"A Python library using numpy"（ARC Prize Foundation 出品的 2D sprite 游戏引擎），Requires-Python >=3.12，依赖 numpy>=1.24.0、pydantic>=2.10.6，MIT 许可

**中文说明：** SDK 主包为 `arc-agi`（import 名 `arc_agi`），底层引擎/类型包为 `arcengine`（提供 `GameAction`、`GameState` 等枚举与帧数据结构）。注意 Python 版本硬性要求 **3.12+**。文档站 changelog 载初版 v0.9.1 于 2026-01-29 发布；GitHub README（https://github.com/arcprize/arc-agi）确认当前版本 0.9.9。

---

## b. 建立环境/连接对局的 API 形态 —— 【已核实】

**来源：**
- https://docs.arcprize.org/toolkit/arc_agi.md（Arcade 客户端参考，抓取日期 2026-10-10）
- https://docs.arcprize.org/toolkit/overview.md（抓取日期 2026-10-10）
- https://github.com/arcprize/arc-agi（README，抓取日期 2026-10-10）

**原文摘录（Arcade 构造器，toolkit/arc_agi.md）：**

> ```python
> Arcade(operation_mode=..., arc_api_key=..., environments_dir=..., recordings_dir=..., arc_base_url=..., logger=...)
> ```
>
> - `operation_mode` (enum): `NORMAL` (default), `OFFLINE`, `ONLINE`, `COMPETITION` — env var `OPERATION_MODE`
> - `arc_api_key` (str): auto-fetches anonymous key if unset and not offline — env var `ARC_API_KEY`
> - `environments_dir` (str, default `"environment_files"`) — env var `ENVIRONMENTS_DIR`
> - `recordings_dir` (str, default `"recordings"`) — env var `RECORDINGS_DIR`
> - `arc_base_url` (str, default `"https://three.arcprize.org"`) — env var `ARC_BASE_URL`
> - `logger`: optional logger instance
>
> ```python
> arc = Arcade(
>     operation_mode=OperationMode.OFFLINE,
>     arc_api_key="your-api-key",
>     environments_dir="./my_games",
>     recordings_dir="./my_recordings",
>     arc_base_url="https://three.arcprize.org",
>     logger=logging.getLogger("my_agent")
> )
> ```

**原文摘录（make 方法，toolkit/arc_agi.md）：**

> ### `make(game_id, seed=0, scorecard_id=None, save_recording=False, include_frame_data=True, render_mode=None, renderer=None)` → `EnvironmentWrapper | None`
> - `game_id` (str): e.g. `'ls20'` or `'ls20-1234abcd'` (version after `'-'`)
> - `render_mode` (str): `"human"`, `"terminal"`, `"terminal-fast"`
> - `renderer` (`Callable[[int, FrameDataRaw], None]`): overrides render_mode
>
> ```python
> env = arc.make("ls20", render_mode="terminal")
> env = arc.make("ls20-1234abcd", seed=42, save_recording=True)
> ```

**原文摘录（EnvironmentWrapper，toolkit/environment_wrapper.md）：**

> - **`reset()`** → `FrameDataRaw | None`: returns the initial game state, or None on failure.
> - **`step(action, data=None, reasoning=None)`** → `FrameDataRaw | None`
> - **`observation_space`** — Returns `FrameDataRaw | None`; the last response data (None if no response yet).
> - **`action_space`** — Returns `list[GameAction]`; available actions (empty list if unset).
> - **`info`** — Returns an `EnvironmentInfo` object with fields `game_id`, `title`, and `tags`.

**中文说明：**
- 连接对局两步走：`arc = Arcade(...)` 建客户端 → `env = arc.make(game_id, seed=..., ...)` 建环境句柄（即本项目 `connect_env` 的 SDK 底座）。
- **没有独立的 episode ID 参数**：一局（session）由 `make()` + 首次 `step(GameAction.RESET)`（REST 层 `POST /api/cmd/RESET`）创建；在线模式下服务端返回 `guid`（会话 UUID）标识该局。seed 通过 `make(seed=42)` 传入（默认 0）。
- API key 三种传法：构造器参数 `arc_api_key=`、环境变量 `ARC_API_KEY`、或 `.env` 文件（python-dotenv 支持）；不设置时在线模式自动取匿名 key（匿名可玩的游戏少）。
- `make()` 失败返回 `None`（文档明确 "Returns an EnvironmentWrapper instance if successful, None otherwise"），**不抛异常**，调用方必须判空。
- 其余 Arcade 方法：`get_environments()`、`create_scorecard(source_url=None, tags=None, opaque=None)`（别名 `open_scorecard`）、`get_scorecard(scorecard_id=None)`、`close_scorecard(scorecard_id=None)`、`listen_and_serve()`。
- REST 层对应关系（full-play-test.md 实核）：`GET /api/games` 取游戏列表 → `POST /api/scorecard/open`（body 含 tags）→ `POST /api/cmd/RESET`（body：`game_id`、`card_id`，可选 `guid`）开局 → `POST /api/cmd/ACTION{n}` 逐步 → `POST /api/scorecard/close` 收分。

---

## c. 观测(observation)对象的精确结构 —— 【已核实（REST 层完整；SDK 层字段为 REST 字段子集）】

**来源：**
- https://docs.arcprize.org/api-reference/commands/start-or-reset-game-instance.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/api-reference/commands/execute-complex-action-requires-xy.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/game-schema.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/toolkit/environment_wrapper.md（抓取日期 2026-10-10）
- https://github.com/arcprize/ARC-AGI-3-Agents（README，抓取日期 2026-10-10）

**原文摘录（REST FrameResponse 字段表，start-or-reset-game-instance.md；ACTION6 端点页同构）：**

> | Field | Type | Notes |
> |---|---|---|
> | `game_id` | string | Running session's game ID |
> | `guid` | string | Session ID for subsequent commands |
> | `frame` | array | 64×64 grids; each cell an integer 0–15; multiple frames possible |
> | `state` | enum | `NOT_PLAYED`, `NOT_FINISHED`, `WIN`, `GAME_OVER` |
> | `levels_completed` | integer 0–254 | Cumulative levels done |
> | `win_levels` | integer 0–254 | Level threshold to win |
> | `action_input` | object | Echo: `id` (0–7, 0 = RESET), `data`, optional `reasoning` |
> | `full_reset` | boolean | True if RESET created a new game vs. level reset |
> | `available_actions` | array of ints 0–7 | Valid actions currently |

**原文摘录（响应 JSON 示例，start-or-reset-game-instance.md）：**

> ```json
> {
>   "game_id": "ls20-016295f7601e",
>   "guid": "2fa5332c-2e55-4825-b5c5-df960d504470",
>   "frame": [[[0, 0, 0, "..."], ["..."]]],
>   "state": "NOT_FINISHED",
>   "levels_completed": 0,
>   "win_levels": 254,
>   "action_input": {"id": 0, "data": {}},
>   "available_actions": [1, 2, 3, 4]
> }
> ```

**原文摘录（GameState 枚举，game-schema.md）：**

> | Value | Meaning |
> |---|---|
> | `NOT_PLAYED` | "No game has been started" |
> | `NOT_FINISHED` | "The game is active and awaiting another action" |
> | `WIN` | "The objective was completed successfully" |
> | `GAME_OVER` | "The run ended without a win" |

**原文摘录（网格结构，game-schema.md）：**

> - Dimensions: Max 64x64
> - Cell values: Integers 0–15 ("representing different states/colors")
> - Coordinates: "(0,0) at top-left, (x,y) format"

**原文摘录（SDK 层属性访问，toolkit/environment_wrapper.md）：**

> ```python
> obs = env.observation_space
> if obs:
>     print(f"Game state: {obs.state}")
>     print(f"Levels completed: {obs.levels_completed}")
> ```

**原文摘录（字段改名史，github.com/arcprize/ARC-AGI-3-Agents README）：**

> "score changed to levels_completed" and "win_score changed to win_levels" ... "available_actions to FrameData" plus "ACTION7 as possible GameAction" were added

**中文说明：**
- SDK 层观测对象为 `FrameDataRaw`（`reset()`/`step()` 返回值；`env.observation_space` 为最近一帧），文档明示的字段访问有 `obs.state`（GameState 枚举）与 `obs.levels_completed`（int）；官方 Agents 仓库 README 证实 `FrameData` 含 `levels_completed`、`win_levels`、`available_actions`（由旧名 score/win_score 改来）。
- REST 层 `FrameResponse` 是最完整、字段类型最明确的观测定义（上表 9 个字段），SDK 的 `FrameDataRaw` 与之对应。
- `frame` 是"数组的数组"：外层可含多个 64×64 网格，每格 0–15 整数（4-bit 颜色/状态索引）。`render_obs` 共享件应按"多帧 × 64×64 int 网格"处理，且网格可能小于 64×64（文档称 Max 64x64）。
- 注意 `available_actions` 在观测里返回的是 **int 数组（0–7）**，而 SDK `env.action_space` 返回 `list[GameAction]` 枚举——两层表示不同，做 render_obs 时要兼容。
- 局限：SDK 层 `FrameDataRaw` 的**完整字段清单**（是否原样透传 `guid`/`action_input`/`full_reset`）文档未逐字段列明；Agents 仓库 `agents/structs.py` 源文件抓取 404（仓库已改结构），未能逐行核对类定义。

---

## d. 提交动作的 API —— 【已核实】

**来源：**
- https://docs.arcprize.org/toolkit/submit-action.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/actions.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/api-reference/commands/execute-simple-action-1.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/api-reference/commands/execute-complex-action-requires-xy.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/create-agent.md（抓取日期 2026-10-10）

**原文摘录（SDK step 签名，toolkit/submit-action.md + environment_wrapper.md）：**

> ### `step(action, data=None, reasoning=None)` → `FrameDataRaw | None`
> - `action`: a `GameAction` enum value
> - `data`: optional dict; for complex actions, contains `"x"` and `"y"` coordinates
> - `reasoning`: optional dict included in recordings
>
> ```python
> obs = env.step(GameAction.ACTION1)                          # simple
> obs = env.step(GameAction.ACTION6, data={"x": 32, "y": 32}) # complex (x,y)
> obs = env.step(
>     GameAction.ACTION6,
>     data={"x": 32, "y": 32},
>     reasoning={"thought": "clicking center of screen", "confidence": 0.85,
>                "alternatives_considered": ["top-left", "bottom-right"]}
> )
> ```

**原文摘录（动作全集，actions.md）：**

> | Action | Meaning |
> |---|---|
> | `RESET` | Initializes or restarts the game or level state |
> | `ACTION1` | Simple action, "semantically mapped to up" |
> | `ACTION2` | Simple action, "semantically mapped to down" |
> | `ACTION3` | Simple action, "semantically mapped to left" |
> | `ACTION4` | Simple action, "semantically mapped to right" |
> | `ACTION5` | Multi-purpose interaction action (examples given: "interact, select, rotate, attach/detach, execute, etc.") |
> | `ACTION6` | The only action "requiring x,y coordinates (0-63 range)" |
> | `ACTION7` | A simple undo action |

**原文摘录（REST 请求体，execute-simple-action-1.md / execute-complex-action-requires-xy.md）：**

> SimpleActionCommand: `game_id` (string, required), `guid` (string, required), `reasoning` (optional JSON, ≤16 KB)
>
> ```json
> {
>   "game_id": "ls20-016295f7601e",
>   "guid": "2fa5332c-2e55-4825-b5c5-df960d504470",
>   "reasoning": { "policy": "π_left" }
> }
> ```
>
> ComplexActionCommand (ACTION6): `game_id`, `guid`, `x` (int, 0–63, 0 = left), `y` (int, 0–63, 0 = top), `reasoning` (any JSON, "≤ 16 KB once serialized")
>
> ```json
> { "game_id": "ls20-016295f7601e", "guid": "2fa5332c-2e55-4825-b5c5-df960d504470", "x": 12, "y": 34 }
> ```

**原文摘录（GameAction 用法，create-agent.md 官方示例）：**

> ```python
> if action.is_simple():
>     action.reasoning = f"Chose {action.value} randomly"
> elif action.is_complex():
>     action.set_data({"x": random.randint(0, 63), "y": random.randint(0, 63)})
>     action.reasoning = {"action": action.value, "reason": "Random choice"}
> ```

**中文说明：**
- SDK 层提交动作 = `env.step(GameAction.XXX)`；action 是 `arcengine.GameAction` **枚举值**（非字符串），复杂动作坐标走独立 `data={"x": int, "y": int}` 参数（0–63）。
- REST 层动作编号：`id` 0–7，0=RESET，6=复杂动作；ACTION6 的 x/y 是**请求体顶层字段**（不在 `data` 下），回显时才进 `action_input.data`。
- `reasoning` 是可选 dict（REST 层任意 JSON、序列化后 ≤16 KB），进录像/审计，不计数计分（methodology.md：内部步骤不计 action 数）。
- `GameAction` 枚举自带 `is_simple()` / `is_complex()` / `set_data()` / `from_name()` 辅助方法（Agents 仓库用法）。
- 每局可用动作是动作全集的子集，由观测的 `available_actions` 字段逐帧告知；ACTION6 可用时也不告知哪些坐标是"活跃区"（actions.md 原文："Action 6 does not provide explicit X/Y coordinates for active areas"）。

---

## e. 终局信号 —— 【已核实】

**来源：**
- https://docs.arcprize.org/toolkit/environment_wrapper.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/full-play-test.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/create-agent.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/api-reference/commands/start-or-reset-game-instance.md（抓取日期 2026-10-10）

**原文摘录（状态判断，toolkit/environment_wrapper.md）：**

> ```python
> from arcengine import GameAction, GameState
> if obs and obs.state == GameState.WIN:
>     print("Game won!")
> ```

**原文摘录（循环退出条件，full-play-test.md）：**

> The loop exits when the state is `WIN` or `GAME_OVER`.
>
> | `NOT_PLAYED` | No game started |
> | `NOT_FINISHED` | Active, awaiting next action |
> | `WIN` | Objective completed |
> | `GAME_OVER` | Run ended without a win |

**原文摘录（agent 侧 is_done，create-agent.md）：**

> ```python
> def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
>     return latest_frame.state is GameState.WIN
> ```
>
> if latest_frame.state in [GameState.NOT_PLAYED, GameState.GAME_OVER]:
>     action = GameAction.RESET

**原文摘录（RESET 语义，start-or-reset-game-instance.md）：**

> - No `guid` → new instance.
> - With `guid` + at least one ACTION since the last level transition → only current level restarts.
> - With `guid` + no ACTIONs → full game reset. Two consecutive RESETs guarantee a fresh game.

**中文说明：**
- 终局信号 = 观测里的 `state` 字段：`WIN`（通关）/ `GAME_OVER`（失败终局）即一局结束；`NOT_FINISHED` 继续循环。
- `step()`/`reset()` 返回 `None` 表示请求失败（网络/服务端错误），**不是**终局——run_episode 必须区分"返回 None（出错重试）"与"state=GAME_OVER（终局）"。
- `GAME_OVER` 后唯一合法动作是 `RESET`（重开当前关或整局）；官方模式：GAME_OVER → `env.reset()` 重来。两次连续 RESET 保证整局全新。
- 通关阈值由观测 `win_levels` 给出（0–254），进度看 `levels_completed`。
- 无独立的"超时"状态枚举；文档未载明墙钟超时会如何置 state（见 h）。

---

## f. 错误码/异常 —— 【已核实（REST 错误码）；SDK 层异常类型文档未载明】

**来源：**
- https://docs.arcprize.org/api-reference/commands/start-or-reset-game-instance.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/api-reference/commands/execute-simple-action-1.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/api-reference/commands/execute-complex-action-requires-xy.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/actions.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/rate_limits.md（抓取日期 2026-10-10）
- https://github.com/arcprize/arc-agi（README，抓取日期 2026-10-10）

**原文摘录（错误码，REST 端点页）：**

> - **400** — Bad request: unknown `game_id`; missing/unknown `card_id`; `guid` not matching an active session.（RESET 页）
> - **400** — bad request: unknown/invalid `game_id`, `guid` mismatch, or `reasoning` over 16 KB / malformed（ACTION1 页）
> - **400** — Bad request: unknown `game_id`; `guid` missing or mismatched with `game_id`; or `x`/`y` outside 0–63（ACTION6 页）
> - **401** — "Missing or invalid **X-API-Key** header."（各端点页）
> - 429 body: `{"error":"RATE_LIMIT_EXCEEDED","message":"rate limit has been exceeded"}`（rate_limits.md）

**原文摘录（400/500 的语义辨析，actions.md）：**

> After game over, the only valid action is `RESET`; anything else triggers a `400 Bad Request` error. A `400` means game-over; a `500` indicates a server-side problem.

**原文摘录（SDK 层失败形态，github.com/arcprize/arc-agi README）：**

> `make()` returns `None` on failure ("Returns an EnvironmentWrapper instance if successful, None otherwise").
> `step()` / `reset()` also return `None` when the operation fails; examples check `if obs is None`.
> In 0.9.9: "Remote action failures now include the HTTP response body in the error log to aid debugging".

**中文说明：**
- **REST 层错误码**（在线模式底层）：401（API key 缺失/无效）、400（非法请求：未知 game_id、guid 不匹配、坐标越界 0–63、reasoning 超 16KB、终局后发非 RESET 动作）、429（限流，body 带 `RATE_LIMITExceeded` 错误名，需指数退避重试）、500（服务端故障）。402 等其他码文档未载明。
- **SDK 层**：`make()`/`step()`/`reset()` 失败**返回 None 不抛异常**（错误进日志，0.9.9 起远程动作失败会把 HTTP 响应体写进 error log）。SDK 没有文档化的自定义异常类型/错误码枚举——`submit_action` 的"非法动作错误码"应对 400 系语义（非法动作→重试或 RESET；429→退避；401→配置错误）自行归一化。
- 注意 400 的双重含义：既可能是真·非法参数，也可能是"GAME_OVER 后非 RESET 动作"——收到 400 时应先查当前 state 再决定策略。

---

## g. 局 ID 形态 —— 【已核实】

**来源：**
- https://docs.arcprize.org/available-games.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/game-schema.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/toolkit/arc_agi.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/api-reference/commands/start-or-reset-game-instance.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/toolkit/list-games.md（抓取日期 2026-10-10）

**原文摘录（game ID 形态，toolkit/arc_agi.md）：**

> `game_id` (str): e.g. `'ls20'` or `'ls20-1234abcd'` (version after `'-'`)

**原文摘录（版本规则，game-schema.md）：**

> `<game_name>`-`<version>` — game names are stable; versions may change.

**原文摘录（会话 ID，start-or-reset-game-instance.md）：**

> `guid` | string | Session ID for subsequent commands
> 例：`"2fa5332c-2e55-4825-b5c5-df960d504470"`（标准 UUID 字符串）

**原文摘录（游戏列表，available-games.md）：**

> IDs appear as short alphanumeric strings (2 lowercase letters + 2 digits), e.g. `ls20`, `ft09`, `vc33`.
> "By default, three games are available to anonymous users after launch."
> Browse at arcprize.org/tasks or "Use the ARC-AGI Toolkit to list games programmatically"

**原文摘录（列表 API，toolkit/list-games.md）：**

> ```python
> arc = arc_agi.Arcade()
> games = arc.get_environments()
> for game in games:
>     print(f"{game.game_id}: {game.title}")
> ```
> `EnvironmentInfo`: `game_id`, `title`, `tags`

**中文说明：**
- 两级 ID 要区分：
  1. **game_id**（游戏 ID，非局 ID）：字符串，`<名称>-<版本hash>`，如 `ls20-016295f7601e`；短名 `ls20` 可被 SDK 解析（取最新版本）。名称稳定、版本可能更替。
  2. **guid**（会话/局 ID）：标准 UUID 字符串，REST 层由 RESET 响应返回，后续所有 ACTION 请求必须携带；SDK 层由 wrapper 内部持有，调用方无需手管。
- 本项目的"局 spec"应落到：`game_id`（含或不含版本后缀）+ 可选 `seed` + 可选 `scorecard_id` —— 正好是 `arc.make()` 的参数集。
- 取局列表：SDK `arc.get_environments()` → `list[EnvironmentInfo]`（game_id/title/tags）；REST `GET /api/games`。匿名 key 默认只有 3 个游戏可玩，注册 key 解锁全部公开游戏。

---

## h. 时限 —— 【文档未载明（无每局/每步墙钟时限）；仅有计分时限与限流】

**来源（均已查证"无"）：**
- https://docs.arcprize.org/methodology.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/rate_limits.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/full-play-test.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/index.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/arc-agi-3.md（抓取日期 2026-10-10）
- https://docs.arcprize.org/changelog.md（抓取日期 2026-10-10）

**原文摘录（计分不看时间，methodology.md）：**

> `level_score = (human_baseline_actions / ai_actions) ^ 2`
> Actions counted: discrete interactions affecting game state; internal steps like "tool calls, reasoning steps, retries" don't count.
> （该页无任何 per-game/per-step/per-episode 时间限制表述，计分纯按动作数）

**原文摘录（限流，rate_limits.md）：**

> Rate limit: 600 requests per minute (RPM) ... Returns a 429 ... Retries use "an exponential backoff mechanism".
> The API is best-effort with "no SLA" or guaranteed response times.

**原文摘录（scorecard 时限，changelog.md 2026-04-14 条目）：**

> "Maximum scorecard open duration is now capped at 24 hours"

**原文摘录（本地速度，local-vs-online.md）：**

> Runs at roughly 2,000 FPS ("~2,000 FPS (120,000 frames per minute)")

**中文说明：**
- **官方文档未载明任何每局/每步的墙钟时间限制或超时后的状态表现**——methodology、quickstart、full-play-test、arc-agi-3 各页均无 per-game/per-step/per-episode 时限表述；GameState 也没有 TIMEOUT 成员。
- 实际存在的"时间类"约束只有三个：
  1. **限流**：在线 600 RPM（超限 429，需指数退避）；
  2. **scorecard 开启时长上限 24 小时**（changelog 2026-04-14）；
  3. **效率按动作数计**（不是时间）：比人多花动作会被平方惩罚。
- 本项目 run_episode 若需要超时保护，属自实现策略（如本地 wall-clock 预算），不能指望 SDK 返回"超时"信号。

---

## 附：本项目三函数映射速查

| 项目函数 | SDK 底座 | 要点 |
|---|---|---|
| `connect_env(spec)` | `Arcade(**cfg)` → `arc.make(game_id, seed, scorecard_id, render_mode, ...)` → 判空 → `env.step(GameAction.RESET)` 或 `env.reset()` 取初始观测 | make 失败返回 None 不抛异常；API key 走 ARC_API_KEY 环境变量或构造器参数 |
| `submit_action(action, ...)` | `env.step(GameAction.XXX, data={"x":..,"y":..}, reasoning={...})` | 返回 FrameDataRaw 或 None（None=请求失败≠终局）；终局看 obs.state；非法动作对应 REST 400 语义；429 退避 |
| `run_episode` | 循环：obs(render) → LLM → action → step；退出条件 `state in {WIN, GAME_OVER}` | GAME_OVER 后合法动作仅 RESET；`available_actions` 逐帧变化需过滤；官方 agent 接口参考 `is_done(frames, latest_frame)` / `choose_action(frames, latest_frame)` |

**观测→LLM 参考（llm_agents.md）：** 官方 LLM agent 用 function calling 让模型返回动作名（`RESET` / `ACTION1`–`ACTION6` 为合法名），并建议正则后处理 + 非法输出回退随机安全动作（官方示例 `safe_parse` 用 `re.search(r"(RESET|ACTION[1-6])", model_response)` + `GameAction.from_name(...)`），避免 `ValueError` 直接终局。

## 附：装包源码补核（2026-10-10，arc-agi==0.9.9 + arcengine==0.9.3 装入 fn_work/venv 后直读 site-packages 源码）

> 以下为文档实核局限的补核结论（对应下方"实核局限记录"第 1、2 条），源码即最终真值。

**arcengine/enums.py 逐行核实：**

- `class GameState(str, Enum)`：`NOT_PLAYED / NOT_FINISHED / WIN / GAME_OVER`（取字符串值用 `.value` 或 `.name`）。
- `class GameAction(Enum)`：`RESET=(0, SimpleAction)`、`ACTION1..5,7=(n, SimpleAction)`、`ACTION6=(6, ComplexAction)`；成员方法 `is_simple() / is_complex() / set_data(dict) / validate_data(dict)`；类方法 `from_id(int)`（无匹配抛 ValueError）、`from_name(str)`（大小写不敏感，内部 `cls[name.upper()]`，无匹配抛 ValueError）；`.value` 即 REST 动作编号 0–7。
- `class ActionInput(BaseModel)`：`id: GameAction`、`data: dict`、`reasoning: Optional[Any]`（field_validator 校验 JSON 可序列化且 ≤16KB）。
- `class FrameData(BaseModel)`：game_id/frame/list[list[list[int]]]/state/levels_completed/win_levels/action_input/guid/full_reset/available_actions —— **纯 JSON 形态**（REST 响应直配）。
- `class FrameDataRaw(BaseModel)`（step()/reset() 实际返回类型）：`game_id:str, state:GameState, levels_completed:int, win_levels:int, action_input:ActionInput, guid:Optional[str], full_reset:bool, available_actions:list[int]` + **`frame` 是 PrivateAttr 的 `List[ndarray]`（numpy 数组，运行时态、不参与序列化）——归一化为 JSON 必须逐帧 `.tolist()`**。

**arc_agi/base.py `Arcade.__init__` 逐参核实（与文档一致性确认）：**

```python
Arcade(arc_api_key: str = "", arc_base_url: str = "https://three.arcprize.org",
       operation_mode: OperationMode = OperationMode.NORMAL,
       environments_dir: str = "environment_files", recordings_dir: str = "recordings",
       logger: Optional[logging.Logger] = None)
```

- 各参数优先级：构造器实参 > 环境变量（ARC_API_KEY / ARC_BASE_URL / OPERATION_MODE / ENVIRONMENTS_DIR / RECORDINGS_DIR）> 默认值；`OperationMode`：NORMAL=本地+API、ONLINE=仅 API、OFFLINE=仅本地。
- `make(game_id, seed=0, scorecard_id=None, save_recording=False, include_frame_data=True, render_mode=None, renderer=None) -> Optional[EnvironmentWrapper]`；game_id 按 "-" 拆 base/version，OFFLINE 只搜本地扫描结果。
- `EnvironmentInfo(BaseModel)`：`game_id: str` 必填，`title/default_fps/tags/...` 可选。
- `arc_agi/wrapper.py`：基类 `reset() -> Optional[FrameDataRaw]`、`step(action: GameAction, data: Optional[dict], reasoning: Optional[dict]) -> Optional[FrameDataRaw]`、属性 `observation_space -> Optional[FrameDataRaw]`、`action_space -> list[GameAction]`、`info -> EnvironmentInfo`——失败路径一律返回 None 不抛异常。

**连通性实跑（2026-10-10，本机直连）：** `Arcade()` 匿名（无 ARC_API_KEY）在线模式 `get_environments()` 成功返回 25 局（vc33-5430563c/cd82-fb555c5d/bp35-0a0ad940/tn36-ef4dde99/sp80-589a99af/cn04-2fe56bfb 等）——SDK 在线匿名链路可用，B2 批验收的局侧实跑可行。

**算力侧实核（2026-10-10，ssh wsl）：** 远端算力机 = 单卡 RTX 4070 Laptop 8188MiB 显存 + 31GB 内存 + 937GB 可用盘，无 vLLM 进程/部署痕迹。**27B FP8（权重 ~27GB+）无法载入 8GB 卡**——"27B vLLM 裸基线实跑"在本机群不可达，属基础设施缺口（requirements 技术栈决策载明 vLLM 远端服务化，但现役 GPU 容量不足），已登记 B2 blocked 项待批间门用户裁决。

## 附：实核局限记录

- Agents 仓库 `agents/structs.py` 源码直抓 404（raw 与 blob 两路径均失败，仓库结构已变），`FrameDataRaw`/`GameAction` 的逐行类定义未能核对；字段清单以官方 REST FrameResponse + 仓库 README 改名记录交叉佐证。
- SDK 层（EnvironmentWrapper/LocalEnvironmentWrapper/RemoteEnvironmentWrapper）的异常类型与完整构造器签名文档未载明（environment_wrapper.md 明言 "Constructor signature: Not documented on this page"）。
- listen_and_serve（REST 包装服务）、competition_mode、scorecards、recordings 各页未逐一抓取正文（与本项目三函数弱相关）。
