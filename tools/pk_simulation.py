"""
PK 机制蒙特卡洛模拟器
=====================
验证 TASK002 方案 D 的数值设计是否满足预期。

核心公式：
  P(A赢) = sigmoid(k1·ln(Sa/Sb) + k2·(Wa-Wb))
  赢家获得 = base × 2(1-P_winner) × r
  输家损失 = base × 2(1-P_winner)
  ΔW = K × (E - S)    # 赢了降胜率，输了升胜率

用法:
  python tools/pk_simulation.py                  # 运行全部模拟
  python tools/pk_simulation.py --challenge      # 只跑挑战通关模拟
  python tools/pk_simulation.py --sweep          # 参数敏感性扫描
  python tools/pk_simulation.py --daily          # 日常 PK 期望模拟
"""

import math
import random
import argparse
from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# 1. 核心公式 —— 与 game.py 将要实现的完全一致
# ============================================================

# 默认参数
K1 = 0.5        # 长度权重
K2 = 3.0        # 胜率权重
K_ADJ = 0.03    # 胜率调整速度
R_RAKE = 0.5    # rake 率（赢家只拿输家损失的 r 倍）
W_MIN = 0.25    # 胜率下限
W_MAX = 0.75    # 胜率上限


def get_random_num() -> float:
    """与 game.py 一致的随机数生成器。
    0.1 概率 → U(1,2)，0.9 概率 → U(0,1)。
    期望 = 0.1×1.5 + 0.9×0.5 = 0.6
    """
    return random.uniform(1, 2) if random.random() <= 0.1 else random.uniform(0, 1)


def sigmoid(x: float) -> float:
    """数值稳定的 sigmoid。"""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    else:
        ex = math.exp(x)
        return ex / (1.0 + ex)


def calc_pk_probability(
    la: float, lb: float,
    wa: float, wb: float,
    k1: float = K1, k2: float = K2,
) -> float:
    """计算 A 的赢面 P(A wins)。"""
    sa = max(abs(la), 1.0)
    sb = max(abs(lb), 1.0)
    z = k1 * math.log(sa / sb) + k2 * (wa - wb)
    return sigmoid(z)


def calc_pk_rewards(base: float, p_winner: float, r: float = R_RAKE):
    """计算赢家获得和输家损失。
    Returns: (winner_gain, loser_loss)
    """
    t = base * 2.0 * (1.0 - p_winner)
    return t * r, t


def calc_win_rate_delta(expected: float, actual: float, k: float = K_ADJ) -> float:
    """ΔW = K × (E - S)。赢了(S=1)→降，输了(S=0)→升。"""
    return k * (expected - actual)


def clamp_wr(w: float) -> float:
    return max(W_MIN, min(W_MAX, w))


# ============================================================
# 2. 阶级挑战参数
# ============================================================

@dataclass
class TierConfig:
    tier: int
    name: str
    entry: float          # 进入挑战的长度（起始点）
    target: float         # 通关目标
    fail_line: float      # 失败线（跌破此线才算失败，低于 entry 提供缓冲）
    debuff: float         # 胜率乘法 debuff
    fail_penalty: float   # 失败后额外惩罚（长度设为 fail_line - penalty）
    reward_multiplier: float  # base 膨胀倍率
    challenge_r: Optional[float] = None  # 挑战期间特殊 rake 率（None = 用全局 r）


# 初始参数估计（将通过模拟迭代调整）
# 距离和缓冲按 step_units × step_size 标准化，step_size ≈ 0.6 × reward_multiplier
# challenge_r 是控制难度的主要旋钮（通过蒙特卡洛扫描确定）
# 无缓冲设计：fail_line = entry，第一把输就失败，每次尝试很快
DIST_STEP_UNITS = 5.5  # 距离占几个步长

def _make_tier(tier: int, name: str, entry: float, debuff: float,
               fail_penalty: float, mult: float, ch_r: float,
               dist_steps: float = DIST_STEP_UNITS,
               buffer_steps: float = 0.0) -> TierConfig:
    step = 0.6 * mult
    dist = dist_steps * step
    buf = buffer_steps * step
    return TierConfig(tier, name, entry, round(entry + dist, 1),
                      round(entry - buf, 1), debuff, fail_penalty, mult, ch_r)

TIER_CONFIGS = [
    # 无缓冲：fail_line = entry，第一把输就出局，每次尝试短促
    # challenge_r 需重新搜索以命中目标通关率
    _make_tier(1, "一阶", entry=25,   debuff=0.85, fail_penalty=3,   mult=1.5,  ch_r=0.85, dist_steps=5.5, buffer_steps=0),
    _make_tier(2, "二阶", entry=100,  debuff=0.80, fail_penalty=10,  mult=3.0,  ch_r=0.70, dist_steps=5.5, buffer_steps=0),
    _make_tier(3, "三阶", entry=500,  debuff=0.75, fail_penalty=30,  mult=8.0,  ch_r=0.65, dist_steps=5.5, buffer_steps=0),
    _make_tier(4, "四阶", entry=1500, debuff=0.70, fail_penalty=80,  mult=20.0, ch_r=0.55, dist_steps=5.5, buffer_steps=0),
    _make_tier(5, "五阶", entry=3000, debuff=0.65, fail_penalty=200, mult=50.0, ch_r=0.50, dist_steps=5.5, buffer_steps=0),
]


# ============================================================
# 3. 挑战通关模拟
# ============================================================

@dataclass
class ChallengeResult:
    success: bool
    pk_count: int
    final_length: float
    max_length: float
    min_length: float


def simulate_one_challenge(
    tier: TierConfig,
    opponent_length: Optional[float] = None,
    opponent_wr: float = 0.50,
    my_wr: float = 0.50,
    r: float = R_RAKE,
    max_pks: int = 5000,
) -> ChallengeResult:
    """模拟一次阶级挑战。

    挑战者从 entry 出发，目标 target，跌破 fail_line 失败。
    对手假设与自己长度差不多（默认 = 自身长度 ×0.95）。
    """
    length = tier.entry
    wr = my_wr
    max_l = length
    min_l = length
    eff_r = tier.challenge_r if tier.challenge_r is not None else r

    for pk_i in range(1, max_pks + 1):
        # 对手长度：默认取自身的 95%（略弱）
        opp_l = opponent_length if opponent_length else length * 0.95
        opp_wr = opponent_wr

        # 计算裸胜率
        p_raw = calc_pk_probability(length, opp_l, wr, opp_wr)
        # 施加挑战 debuff
        p_eff = p_raw * tier.debuff

        # 随机基底
        base = get_random_num() * tier.reward_multiplier

        # PK 结果
        if random.random() < p_eff:
            # 我赢了
            gain_me = base * 2.0 * (1.0 - p_eff) * eff_r
            length += gain_me
            delta_w = calc_win_rate_delta(p_eff, 1.0)
        else:
            # 我输了：对方赢面 = 1-p_eff，T = base × 2×p_eff
            loss_me = base * 2.0 * p_eff
            length -= loss_me
            delta_w = calc_win_rate_delta(p_eff, 0.0)

        wr = clamp_wr(wr + delta_w)
        max_l = max(max_l, length)
        min_l = min(min_l, length)

        # 成功检查
        if length >= tier.target:
            return ChallengeResult(True, pk_i, length, max_l, min_l)

        # 失败检查（跌破 fail_line）
        if length < tier.fail_line:
            return ChallengeResult(False, pk_i, length, max_l, min_l)

    # 超时
    return ChallengeResult(False, max_pks, length, max_l, min_l)


def run_challenge_simulation(n_trials: int = 10000, r: float = R_RAKE):
    """对每个阶级跑 n_trials 次模拟，统计通关率和 PK 次数。"""
    print("=" * 80)
    print(f"阶级挑战蒙特卡洛模拟  (N={n_trials:,}, rake r={r})")
    print("=" * 80)

    for tier in TIER_CONFIGS:
        successes = 0
        total_pks_success = 0
        total_pks_fail = 0
        fail_count = 0
        max_reached = []

        for _ in range(n_trials):
            result = simulate_one_challenge(tier, r=r)
            if result.success:
                successes += 1
                total_pks_success += result.pk_count
            else:
                fail_count += 1
                total_pks_fail += result.pk_count
            max_reached.append(result.max_length)

        rate = successes / n_trials * 100
        avg_pks_s = total_pks_success / successes if successes else 0
        avg_pks_f = total_pks_fail / fail_count if fail_count else 0

        # 最高到达的分位数
        max_reached.sort()
        p50 = max_reached[len(max_reached) // 2]
        p90 = max_reached[int(len(max_reached) * 0.9)]
        p99 = max_reached[int(len(max_reached) * 0.99)]

        dist = tier.target - tier.entry
        buffer = tier.entry - tier.fail_line
        print(f"\n{'─' * 60}")
        print(f"  {tier.name}  |  {tier.entry:.0f} → {tier.target:.0f}  (距离 {dist:.1f})  |  debuff ×{tier.debuff}")
        ch_r_str = f"  challenge_r={tier.challenge_r}" if tier.challenge_r else ""
        print(f"  缓冲 {buffer:.1f} (fail_line={tier.fail_line:.0f})  |  倍率 ×{tier.reward_multiplier}{ch_r_str}")
        print(f"{'─' * 60}")
        print(f"  通关率:                 {rate:6.2f}%  ({successes}/{n_trials})")
        print(f"  成功时平均 PK 次数:     {avg_pks_s:6.1f}")
        print(f"  失败时平均 PK 次数:     {avg_pks_f:6.1f}")
        print(f"  最高到达 (P50/P90/P99): {p50:.1f} / {p90:.1f} / {p99:.1f}")


# ============================================================
# 4. 日常 PK 期望验证
# ============================================================

def run_daily_pk_simulation(n_trials: int = 50000, r: float = R_RAKE):
    """验证不同对手强弱下的期望收益。"""
    print("\n" + "=" * 80)
    print(f"日常 PK 期望验证  (N={n_trials:,}, rake r={r})")
    print("=" * 80)

    scenarios = [
        ("势均力敌",    100, 100, 0.50, 0.50),
        ("略强 (1.5x)", 150, 100, 0.52, 0.50),
        ("强打弱 (3x)", 300, 100, 0.55, 0.50),
        ("碾压 (10x)",  1000, 100, 0.60, 0.50),
        ("弱打强",       50, 100, 0.50, 0.50),
        ("小号刷分",    100,  10, 0.55, 0.50),
    ]

    print(f"\n  {'场景':<16} {'P(A赢)':>8} {'E[ΔL_A]':>10} {'E[ΔL_B]':>10} {'理论E(÷base)':>14} {'实际验证':>8}")
    print(f"  {'─' * 70}")

    for name, la, lb, wa, wb in scenarios:
        total_delta_a = 0.0
        total_delta_b = 0.0
        total_base = 0.0

        p = calc_pk_probability(la, lb, wa, wb)

        for _ in range(n_trials):
            base = get_random_num()
            if random.random() < p:
                # A 赢
                gain, _ = calc_pk_rewards(base, p, r)
                loss = base * 2.0 * (1.0 - p)  # B 的损失：对方(A)赢面=p, T=base*2*(1-p)
                # 等等，让我理清：A赢时，赢家=A，赢家赢面=p
                # 赢家获得 = base * 2(1-p) * r
                # 输家损失 = base * 2(1-p)
                gain_a = base * 2.0 * (1.0 - p) * r
                loss_b = base * 2.0 * (1.0 - p)
                total_delta_a += gain_a
                total_delta_b -= loss_b
            else:
                # B 赢，赢家=B，赢家赢面=1-p
                gain_b = base * 2.0 * p * r      # 2(1-(1-p)) = 2p
                loss_a = base * 2.0 * p
                total_delta_a -= loss_a
                total_delta_b += gain_b
            total_base += base

        avg_delta_a = total_delta_a / n_trials
        avg_delta_b = total_delta_b / n_trials
        avg_base = total_base / n_trials
        theoretical = 2 * p * (1 - p) * (r - 1)  # 理论值 ÷ base

        print(f"  {name:<16} {p:>7.1%} {avg_delta_a:>+10.4f} {avg_delta_b:>+10.4f} "
              f"{theoretical:>+14.4f} {'✅' if abs(avg_delta_a / avg_base - theoretical) < 0.02 else '❌':>8}")


# ============================================================
# 5. Buff 窗口分析
# ============================================================

def run_buff_analysis(n_trials: int = 50000):
    """分析不同 buff 组合下 PK 的期望变化。"""
    print("\n" + "=" * 80)
    print(f"Buff 窗口期望分析  (N={n_trials:,})")
    print("=" * 80)

    # 场景：100cm vs 100cm, 双方 W=50%, 不同 buff 组合
    la, lb, wa, wb = 100, 100, 0.50, 0.50

    buff_combos = [
        ("裸 PK (无buff)",           0.5,  0.0),
        ("牛力加持 (+15% 收益)",       0.575, 0.0),   # r: 0.5*1.15
        ("牛力+运势 (+15%+20%)",      0.69,  0.0),   # r: 0.5*1.15*1.20
        ("以下犯上 (+8% 胜率)",        0.5,   0.08),
        ("牛力+以下犯上",             0.575, 0.08),
        ("全buff叠满 (r→0.8, P+10%)", 0.8,   0.10),
        ("极端buff (r→1.0, P+10%)",   1.0,   0.10),  # 期望应该 ≈ 0
        ("超极端 (r→1.2, P+10%)",     1.2,   0.10),  # 期望应该 > 0
    ]

    print(f"\n  {'Buff 组合':<30} {'有效r':>6} {'P_boost':>8} {'P(A赢)':>8} {'E[ΔL_A]/base':>14} {'判定':>8}")
    print(f"  {'─' * 78}")

    for name, eff_r, p_boost in buff_combos:
        p_base = calc_pk_probability(la, lb, wa, wb)
        p_eff = min(p_base + p_boost, 0.95)

        total_delta = 0.0
        total_base = 0.0

        for _ in range(n_trials):
            base = get_random_num()
            if random.random() < p_eff:
                gain = base * 2.0 * (1.0 - p_eff) * eff_r
                total_delta += gain
            else:
                loss = base * 2.0 * p_eff
                total_delta -= loss
            total_base += base

        avg_ratio = total_delta / total_base
        theoretical = 2 * p_eff * (1 - p_eff) * (eff_r - 1)

        if avg_ratio < -0.01:
            verdict = "亏损"
        elif avg_ratio > 0.01:
            verdict = "盈利 🎰"
        else:
            verdict = "持平"

        print(f"  {name:<30} {eff_r:>6.3f} {p_boost:>+7.0%} {p_eff:>7.1%} "
              f"{avg_ratio:>+14.4f} {verdict:>8}")


# ============================================================
# 6. 参数敏感性扫描
# ============================================================

def run_parameter_sweep(n_trials: int = 5000):
    """扫描关键参数 — 无缓冲设计 (fail_line = entry)。"""
    print("\n" + "=" * 80)
    print(f"参数敏感性扫描 — 无缓冲设计  (N={n_trials:,})")
    print("=" * 80)

    # ── 扫 1: dist_steps × challenge_r 全扫 (一阶, debuff=0.85) ──
    print(f"\n  --- dist_steps × challenge_r 扫描 (debuff=0.85, buffer=0, mult=1.5) ---")
    print(f"  {'dist_s':>6} {'ch_r':>6} {'通关率':>8} {'成功PK':>8} {'失败PK':>8}")
    for dist_steps in [1, 2, 3, 4, 5.5]:
        for ch_r in [0.8, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0]:
            t = _make_tier(1, "一阶", 25, 0.85, 3, 1.5, ch_r,
                           dist_steps=dist_steps, buffer_steps=0)
            results = [simulate_one_challenge(t, r=0.5) for _ in range(n_trials)]
            s = [x for x in results if x.success]
            f = [x for x in results if not x.success]
            avg_s = sum(x.pk_count for x in s) / len(s) if s else 0
            avg_f = sum(x.pk_count for x in f) / len(f) if f else 0
            rate = len(s) / n_trials * 100
            marker = " ◀" if 25 <= rate <= 35 else ""
            print(f"  {dist_steps:>6.1f} {ch_r:>6.2f} {rate:>7.1f}%{marker} {avg_s:>8.1f} {avg_f:>8.1f}")
        print()

    # ── 扫 2: 全阶级 challenge_r 搜索 (固定 dist_steps) ──
    print(f"\n  {'=' * 70}")
    print(f"  全阶级 challenge_r 搜索 — 无缓冲")
    print(f"  {'=' * 70}")

    target_rates = {1: 0.30, 2: 0.15, 3: 0.08, 4: 0.03, 5: 0.01}

    for tier_num in range(1, 6):
        target_rate = target_rates[tier_num]
        cfg = TIER_CONFIGS[tier_num - 1]
        step = 0.6 * cfg.reward_multiplier
        dist_steps = (cfg.target - cfg.entry) / step  # 从当前配置反推

        print(f"\n  --- {cfg.name} (step≈{step:.1f}, dist_steps={dist_steps:.1f}, debuff={cfg.debuff}) ---")
        print(f"  目标通关率: {target_rate:.0%}")
        print(f"  {'ch_r':>6} {'通关率':>8} {'成功PK':>8} {'失败PK':>8}")

        best_r = 0.5
        best_diff = 1.0
        for ch_r_x10 in range(50, 250, 10):
            ch_r = ch_r_x10 / 100.0
            t = _make_tier(tier_num, cfg.name,
                           cfg.entry, cfg.debuff,
                           cfg.fail_penalty, cfg.reward_multiplier,
                           ch_r, dist_steps=dist_steps, buffer_steps=0)
            results = [simulate_one_challenge(t, r=0.5) for _ in range(n_trials)]
            s = [x for x in results if x.success]
            f = [x for x in results if not x.success]
            rate = len(s) / n_trials
            avg_s = sum(x.pk_count for x in s) / len(s) if s else 0
            avg_f = sum(x.pk_count for x in f) / len(f) if f else 0
            marker = " ◀" if abs(rate - target_rate) < 0.05 else ""
            print(f"  {ch_r:>6.2f} {rate*100:>7.1f}%{marker} {avg_s:>8.1f} {avg_f:>8.1f}")
            if abs(rate - target_rate) < best_diff:
                best_diff = abs(rate - target_rate)
                best_r = ch_r
        print(f"  → 最佳 challenge_r = {best_r:.2f} (偏差 {best_diff*100:.1f}%)")


# ============================================================
# 7. 胜率收敛验证
# ============================================================

def run_winrate_convergence(n_pks: int = 500, n_trials: int = 5000):
    """验证胜率调整的自平衡性：两个相同实力的人 PK 多次后胜率是否稳定。"""
    print("\n" + "=" * 80)
    print(f"胜率收敛验证  (每组{n_pks}把 PK, N={n_trials:,})")
    print("=" * 80)

    scenarios = [
        ("等长等率",    10, 10, 0.50, 0.50),
        ("A胜率偏高",   10, 10, 0.65, 0.50),
        ("A长度偏高",   20, 10, 0.50, 0.50),
        ("A全面碾压",   50, 10, 0.65, 0.40),
    ]

    for name, la0, lb0, wa0, wb0 in scenarios:
        final_wa = []
        final_wb = []
        a_wins_total = 0

        for _ in range(n_trials):
            la, lb, wa, wb = la0, lb0, wa0, wb0
            a_wins = 0
            for _ in range(n_pks):
                p = calc_pk_probability(la, lb, wa, wb)
                base = get_random_num()
                if random.random() < p:
                    # A 赢
                    gain_a = base * 2.0 * (1.0 - p) * R_RAKE
                    loss_b = base * 2.0 * (1.0 - p)
                    la += gain_a
                    lb -= loss_b
                    wa = clamp_wr(wa + calc_win_rate_delta(p, 1.0))
                    wb = clamp_wr(wb + calc_win_rate_delta(1 - p, 0.0))
                    a_wins += 1
                else:
                    # B 赢
                    gain_b = base * 2.0 * p * R_RAKE
                    loss_a = base * 2.0 * p
                    la -= loss_a
                    lb += gain_b
                    wa = clamp_wr(wa + calc_win_rate_delta(p, 0.0))
                    wb = clamp_wr(wb + calc_win_rate_delta(1 - p, 1.0))

                # 长度保底 1
                la = max(la, 1.0)
                lb = max(lb, 1.0)

            final_wa.append(wa)
            final_wb.append(wb)
            a_wins_total += a_wins

        avg_wa = sum(final_wa) / len(final_wa)
        avg_wb = sum(final_wb) / len(final_wb)
        avg_wr = a_wins_total / (n_trials * n_pks)

        print(f"\n  {name}: 初始 A({la0}cm,{wa0:.0%}) vs B({lb0}cm,{wb0:.0%})")
        print(f"    {n_pks}把后 → A胜率均值={avg_wa:.3f}, B胜率均值={avg_wb:.3f}")
        print(f"    A实际胜率={avg_wr:.1%}")
        print(f"    {'✅ 收敛' if abs(avg_wa - avg_wb) < 0.10 else '⚠️ 未充分收敛'}")


# ============================================================
# 8. 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="PK 机制蒙特卡洛模拟器")
    parser.add_argument("--challenge", action="store_true", help="只跑挑战通关模拟")
    parser.add_argument("--daily", action="store_true", help="只跑日常 PK 期望")
    parser.add_argument("--buff", action="store_true", help="只跑 buff 窗口分析")
    parser.add_argument("--sweep", action="store_true", help="只跑参数敏感性扫描")
    parser.add_argument("--convergence", action="store_true", help="只跑胜率收敛验证")
    parser.add_argument("-n", "--trials", type=int, default=10000, help="模拟次数 (默认 10000)")
    parser.add_argument("-r", "--rake", type=float, default=0.5, help="rake 率 (默认 0.5)")
    args = parser.parse_args()

    any_specific = args.challenge or args.daily or args.buff or args.sweep or args.convergence
    run_all = not any_specific

    if run_all or args.challenge:
        run_challenge_simulation(n_trials=args.trials, r=args.rake)

    if run_all or args.daily:
        run_daily_pk_simulation(n_trials=min(args.trials * 5, 50000), r=args.rake)

    if run_all or args.buff:
        run_buff_analysis(n_trials=min(args.trials * 5, 50000))

    if run_all or args.sweep:
        run_parameter_sweep(n_trials=min(args.trials, 5000))

    if run_all or args.convergence:
        run_winrate_convergence(n_trials=min(args.trials, 5000))

    print("\n\n✅ 模拟完成。")


if __name__ == "__main__":
    main()
