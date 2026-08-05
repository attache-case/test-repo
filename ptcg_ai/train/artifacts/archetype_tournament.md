# Archetype Tournament Crosstable

Round-robin, our own agent piloting both sides, alternating seats, full production search budget. See `card_pool_catalog.md` for card details and `strategy_report.md` for analysis.

## Decks

- `v3_champion`: v3 (champion): Kyogre/Snover-MegaAbomasnowEx/Chien-Pao
- `t1_lightning_aggro`: T1: Lightning Big-Basic Aggro (Pikachu ex/Zekrom ex/Tapu Koko ex)
- `t2_grass_stage2`: T2: Grass Stage-2 Powerhouse (Mega Venusaur ex + Rare Candy)
- `t3_tera_box`: T3: Tera Box (Water/Fighting/Colorless)
- `t4_fighting_spread`: T4: Fighting Spread/Bench-damage (Stonjourner/Ting-Lu/Terrakion)
- `t5_colorless_stall`: T5: Colorless Disruption/Stall (Snorlax/Regigigas/Hop's Snorlax)

## Crosstable (row's winrate vs column)

| vs | v3_champion | t1_lightning_aggro | t2_grass_stage2 | t3_tera_box | t4_fighting_spread | t5_colorless_stall |
|---|---|---|---|---|---|---|
| **v3_champion** | - | 80% (30) | 90% (30) | 83% (30) | 77% (30) | 97% (30) |
| **t1_lightning_aggro** | 20% (30) | - | 67% (30) | 70% (30) | 10% (30) | 73% (30) |
| **t2_grass_stage2** | 10% (30) | 33% (30) | - | 30% (30) | 62% (30) | 60% (30) |
| **t3_tera_box** | 17% (30) | 30% (30) | 70% (30) | - | 70% (30) | 27% (30) |
| **t4_fighting_spread** | 23% (30) | 87% (30) | 38% (30) | 30% (30) | - | 83% (30) |
| **t5_colorless_stall** | 3% (30) | 27% (30) | 40% (30) | 73% (30) | 17% (30) | - |

## Overall ranking

| Rank | Deck | Overall winrate | Games | Elo-ish rating |
|---|---|---:|---:|---:|
| 1 | `v3_champion` | 85.3% | 150 | 1757 |
| 2 | `t4_fighting_spread` | 52.3% | 149 | 1630 |
| 3 | `t5_colorless_stall` | 32.0% | 150 | 1514 |
| 4 | `t1_lightning_aggro` | 48.0% | 150 | 1379 |
| 5 | `t3_tera_box` | 42.7% | 150 | 1363 |
| 6 | `t2_grass_stage2` | 38.9% | 149 | 1356 |

Total bad-status games across the tournament: 1.
