# Card Pool Catalog

Mined from `AllCard.json` (1267 cards) / `AllAttack.json` (1556 attacks) via `lib.AllCard()`/`lib.AllAttack()`. This is a Scarlet/Violet + Mega-era-style card pool (rule-box flags: `ex`, `megaEx`, `tera`, `aceSpec`), with many cards using invented names but real-world-recognizable mechanics (and a few exact real names, e.g. **Boss's Orders**, **Rare Candy**, **Ultra Ball**).

## Overview

- 1056 Pokemon: 595 Basic, 345 Stage 1, 116 Stage 2, 121 `ex`, 30 `megaEx`, 32 `tera`, 218 with an Ability.
- 191 Trainers: 77 Item, 27 Tool, 61 Supporter, 26 Stadium.
- 8 Basic Energy types (ids 1-8, uncapped copies), plus Special Energy (cardType 6, capped at 4 like any other card) and 29 ACE SPEC cards (deck-wide cap of 1).

## Strong Basic attackers, by energy type

Non-evolving Basics with HP>=90 and at least one attack dealing >=60 damage, sorted by HP within type. These are the best PIMC-friendly basic-only attackers (no multi-turn evolution sequencing needed).

### Colorless (-)

- **Mega Kangaskhan ex** [megaEx] (id 756, Colorless, 300HP, retreat 3): Rapid-Fire Combo (200dmg/3en, 67/en) -- Ability * Run Errand*: Once during your turn, if this Pokémon is in the Active Spot, you may use this Ability. Draw 2 cards. You can’t use more than 1 Run Errand A
- **Bloodmoon Ursaluna ex** [ex] (id 44, Colorless, 260HP, retreat 3): Blood Moon (240dmg/5en, 48/en) -- Ability *Seasoned Skill*: Blood Moon used by this Pokémon costs {C} less for each Prize card your opponent has taken.
- **Team Rocket's Kangaskhan ex** [ex] (id 24, Colorless, 230HP, retreat 2): Comet Punch (0dmg/2en, 0/en); Wicked Impact (120dmg/3en, 40/en)
- **Terapagos ex** [ex,tera] (id 176, Colorless, 230HP, retreat 2): Unified Beatdown (0dmg/2en, 0/en); Crown Opal (180dmg/3en, 60/en)
- **LugiaEX** [ex] (id 337, Colorless, 220HP, retreat 2): Hyper Whirlpool (140dmg/3en, 47/en)
- **Bouffalant ex** [ex] (id 631, Colorless, 220HP, retreat 2): Gold Breaker (100dmg/3en, 33/en) -- Ability * Bouffer*: This Pokémon takes 30 less damage from attacks (after applying Weakness and Resistance).
- **Eevee ex** [ex,tera] (id 249, Colorless, 200HP, retreat 1): Coruscating Quartz (200dmg/3en, 67/en) -- Ability *Rainbow DNA*: This Pokémon can evolve into any Pokémon {ex} that evolves from Eevee if you play it from your hand onto this Pokémon. (This Pokémon can’t e
- **Zangoose ex** [ex] (id 1002, Colorless, 200HP, retreat 1): Spike Draw (20dmg/1en, 20/en); Wild Scissors (180dmg/3en, 60/en)
- **Meowth ex** [ex] (id 1071, Colorless, 170HP, retreat 1): Tuck Tail (60dmg/3en, 20/en) -- Ability * Last-Ditch Catch*: Once during your turn, when you play this Pokémon from your hand onto your Bench, you may use this Ability. Search your deck for a Supporter
- **Regigigas** (id 251, Colorless, 160HP, retreat 4): Jewel Breaker (100dmg/4en, 25/en)
- **Snorlax** (id 1072, Colorless, 160HP, retreat 4): Gormandizer (0dmg/1en, 0/en); Collapse (160dmg/4en, 40/en)
- **Hop’s Snorlax** (id 304, Colorless, 150HP, retreat 4): Dynamic Press (140dmg/3en, 47/en) -- Ability *Extra Helpings*: Attacks used by your Hop’s Pokémon do 30 more damage to your opponent’s Active Pokémon (before applying Weakness and Resistance). The effect

### Grass (1)

- **Mega Heracross ex** [megaEx] (id 781, Grass, 280HP, retreat 2): Juggernaut Horn (100dmg/2en, 50/en); Mountain Ramming (170dmg/3en, 57/en)
- **Iron Leaves ex** [ex] (id 75, Grass, 220HP, retreat 1): Prism Edge (180dmg/3en, 60/en) -- Ability *Rapid Vernier*: When you play this Pokémon from your hand onto your Bench during your turn, you may switch it with your Active Pokémon. If you do, you may m
- **Durant ex** [ex] (id 198, Grass, 190HP, retreat 2): Vengeful Crush (120dmg/3en, 40/en) -- Ability *Sudden Shearing*: When you play this Pokémon from your hand onto your Bench during your turn, you may discard the top card of your opponent’s deck.
- **Tapu Bulu** (id 920, Grass, 140HP, retreat 3): Wood Hammer (220dmg/4en, 55/en)
- **Wo-Chien** (id 201, Grass, 130HP, retreat 3): Hazardous Greed (20dmg/2en, 10/en); Entangling Whip (130dmg/3en, 43/en)
- **Iron Leaves** (id 27, Grass, 120HP, retreat 1): Recovery Net (0dmg/1en, 0/en); Avenging Edge (100dmg/3en, 33/en)
- **Zarude** (id 178, Grass, 120HP, retreat 1): Leaf Drain (20dmg/1en, 20/en); Jungle Whip (80dmg/3en, 27/en)
- **Ethan's Pinsir** (id 338, Grass, 120HP, retreat 2): Vise Grip (20dmg/1en, 20/en); Rallying Horn (70dmg/3en, 23/en)
- **Virizion** (id 566, Grass, 120HP, retreat 1): Giga Drain (30dmg/1en, 30/en); Emerald Blade (130dmg/3en, 43/en)
- **Genesect** (id 785, Grass, 120HP, retreat 2): Bug’s Cannon (0dmg/1en, 0/en); Speed Attack (110dmg/3en, 37/en)
- **Pinsir** (id 25, Grass, 110HP, retreat 2): Slow Crunch (0dmg/2en, 0/en); Superpowered Horns (100dmg/3en, 33/en)
- **Teal Mask Ogerpon** (id 349, Grass, 110HP, retreat 1): Grass Kagura (0dmg/1en, 0/en); Ogre’s Hammer (120dmg/3en, 40/en)

### Fire (2)

- **Gouging Fire ex** [ex] (id 46, Fire, 230HP, retreat 2): Heat Blast (60dmg/2en, 30/en); Blaze Blitz (260dmg/3en, 87/en)
- **Ethan's Ho-Oh ex** [ex] (id 357, Fire, 230HP, retreat 2): Shining Feathers (160dmg/4en, 40/en) -- Ability * Golden Flame*: Once during your turn, you may attach up to 2 Basic {R} Energy cards from your hand to 1 of your Benched Ethan’s Pokémon.
- **Reshiram ex** [ex] (id 573, Fire, 230HP, retreat 2): Slash (50dmg/2en, 25/en); Blazing Burst (130dmg/3en, 43/en)
- **Volcanion ex** [ex] (id 259, Fire, 220HP, retreat 3): Scorching Cyclone (160dmg/3en, 53/en) -- Ability *Scalding Steam*: Once during your turn, if this Pokémon is in the Active Spot, you may make your opponent’s Active Pokémon Burned.
- **Team Rocket's Moltres ex** [ex] (id 407, Fire, 220HP, retreat 2): Flame Screen (110dmg/3en, 37/en); Evil Incineration (0dmg/4en, 0/en)
- **Hearthflame Mask Ogerpon ex** [ex,tera] (id 99, Fire, 210HP, retreat 1): Wrathful Hearth (0dmg/3en, 0/en); Dynamic Blaze (140dmg/3en, 47/en)
- **Oricorio ex** [ex] (id 795, Fire, 190HP, retreat 1): Fire Wing (110dmg/3en, 37/en) -- Ability * Excited Turbo*: As often as you like during your turn, if you have any {R} Mega Evolution Pokémon {ex} in play, you may use this Ability. Attach a Basic {R}
- **Ho-Oh** (id 318, Fire, 130HP, retreat 2): Flap (50dmg/2en, 25/en); Shining Blaze (100dmg/3en, 33/en)
- **Volcanion** (id 663, Fire, 130HP, retreat 2): Singe (0dmg/1en, 0/en); Backfire (130dmg/3en, 43/en)
- **Reshiram** (id 794, Fire, 130HP, retreat 2): Combustion (30dmg/1en, 30/en); Burning Flare (240dmg/4en, 60/en)
- **Heatmor** (id 572, Fire, 120HP, retreat 2): Licking Catch (0dmg/1en, 0/en); Fire Claws (60dmg/2en, 30/en)
- **Turtonator** (id 1027, Fire, 120HP, retreat 2): Heat Breath (80dmg/3en, 27/en) -- Ability * Shell Spikes*: If this Pokémon is in the Active Spot and is damaged by an attack from your opponent’s Pokémon (even if this Pokémon is Knocked Out), discar

### Water (3)

- **Dondozo ex** [ex] (id 369, Water, 260HP, retreat 4): Avenging Billow (30dmg/2en, 15/en); Dynamic Dive (120dmg/4en, 30/en)
- **Black Kyurem ex** [ex] (id 179, Water, 230HP, retreat 3): Ice Age (90dmg/3en, 30/en); Black Frost (250dmg/4en, 62/en)
- **Kyurem ex** [ex] (id 509, Water, 230HP, retreat 2): Slash (50dmg/2en, 25/en); Blizzard Burst (130dmg/3en, 43/en)
- **Regice ex** [ex] (id 944, Water, 230HP, retreat 3): Regi Charge (0dmg/1en, 0/en); Ice Prison (140dmg/4en, 35/en)
- **Wellspring Mask Ogerpon ex** [ex,tera] (id 108, Water, 210HP, retreat 1): Sob (20dmg/1en, 20/en); Torrential Pump (100dmg/3en, 33/en)
- **Keldeo ex** [ex] (id 583, Water, 210HP, retreat 2): Gale Thrust (30dmg/2en, 15/en); Sonic Edge (120dmg/3en, 40/en)
- **Kyogre** (id 721, Water, 150HP, retreat 3): Riptide (0dmg/1en, 0/en); Swirling Waves (130dmg/3en, 43/en)
- **Veluza** (id 159, Water, 130HP, retreat 2): Sonic Edge (110dmg/4en, 28/en) -- Ability *Food Prep*: Attacks used by this Pokémon cost {C} less for each Kofu card in your discard pile.
- **Wailmer** (id 263, Water, 130HP, retreat 3): Surf (60dmg/3en, 20/en)
- **Glastrier** (id 867, Water, 130HP, retreat 2): Ice Shot (20dmg/1en, 20/en); Frosty Typhoon (130dmg/3en, 43/en)
- **Chien-Pao** (id 209, Water, 120HP, retreat 1): Icicle Loop (120dmg/3en, 40/en) -- Ability *Snow Sink*: When you play this Pokémon from your hand onto your Bench during your turn, you may discard a Stadium in play.
- **Team Rocket's Articuno** (id 414, Water, 120HP, retreat 1): Dark Frost (60dmg/3en, 20/en) -- Ability * Repelling Veil*: Prevent all effects of attacks used by your opponent’s Pokémon done to your Basic Team Rocket’s Pokémon. (Existing effects are not removed. 

### Lightning (4)

- **Iron Thorns ex** [ex] (id 37, Lightning, 230HP, retreat 4): Volt Cyclone (140dmg/3en, 47/en) -- Ability *Initialization*: As long as this Pokémon is in the Active Spot, Pokémon with a Rule Box in play (both yours and your opponent’s) have no Abilities, except fo
- **Zekrom ex** [ex] (id 515, Lightning, 230HP, retreat 2): Slash (50dmg/2en, 25/en); Voltage Burst (130dmg/3en, 43/en)
- **Miraidon ex** [ex,tera] (id 957, Lightning, 220HP, retreat 1): Slashing Claw (40dmg/1en, 40/en); Hadron Spark (120dmg/3en, 40/en)
- **Pikachu ex** [ex,tera] (id 210, Lightning, 200HP, retreat 1): Topaz Bolt (300dmg/3en, 100/en) -- Ability *Resolute Heart*: If this Pokémon has full HP and would be Knocked Out by damage from an attack, it is not Knocked Out, and its remaining HP becomes 10.
- **Tapu Koko ex** [ex] (id 329, Lightning, 200HP, retreat 0): Linked Lightning (60dmg/2en, 30/en)
- **Pikachu ex** [ex] (id 328, Lightning, 190HP, retreat 1): Tail Whap (30dmg/1en, 30/en); Thunder (220dmg/3en, 73/en)
- **Rotom ex** [ex] (id 806, Lightning, 190HP, retreat 1): Thunderbolt (130dmg/2en, 65/en) -- Ability * Multi Adapter*: Each of your Pokémon that has "Rotom" in its name may have up to 2 Pokémon Tool cards attached. If this Ability goes away, discard Pokémon T
- **Voltorb ex** [ex] (id 951, Lightning, 170HP, retreat 1): Hundred-Hitting Ball (100dmg/3en, 33/en)
- **Tapu Koko** (id 213, Lightning, 120HP, retreat 1): Summon Lightning (0dmg/1en, 0/en); Prize Count (90dmg/3en, 30/en)
- **Team Rocket's Zapdos** (id 425, Lightning, 120HP, retreat 1): Jamming Wing (30dmg/2en, 15/en); Wicked Thunder (60dmg/3en, 20/en)
- **Thundurus** (id 514, Lightning, 120HP, retreat 1): Charge (0dmg/1en, 0/en); Disaster Volt (110dmg/3en, 37/en)
- **Tapu Koko** (id 872, Lightning, 120HP, retreat 1): Fast Flight (0dmg/1en, 0/en); Thunder Blast (130dmg/3en, 43/en)

### Psychic (5)

- **Team Rocket's Mewtwo ex** [ex] (id 431, Psychic, 280HP, retreat 3): Erasure Ball (160dmg/3en, 53/en) -- Ability * Power Saver*: This Pokémon can’t attack unless you have 4 or more Team Rocket’s Pokémon in play.
- **Latias ex** [ex] (id 184, Psychic, 210HP, retreat 2): Eon Blade (200dmg/3en, 67/en) -- Ability *Skyliner*: Your Basic Pokémon in play have no Retreat Cost.
- **XerneasEX** [ex] (id 331, Psychic, 210HP, retreat 1): Aurora Beam (50dmg/2en, 25/en); Rising Horns (120dmg/3en, 40/en)
- **Scream Tail ex** [ex] (id 969, Psychic, 190HP, retreat 1): Scream (0dmg/1en, 0/en); Crunch (120dmg/3en, 40/en)
- **Iron Boulder** (id 971, Psychic, 140HP, retreat 3): Adjusted Horn (170dmg/2en, 85/en)
- **Dhelmise** (id 332, Psychic, 130HP, retreat 3): Bind Down (60dmg/3en, 20/en); Anchor Smash (130dmg/4en, 32/en)
- **Enamorus** (id 39, Psychic, 120HP, retreat 1): Heart Sign (30dmg/1en, 30/en); Love Resonance (80dmg/3en, 27/en)
- **Xerneas** (id 751, Psychic, 120HP, retreat 1): Geo Gate (0dmg/1en, 0/en); Bright Horns (120dmg/3en, 40/en)
- **Cresselia** (id 764, Psychic, 120HP, retreat 1): Swelling Light (0dmg/1en, 0/en); Aurora Beam (90dmg/3en, 30/en)
- **Munkidori** (id 112, Psychic, 110HP, retreat 1): Mind Bend (60dmg/2en, 30/en) -- Ability *Adrena-Brain*: Once during your turn, if this Pokémon has any {D} Energy attached, you may move up to 3 damage counters from 1 of your Pokémon to 1 of your
- **Team Rocket's Wobbuffet** (id 432, Psychic, 110HP, retreat 2): Rocket Mirror (0dmg/2en, 0/en); Headbutt Bounce (70dmg/3en, 23/en)
- **Flutter Mane** (id 56, Psychic, 90HP, retreat 1): Hex Hurl (90dmg/3en, 30/en) -- Ability *Midnight Fluttering*: As long as this Pokémon is in the Active Spot, your opponent’s Active Pokémon has no Abilities, except for Midnight Fluttering.

### Fighting (6)

- **Mega Zygarde ex** [megaEx] (id 1056, Fighting, 310HP, retreat 2): Gaia Wave (200dmg/3en, 67/en); Nullifying Zero (0dmg/5en, 0/en)
- **Mega Hawlucha ex** [megaEx] (id 886, Fighting, 250HP, retreat 1): Somersault Dive (120dmg/3en, 40/en) -- Ability * Tenacious Body*: If this Pokémon would be Knocked Out by damage from an attack, flip a coin. If heads, this Pokémon is not Knocked Out, and its remaining HP 
- **Regirock ex** [ex] (id 447, Fighting, 230HP, retreat 3): Regi Charge (0dmg/1en, 0/en); Giant Rock (140dmg/4en, 35/en)
- **Koraidon ex** [ex,tera] (id 979, Fighting, 230HP, retreat 2): Tera (50dmg/2en, 25/en); Orichalcum Fang (200dmg/3en, 67/en)
- **Cornerstone Mask Ogerpon ex** [ex,tera] (id 117, Fighting, 210HP, retreat 1): Demolish (140dmg/3en, 47/en) -- Ability *Cornerstone Stance*: Prevent all damage from attacks done to this Pokémon by your opponent’s Pokémon that have an Ability.
- **Stunfisk ex** [ex] (id 975, Fighting, 210HP, retreat 2): Big Bite (30dmg/1en, 30/en); Flopping Trap (100dmg/3en, 33/en)
- **Bloodmoon Ursaluna** (id 135, Fighting, 150HP, retreat 4): Mad Bite (100dmg/3en, 33/en) -- Ability *Battle-Hardened*: When you play this Pokémon from your hand onto your Bench during your turn, you may attach up to 2 Basic {F} Energy cards from your hand to 
- **Ting-Lu** (id 41, Fighting, 140HP, retreat 3): Ground Crasher (30dmg/1en, 30/en); Hammer In (110dmg/3en, 37/en)
- **Great Tusk** (id 58, Fighting, 140HP, retreat 3): Land Collapse (0dmg/2en, 0/en); Giant Tusk (160dmg/4en, 40/en)
- **Terrakion** (id 607, Fighting, 140HP, retreat 3): Retaliate (50dmg/2en, 25/en); Land Crush (100dmg/3en, 33/en)
- **Okidogi** (id 890, Fighting, 140HP, retreat 3): Light Punch (20dmg/1en, 20/en); Settle the Score (80dmg/3en, 27/en)
- **Groudon** (id 973, Fighting, 140HP, retreat 3): Hammer In (80dmg/3en, 27/en); Megaton Fall (150dmg/4en, 38/en)

### Darkness (7)

- **Mega Absol ex** [megaEx] (id 687, Darkness, 280HP, retreat 2): Terminal Period (0dmg/2en, 0/en); Claw of Darkness (200dmg/3en, 67/en)
- **Okidogi ex** [ex] (id 138, Darkness, 250HP, retreat 3): Poisonous Musculature (0dmg/1en, 0/en); Chain-Crazed (130dmg/3en, 43/en)
- **Munkidori ex** [ex] (id 139, Darkness, 210HP, retreat 1): Dirty Headbutt (190dmg/3en, 63/en) -- Ability *Oh No You Don’t*: If this Pokémon is Knocked Out by damage from an attack from your opponent’s Pokémon, and if you have any Pecharunt {ex} in play, your oppon
- **Yveltal ex** [ex] (id 1062, Darkness, 210HP, retreat 1): Soul Destroyer (0dmg/3en, 0/en); Dark Strike (210dmg/3en, 70/en)
- **Eternatus** (id 777, Darkness, 150HP, retreat 2): Shatter (50dmg/2en, 25/en); Power Rush (130dmg/3en, 43/en)
- **Roaring Moon** (id 61, Darkness, 140HP, retreat 2): Vengeance Fletching (70dmg/2en, 35/en); Speed Wing (120dmg/4en, 30/en)
- **Seviper** (id 829, Darkness, 120HP, retreat 1): Pitch-Black Fangs (120dmg/3en, 40/en) -- Ability * Excited Power*: If you have any {D} Mega Evolution Pokémon {ex} in play, attacks used by this Pokémon do 120 more damage to your opponent’s Active Pokémon (
- **Hoopa** (id 985, Darkness, 120HP, retreat 2): Filch (0dmg/1en, 0/en); Knuckle Impact (130dmg/3en, 43/en)
- **Chien-Pao** (id 1063, Darkness, 120HP, retreat 1): Strafe (20dmg/1en, 20/en); Rising Blade (80dmg/3en, 27/en)
- **Yveltal** (id 689, Darkness, 110HP, retreat 0): Clutch (20dmg/1en, 20/en); Dark Feather (110dmg/3en, 37/en)
- **Absol** (id 776, Darkness, 110HP, retreat 1): Allure (0dmg/1en, 0/en); Dark Cutter (60dmg/2en, 30/en)

### Metal (8)

- **Mega Mawile ex** [megaEx] (id 695, Metal, 270HP, retreat 2): Gobble Down (0dmg/2en, 0/en); Huge Bite (260dmg/3en, 87/en)
- **Hop’s Zacian ex** [ex] (id 299, Metal, 230HP, retreat 2): Insta-Strike (30dmg/1en, 30/en); Brave Slash (240dmg/4en, 60/en)
- **Registeel ex** [ex] (id 988, Metal, 230HP, retreat 3): Regi Charge (0dmg/1en, 0/en); Protecting Steel (140dmg/4en, 35/en)
- **Zacian ex** [ex] (id 336, Metal, 220HP, retreat 2): Steel Armament (20dmg/1en, 20/en); Slashing Strike (210dmg/3en, 70/en)
- **Genesect ex** [ex] (id 547, Metal, 220HP, retreat 2): Protect Charge (150dmg/3en, 50/en) -- Ability * Metallic Signal*: Once during your turn, you may search your deck for up to 2 Evolution {M} Pokémon, reveal them, and put them into your hand. Then, shuffle y
- **Orthworm ex** [ex] (id 993, Metal, 220HP, retreat 4): Rock Tomb (150dmg/4en, 38/en) -- Ability * Pummeling Payback*: If this Pokémon is damaged by an attack from your opponent’s Pokémon (even if this Pokémon is Knocked Out), place 2 damage counters on the A
- **Togedemaru ex** [ex] (id 990, Metal, 190HP, retreat 1): Stun Needle (20dmg/1en, 20/en); Spiky Rolling (80dmg/2en, 40/en)
- **Dialga** (id 696, Metal, 140HP, retreat 2): Beam (30dmg/1en, 30/en); Chrono Burst (80dmg/3en, 27/en)
- **Duraludon** (id 169, Metal, 130HP, retreat 2): Hammer In (30dmg/1en, 30/en); Raging Hammer (80dmg/3en, 27/en)
- **Iron Crown** (id 192, Metal, 130HP, retreat 2): Deleting Slash (40dmg/2en, 20/en); Slicing Blade (100dmg/3en, 33/en)
- **Zamazenta** (id 467, Metal, 130HP, retreat 2): Strong Bash (70dmg/3en, 23/en)
- **Duraludon** (id 839, Metal, 130HP, retreat 2): Hyper Beam (70dmg/3en, 23/en)

### Dragon (-)

- **Mega Latias ex** [megaEx] (id 754, Dragon, 280HP, retreat 1): Strafe (40dmg/1en, 40/en); Illusory Impulse (300dmg/3en, 100/en)
- **Miraidon ex** [ex] (id 313, Dragon, 220HP, retreat 1): Repulsion Bolt (60dmg/2en, 30/en); Cyber Drive (220dmg/3en, 73/en)
- **Tatsugiri ex** [ex,tera] (id 231, Dragon, 160HP, retreat 1): Surprise Pump (100dmg/2en, 50/en); Cinnabar Lure (0dmg/3en, 0/en)
- **Koraidon** (id 62, Dragon, 140HP, retreat 2): Primordial Beatdown (0dmg/2en, 0/en); Shred (130dmg/3en, 43/en)
- **Raging Bolt** (id 171, Dragon, 130HP, retreat 3): Thunderburst Storm (0dmg/2en, 0/en); Dragon Headbutt (130dmg/3en, 43/en)
- **Dialga** (id 195, Dragon, 130HP, retreat 2): Time Manipulation (0dmg/1en, 0/en); Buster Tail (160dmg/3en, 53/en)
- **N’s Reshiram** (id 303, Dragon, 130HP, retreat 2): Powerful Rage (0dmg/2en, 0/en); Virtuous Flame (170dmg/4en, 42/en)
- **Latios** (id 755, Dragon, 130HP, retreat 1): Dragon Claw (130dmg/3en, 43/en) -- Ability * Lustrous Assist*: Once during your turn, when your Mega Latias {ex} moves from your Bench to the Active Spot, you may use this Ability. Move any amount of Ene
- **N's Zekrom** (id 906, Dragon, 130HP, retreat 2): Shred (70dmg/3en, 23/en); Rampaging Thunder (250dmg/4en, 62/en)
- **Turtonator** (id 196, Dragon, 120HP, retreat 3): Fully Singe (0dmg/1en, 0/en); Steaming Stomp (100dmg/3en, 33/en)
- **Druddigon** (id 625, Dragon, 120HP, retreat 2): Shred (40dmg/1en, 40/en); Ambush (90dmg/3en, 30/en)
- **Rayquaza** (id 905, Dragon, 120HP, retreat 1): Breakthrough Assault (20dmg/2en, 10/en); Dragon Claw (130dmg/3en, 43/en)

## Stage 2 lines (Basic -> Stage 1 -> Stage 2), by final HP

Full 3-card evolution lines topping out at Stage 2, for archetypes willing to pay the evolution-sequencing tax in exchange for a big payoff. Flagged where `Rare Candy` (id 1079, a real-card-name Basic-straight-to-Stage-2 skip) applies (any Stage 2 with a Basic that has no listed Stage 1 requirement text issue -- Rare Candy works generically per its own text).

- **Bulbasaur -> Ivysaur -> Mega Venusaur ex**
    - **Bulbasaur** (id 650, Grass, 80HP, retreat 2): Bind Down (10dmg/1en, 10/en)
    - **Ivysaur** (id 651, Grass, 110HP, retreat 3): Razor Leaf (60dmg/2en, 30/en)
    - **Mega Venusaur ex** [megaEx] (id 652, Grass, 380HP, retreat 4): Jungle Dump (240dmg/4en, 60/en) -- Ability * Solar Transfer*: As often as you like during your turn, you may use this Ability. Move a Basic {G} Energy from 1 of your Pokémon to another of your Pokémon.
- **Tepig -> Pignite -> Mega Emboar ex**
    - **Tepig** (id 930, Fire, 80HP, retreat 2): Steady Firebreathing (20dmg/1en, 20/en)
    - **Pignite** (id 931, Fire, 110HP, retreat 3): Super Singe (70dmg/3en, 23/en)
    - **Mega Emboar ex** [megaEx] (id 932, Fire, 380HP, retreat 4): Crimson Blast (320dmg/3en, 107/en)
- **Dratini -> Dragonair -> Mega Dragonite ex**
    - **Dratini** (id 902, Dragon, 80HP, retreat 2): Headbutt (30dmg/2en, 15/en)
    - **Dragonair** (id 903, Dragon, 100HP, retreat 2): Tail Snap (60dmg/2en, 30/en) -- Ability * Evolutionary Guidance*: Once during your turn, if this Pokémon has any Energy attached, you may use this Ability. Search your deck for an Evolution Pokémon, reveal 
    - **Mega Dragonite ex** [megaEx] (id 904, Dragon, 370HP, retreat 2): Ryuno Glide (330dmg/3en, 110/en) -- Ability * Sky Transport*: Once during your turn, you may use this Ability. Switch your Active Pokémon with 1 of your Benched Pokémon.
- **Totodile -> Croconaw -> Mega Feraligatr ex**
    - **Totodile** (id 937, Water, 80HP, retreat 1): Slight Intrusion (40dmg/2en, 20/en)
    - **Croconaw** (id 938, Water, 100HP, retreat 2): Crunch (50dmg/2en, 25/en)
    - **Mega Feraligatr ex** [megaEx] (id 939, Water, 370HP, retreat 3): Mortal Crunch (200dmg/3en, 67/en)
- **Ralts -> Kirlia -> Mega Gardevoir ex**
    - **Ralts** (id 745, Psychic, 70HP, retreat 1): Collect (0dmg/1en, 0/en); Headbutt (10dmg/1en, 10/en)
    - **Kirlia** (id 746, Psychic, 100HP, retreat 1): Call Sign (0dmg/1en, 0/en); Psyshot (30dmg/1en, 30/en)
    - **Mega Gardevoir ex** [megaEx] (id 747, Psychic, 360HP, retreat 2): Overflowing Wishes (0dmg/1en, 0/en); Mega Symphonia (0dmg/1en, 0/en)
- **Charmander -> Charmeleon -> Mega Charizard X ex**
    - **Charmander** (id 926, Fire, 80HP, retreat 1): Fire Claws (30dmg/2en, 15/en)
    - **Charmeleon** (id 927, Fire, 100HP, retreat 1): Heat Blast (50dmg/2en, 25/en)
    - **Mega Charizard X ex** [megaEx] (id 790, Fire, 360HP, retreat 2): Inferno X (0dmg/2en, 0/en)
- **Chikorita -> Bayleef -> Mega Meganium ex**
    - **Chikorita** (id 917, Grass, 70HP, retreat 1): Growl (0dmg/1en, 0/en); Seed Bomb (30dmg/2en, 15/en)
    - **Bayleef** (id 918, Grass, 100HP, retreat 2): Leaf Step (60dmg/2en, 30/en)
    - **Mega Meganium ex** [megaEx] (id 919, Grass, 360HP, retreat 2): Giant Bouquet (70dmg/3en, 23/en)
- **Charmander -> Charmeleon -> Mega Charizard Y ex**
    - **Charmander** (id 926, Fire, 80HP, retreat 1): Fire Claws (30dmg/2en, 15/en)
    - **Charmeleon** (id 927, Fire, 100HP, retreat 1): Heat Blast (50dmg/2en, 25/en)
    - **Mega Charizard Y ex** [megaEx] (id 928, Fire, 360HP, retreat 1): Explosion Y (0dmg/3en, 0/en)
- **Gastly -> Haunter -> Mega Gengar ex**
    - **Gastly** (id 1057, Darkness, 70HP, retreat 1): Surprise Attack (30dmg/1en, 30/en)
    - **Haunter** (id 1058, Darkness, 100HP, retreat 1): Haunt (0dmg/1en, 0/en)
    - **Mega Gengar ex** [megaEx] (id 772, Darkness, 350HP, retreat 2): Void Gale (230dmg/2en, 115/en) -- Ability * Shadowy Concealment*: If 1 of your {D} Pokémon is Knocked Out by damage from an attack from your opponent’s Pokémon {ex}, that player takes 1 fewer Prize card. Th
- **Tynamo -> Eelektrik -> Mega Eelektross ex**
    - **Tynamo** (id 511, Lightning, 40HP, retreat 0): Hold Still (0dmg/1en, 0/en)
    - **Eelektrik** (id 512, Lightning, 90HP, retreat 2): Electric Ball (50dmg/3en, 17/en) -- Ability * Dynamotor*: Once during your turn, you may attach a Basic {L} Energy card from your discard pile to 1 of your Benched Pokémon.
    - **Mega Eelektross ex** [megaEx] (id 868, Lightning, 350HP, retreat 2): Split Bomb (0dmg/2en, 0/en); Disaster Shock (190dmg/3en, 63/en)
- **Slakoth -> Vigoroth -> Slaking ex**
    - **Slakoth** (id 998, Colorless, 60HP, retreat 2): Take It Easy (0dmg/1en, 0/en)
    - **Vigoroth** (id 999, Colorless, 90HP, retreat 2): Slashing Claw (50dmg/2en, 25/en)
    - **Slaking ex** [ex] (id 232, Colorless, 340HP, retreat 4): Great Swing (280dmg/2en, 140/en) -- Ability *Born to Slack*: If your opponent has no Pokémon {ex} or Pokémon {V} in play, this Pokémon can’t attack.
- **Swinub -> Piloswine -> Mamoswine ex**
    - **Swinub** (id 800, Water, 70HP, retreat 2): Stampede (10dmg/1en, 10/en); Icy Snow (20dmg/2en, 10/en)
    - **Piloswine** (id 801, Water, 100HP, retreat 3): Rising Lunge (30dmg/2en, 15/en); Frost Smash (70dmg/3en, 23/en)
    - **Mamoswine ex** [ex] (id 283, Fighting, 340HP, retreat 4): Rumbling March (180dmg/2en, 90/en) -- Ability *Mammoth Hauler*: Once during your turn, you may search your deck for a Pokémon, reveal it, and put it into your hand. Then, shuffle your deck.
- **Steven's Beldum -> Steven's Metang -> Steven's Metagross ex**
    - **Steven's Beldum** (id 639, Metal, 70HP, retreat 1): Ram (30dmg/2en, 15/en)
    - **Steven's Metang** (id 640, Metal, 100HP, retreat 2): Metal Slash (70dmg/2en, 35/en)
    - **Steven's Metagross ex** [ex] (id 641, Metal, 340HP, retreat 3): Metal Stomp (200dmg/3en, 67/en) -- Ability * X-Boot*: Once during your turn, you may search your deck for a Basic {P} Energy card, a Basic {M} Energy card, or 1 of each and attach them to your {
- **Applin -> Dipplin -> Hydrapple ex**
    - **Applin** (id 346, Grass, 40HP, retreat 1): Mini Drain (10dmg/1en, 10/en)
    - **Dipplin** (id 921, Grass, 90HP, retreat 3): Coated Attack (20dmg/1en, 20/en)
    - **Hydrapple ex** [ex] (id 150, Grass, 330HP, retreat 3): Syrup Storm (30dmg/2en, 15/en) -- Ability *Ripening Charge*: Once during your turn, you may attach a Basic {G} Energy card from your hand to 1 of your Pokémon. If you attached Energy to a Pokémon in th
- **Deino -> Zweilous -> Hydreigon ex**
    - **Deino** (id 616, Darkness, 80HP, retreat 2): Body Slam (20dmg/2en, 10/en); Darkness Fang (50dmg/3en, 17/en)
    - **Zweilous** (id 617, Darkness, 110HP, retreat 3): Double Hit (0dmg/2en, 0/en); Pitch-Black Fangs (100dmg/4en, 25/en)
    - **Hydreigon ex** [ex,tera] (id 229, Darkness, 330HP, retreat 3): Crashing Headbutt (200dmg/2en, 100/en); Obsidian (130dmg/4en, 32/en)
- **Cynthia's Gible -> Cynthia's Gabite -> Cynthia's Garchomp ex**
    - **Cynthia's Gible** (id 379, Fighting, 70HP, retreat 1): Rock Hurl (20dmg/1en, 20/en)
    - **Cynthia's Gabite** (id 380, Fighting, 100HP, retreat 1): Dragonslice (40dmg/1en, 40/en) -- Ability * Champion’s Call*: Once during your turn, you may search your deck for a Cynthia’s Pokémon, reveal it, and put it into your hand. Then, shuffle your deck.
    - **Cynthia's Garchomp ex** [ex] (id 381, Fighting, 330HP, retreat 0): Corkscrew Dive (100dmg/1en, 100/en); Draconic Buster (260dmg/2en, 130/en)
- **Team Rocket's Nidoran♂ -> Team Rocket's Nidorino -> Team Rocket's Nidoking ex**
    - **Team Rocket's Nidoran♂** (id 453, Darkness, 70HP, retreat 1): Pierce (10dmg/1en, 10/en); Hammer In (30dmg/2en, 15/en)
    - **Team Rocket's Nidorino** (id 454, Darkness, 100HP, retreat 2): Hammer In (30dmg/2en, 15/en); Horn Rend (60dmg/3en, 20/en)
    - **Team Rocket's Nidoking ex** [ex] (id 455, Darkness, 330HP, retreat 3): Tainted Horn (100dmg/3en, 33/en); Kingly Impact (240dmg/4en, 60/en)
- **Deino -> Zweilous -> Hydreigon ex**
    - **Deino** (id 616, Darkness, 80HP, retreat 2): Body Slam (20dmg/2en, 10/en); Darkness Fang (50dmg/3en, 17/en)
    - **Zweilous** (id 617, Darkness, 110HP, retreat 3): Double Hit (0dmg/2en, 0/en); Pitch-Black Fangs (100dmg/4en, 25/en)
    - **Hydreigon ex** [ex] (id 618, Darkness, 330HP, retreat 3): Dark Bite (200dmg/5en, 40/en) -- Ability * Greedy Eater*: If your opponent’s Basic Pokémon is Knocked Out by damage from an attack used by this Pokémon, take 1 more Prize card.
- **Litten -> Torracat -> Incineroar ex**
    - **Litten** (id 77, Fire, 70HP, retreat 2): Fake Out (10dmg/1en, 10/en)
    - **Torracat** (id 78, Fire, 100HP, retreat 2): Bite (30dmg/1en, 30/en); Flare Strike (80dmg/3en, 27/en)
    - **Incineroar ex** [ex] (id 79, Fire, 320HP, retreat 2): Blaze Blast (240dmg/5en, 48/en) -- Ability *Hustle Play*: Attacks used by this Pokémon cost {C} less for each of your opponent’s Benched Pokémon.
- **Dreepy -> Drakloak -> Dragapult ex**
    - **Dreepy** (id 119, Dragon, 70HP, retreat 1): Petty Grudge (10dmg/1en, 10/en); Bite (40dmg/2en, 20/en)
    - **Drakloak** (id 120, Dragon, 90HP, retreat 1): Dragon Headbutt (70dmg/2en, 35/en) -- Ability *Recon Directive*: Once during your turn, you may look at the top 2 cards of your deck and put 1 of them into your hand. Put the other card on the bottom of yo
    - **Dragapult ex** [ex,tera] (id 121, Dragon, 320HP, retreat 1): Jet Headbutt (70dmg/1en, 70/en); Phantom Dive (200dmg/2en, 100/en)

## `ex` / `megaEx` / `tera` Basic Pokemon (no evolution needed, but 2-prize tax if KO'd)

- **Mega Zygarde ex** [megaEx] (id 1056, Fighting, 310HP, retreat 2): Gaia Wave (200dmg/3en, 67/en); Nullifying Zero (0dmg/5en, 0/en)
- **Mega Kangaskhan ex** [megaEx] (id 756, Colorless, 300HP, retreat 3): Rapid-Fire Combo (200dmg/3en, 67/en) -- Ability * Run Errand*: Once during your turn, if this Pokémon is in the Active Spot, you may use this Ability. Draw 2 cards. You can’t use more than 1 Run Errand A
- **Team Rocket's Mewtwo ex** [ex] (id 431, Psychic, 280HP, retreat 3): Erasure Ball (160dmg/3en, 53/en) -- Ability * Power Saver*: This Pokémon can’t attack unless you have 4 or more Team Rocket’s Pokémon in play.
- **Mega Absol ex** [megaEx] (id 687, Darkness, 280HP, retreat 2): Terminal Period (0dmg/2en, 0/en); Claw of Darkness (200dmg/3en, 67/en)
- **Mega Latias ex** [megaEx] (id 754, Dragon, 280HP, retreat 1): Strafe (40dmg/1en, 40/en); Illusory Impulse (300dmg/3en, 100/en)
- **Mega Heracross ex** [megaEx] (id 781, Grass, 280HP, retreat 2): Juggernaut Horn (100dmg/2en, 50/en); Mountain Ramming (170dmg/3en, 57/en)
- **Mega Mawile ex** [megaEx] (id 695, Metal, 270HP, retreat 2): Gobble Down (0dmg/2en, 0/en); Huge Bite (260dmg/3en, 87/en)
- **Mega Diancie ex** [megaEx] (id 766, Psychic, 270HP, retreat 1): Garland Ray (0dmg/2en, 0/en) -- Ability * Diamond Coat*: This Pokémon takes 30 less damage from attacks (after applying Weakness and Resistance).
- **Mega Audino ex** [megaEx] (id 1006, Colorless, 270HP, retreat 1): Kaleidowaltz (0dmg/1en, 0/en); Ear Force (20dmg/3en, 7/en)
- **Bloodmoon Ursaluna ex** [ex] (id 44, Colorless, 260HP, retreat 3): Blood Moon (240dmg/5en, 48/en) -- Ability *Seasoned Skill*: Blood Moon used by this Pokémon costs {C} less for each Prize card your opponent has taken.
- **Dondozo ex** [ex] (id 369, Water, 260HP, retreat 4): Avenging Billow (30dmg/2en, 15/en); Dynamic Dive (120dmg/4en, 30/en)
- **Mega Skarmory ex** [megaEx] (id 1064, Metal, 260HP, retreat 0): Sonic Ripper (0dmg/3en, 0/en)
- **Okidogi ex** [ex] (id 138, Darkness, 250HP, retreat 3): Poisonous Musculature (0dmg/1en, 0/en); Chain-Crazed (130dmg/3en, 43/en)
- **Mega Hawlucha ex** [megaEx] (id 886, Fighting, 250HP, retreat 1): Somersault Dive (120dmg/3en, 40/en) -- Ability * Tenacious Body*: If this Pokémon would be Knocked Out by damage from an attack, flip a coin. If heads, this Pokémon is not Knocked Out, and its remaining HP 
- **Raging Bolt ex** [ex] (id 63, Dragon, 240HP, retreat 3): Burst Roar (0dmg/1en, 0/en); Bellowing Thunder (0dmg/2en, 0/en)
- **Team Rocket's Kangaskhan ex** [ex] (id 24, Colorless, 230HP, retreat 2): Comet Punch (0dmg/2en, 0/en); Wicked Impact (120dmg/3en, 40/en)
- **Iron Thorns ex** [ex] (id 37, Lightning, 230HP, retreat 4): Volt Cyclone (140dmg/3en, 47/en) -- Ability *Initialization*: As long as this Pokémon is in the Active Spot, Pokémon with a Rule Box in play (both yours and your opponent’s) have no Abilities, except fo
- **Gouging Fire ex** [ex] (id 46, Fire, 230HP, retreat 2): Heat Blast (60dmg/2en, 30/en); Blaze Blitz (260dmg/3en, 87/en)
- **Terapagos ex** [ex,tera] (id 176, Colorless, 230HP, retreat 2): Unified Beatdown (0dmg/2en, 0/en); Crown Opal (180dmg/3en, 60/en)
- **Black Kyurem ex** [ex] (id 179, Water, 230HP, retreat 3): Ice Age (90dmg/3en, 30/en); Black Frost (250dmg/4en, 62/en)

## Basic/Stage-1 Pokemon with a notable Ability (search/draw/setup)

- **Mega Kangaskhan ex** [megaEx] (id 756, Colorless, 300HP, retreat 3): Rapid-Fire Combo (200dmg/3en, 67/en) -- Ability * Run Errand*: Once during your turn, if this Pokémon is in the Active Spot, you may use this Ability. Draw 2 cards. You can’t use more than 1 Run Errand A
- **N’s Zoroark ex** [ex] (id 293, Darkness, 280HP, retreat 2): Night Joker (0dmg/2en, 0/en) -- Ability *Trade*: You must discard a card from your hand in order to use this Ability. Once during your turn, you may draw 2 cards.
- **Yanmega ex** [ex] (id 340, Grass, 280HP, retreat 1): Jet Cyclone (210dmg/4en, 52/en) -- Ability * Buzzing Boost*: Once during your turn, when this Pokémon moves from your Bench to the Active Spot, you may search your deck for up to 3 Basic {G} Energy car
- **Genesect ex** [ex] (id 547, Metal, 220HP, retreat 2): Protect Charge (150dmg/3en, 50/en) -- Ability * Metallic Signal*: Once during your turn, you may search your deck for up to 2 Evolution {M} Pokémon, reveal them, and put them into your hand. Then, shuffle y
- **Teal Mask Ogerpon ex** [ex,tera] (id 96, Grass, 210HP, retreat 1): Myriad Leaf Shower (30dmg/3en, 10/en) -- Ability *Teal Dance*: Once during your turn, you may attach a Basic {G} Energy card from your hand to this Pokémon. If you attached Energy to a Pokémon in this wa
- **Fezandipiti ex** [ex] (id 140, Darkness, 210HP, retreat 1): Cruel Arrow (0dmg/3en, 0/en) -- Ability *Flip the Script*: Once during your turn, if any of your Pokémon were Knocked Out during your opponent’s last turn, you may draw 3 cards. You can’t use more th
- **Meowth ex** [ex] (id 1071, Colorless, 170HP, retreat 1): Tuck Tail (60dmg/3en, 20/en) -- Ability * Last-Ditch Catch*: Once during your turn, when you play this Pokémon from your hand onto your Bench, you may use this Ability. Search your deck for a Supporter
- **Dudunsparce** (id 66, Colorless, 140HP, retreat 3): Land Crush (90dmg/3en, 30/en) -- Ability *Run Away Draw*: Once during your turn, you may draw 3 cards. If you drew any cards in this way, shuffle this Pokémon and all attached cards into your deck.
- **Toxtricity** (id 834, Darkness, 140HP, retreat 2): Gentle Slap (100dmg/3en, 33/en) -- Ability * Sinister Surge*: Once during your turn, you may use this Ability. Search your deck for a Basic {D} Energy card and attach it to 1 of your Benched {D} Pokémon
- **Sawsbuck** (id 72, Grass, 130HP, retreat 2): Superpowered Horns (110dmg/3en, 37/en) -- Ability * Changing Seasons*: Once during your turn, you may search your deck for a Stadium card, reveal it, and put it into your hand. Then, shuffle your deck.
- **Iono’s Kilowattrel** (id 271, Lightning, 120HP, retreat 1): Mach Bolt (70dmg/3en, 23/en) -- Ability *Flashing Draw*: You must discard a Basic {L} Energy from this Pokémon in order to use this Ability. Once during your turn, you may draw cards until you have
- **Grumpig** (id 750, Psychic, 120HP, retreat 2): Psychic Sphere (60dmg/3en, 20/en) -- Ability * Energized Steps*: Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may use this Ability. Look at the top 4 ca
- **Heliolisk** (id 871, Lightning, 120HP, retreat 1): Powerful Bolt (0dmg/3en, 0/en) -- Ability * Frilled Generator*: Once during your turn, if you played Canari from your hand this turn, you may use this Ability. Search your deck for up to 2 Basic {L} Energ
- **Aromatisse** (id 1045, Psychic, 120HP, retreat 1): Draining Kiss (50dmg/2en, 25/en) -- Ability * Scent Collection*: Once during your turn, you may use this Ability. Search your deck for up to 2 Basic {P} Energy cards, reveal them, and put them into your ha
- **Rapidash** (id 351, Fire, 110HP, retreat 1): Fire Mane (60dmg/2en, 30/en) -- Ability * Hurried Gait*: Once during your turn, you may draw a card.
- **Lunatone** (id 675, Fighting, 110HP, retreat 1): Power Gem (50dmg/2en, 25/en) -- Ability * Lunar Cycle*: Once during your turn, if you have Solrock in play, you may discard a Basic {F} Energy card from your hand in order to use this Ability. Dra
- **Frosmoth** (id 866, Water, 110HP, retreat 2): Cold Cyclone (90dmg/2en, 45/en) -- Ability * Alluring Wings*: Once during your turn, if this Pokémon is in the Active Spot, you may use this Ability. Each player draws a card.
- **Metang** (id 86, Metal, 100HP, retreat 2): Beam (60dmg/3en, 20/en) -- Ability *Metal Maker*: Once during your turn, you may look at the top 4 cards of your deck and attach any number of Basic {M} Energy cards you find there to your P
- **Thwackey** (id 90, Grass, 100HP, retreat 2): Beat (50dmg/2en, 25/en) -- Ability *Boom Boom Groove*: Once during your turn, if your Active Pokémon has the Festival Lead Ability, you may search your deck for a card and put it into your hand. 
- **Palafin** (id 106, Water, 100HP, retreat 1): Wave Splash (30dmg/2en, 15/en) -- Ability *Zero to Hero*: Once during your turn, when this Pokémon moves from the Active Spot to the Bench, you may search your deck for a Palafin {ex} and switch it 
- **Noctowl** (id 173, Colorless, 100HP, retreat 1): Speed Wing (60dmg/2en, 30/en) -- Ability *Jewel Seeker*: Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, if you have any Tera Pokémon in play, you may 
- **Ethan's Quilava** (id 353, Fire, 100HP, retreat 1): Combustion (40dmg/1en, 40/en) -- Ability * Bonded by the Journey*: Once during your turn, you may search your deck for an Ethan’s Adventure card, reveal it, and put it into your hand. Then, shuffle your deck
- **Cynthia's Gabite** (id 380, Fighting, 100HP, retreat 1): Dragonslice (40dmg/1en, 40/en) -- Ability * Champion’s Call*: Once during your turn, you may search your deck for a Cynthia’s Pokémon, reveal it, and put it into your hand. Then, shuffle your deck.
- **Dragonair** (id 903, Dragon, 100HP, retreat 2): Tail Snap (60dmg/2en, 30/en) -- Ability * Evolutionary Guidance*: Once during your turn, if this Pokémon has any Energy attached, you may use this Ability. Search your deck for an Evolution Pokémon, reveal 
- **Drakloak** (id 120, Dragon, 90HP, retreat 1): Dragon Headbutt (70dmg/2en, 35/en) -- Ability *Recon Directive*: Once during your turn, you may look at the top 2 cards of your deck and put 1 of them into your hand. Put the other card on the bottom of yo

## Trainer catalog (by function)

### Draw supporters (19)

- **Billy & O'Nare** (id 1181): Draw 2 cards. Then, if you have 10 or more cards in your hand, draw 2 more cards.
- **Morty’s Conviction** (id 1187): You can use this card only if you discard another card from your hand. Draw a card for each of your opponent’s Benched Pokémon.
- **Carmine** (id 1192): If you go first, you may use this card during your first turn. Discard your hand and draw 5 cards.
- **Lacey** (id 1199): Shuffle your hand into your deck. Then, draw 4 cards. If your opponent has 3 or fewer Prize cards remaining, draw 8 cards instead.
- **Kofu** (id 1200): Put 2 cards from your hand on the bottom of your deck in any order. If you put 2 cards on the bottom of your deck in this way, draw 4 cards. (If you can’t put 2
- **Surfer** (id 1203): Switch your Active Pokémon with 1 of your Benched Pokémon. If you do, draw cards until you have 5 cards in your hand.
- **Amarys** (id 1207): Draw 4 cards. At the end of this turn, if you have 5 or more cards in your hand, discard your hand.
- **Iris’s Fighting Spirit** (id 1208): You can use this card only if you discard another card from your hand. Draw cards until you have 6 cards in your hand.
- **Judge** (id 1213): Each player shuffles their hand into their deck and draws 4 cards.  **[functions like N / Judge (both players shuffle+draw)]**
- **Emcee's Hype** (id 1214): Draw 2 cards. If your opponent has 3 or fewer Prize cards remaining, draw 2 more cards.
- **Team Rocket's Ariana** (id 1216): Draw cards until you have 5 cards in your hand. If all of your Pokémon in play are Team Rocket’s Pokémon, draw cards until you have 8 cards in your hand instead
- **Team Rocket's Archer** (id 1217): You can use this card only if any of your Team Rocket’s Pokémon were Knocked Out during your opponent’s last turn. Each player shuffles their hand into their de
- **Harlequin** (id 1223): Each player shuffles their hand into their deck. Then, flip a coin. If heads, you draw 5 cards, and your opponent draws 3 cards. If tails, you draw 3 cards, and
- **Cheren** (id 1224): Draw 3 cards.
- **Lt. Surge's Bargain** (id 1226): Ask your opponent if each player may take a Prize card. If yes, each player takes a Prize card. If no, you draw 4 cards.
- **Lillie's Determination** (id 1227): Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead.
- **Urbain** (id 1236): Draw 3 cards.
- **Lucian** (id 1237): Each player shuffles their hand and puts it on the bottom of their deck. If either player put any cards on the bottom of their deck in this way, each player fli
- **Naveen** (id 1239): Draw cards until you have 5 cards in your hand. Before drawing cards, you may discard any number of cards from your hand. (If you can’t draw any cards in this w

### Pokemon search (Items/Supporters) (17)

- **Hyper Aroma** (id 1082): Search your deck for up to 3 Stage 1 Pokémon, reveal them, and put them into your hand. Then, shuffle your deck.
- **Love Ball** (id 1083): Search your deck for a Pokémon with the same name as 1 of your opponent’s Pokémon in play, reveal it, and put it into your hand. Then, shuffle your deck.
- **Buddy-Buddy Poffin** (id 1086): Search your deck for up to 2 Basic Pokémon with 70 HP or less and put them onto your Bench. Then, shuffle your deck.
- **Treasure Tracker** (id 1111): Search your deck for up to 5 Pokémon Tool cards, reveal them, and put them into your hand. Then, shuffle your deck.
- **Hop’s Bag** (id 1115): Search your deck for up to 2 Basic Hop’s Pokémon and put them onto your Bench. Then, shuffle your deck.
- **Ultra Ball** (id 1121): You can use this card only if you discard 2 other cards from your hand. Search your deck for a Pokémon, reveal it, and put it into your hand. Then, shuffle your  **[real-name analog of Ultra Ball (generic Pokemon search)]**
- **Master Ball** (id 1125): Search your deck for a Pokémon, reveal it, and put it into your hand. Then, shuffle your deck.
- **Poké Pad** (id 1152): Search your deck for a Pokémon that doesn’t have a Rule Box, reveal it, and put it into your hand. Then, shuffle your deck. (Pokémon {ex}, Pokémon {V}, etc. hav
- **Amulet of Hope** (id 1169): If the Pokémon this card is attached to is Knocked Out by damage from an attack from your opponent’s Pokémon, search your deck for up to 3 cards and put them in
- **Perrin** (id 1183): Reveal up to 2 Pokémon in your hand and put them into your deck. If you do, search your deck for up to that many Pokémon, reveal them, and put them into your ha
- **Crispin** (id 1198): Search your deck for up to 2 Basic Energy cards of different types, reveal them, and put 1 of them into your hand. Attach the other to 1 of your Pokémon. Then, 
- **Cyrano** (id 1205): Search your deck for up to 3 Pokémon {ex}, reveal them, and put them into your hand. Then, shuffle your deck.
- **Larry’s Skill** (id 1206): Discard your hand and search your deck for a Pokémon, a Supporter card, and a Basic Energy card, reveal them, and put them into your hand. Then, shuffle your de
- **Brock’s Scouting** (id 1210): Search your deck for up to 2 Basic Pokémon or 1 Evolution Pokémon, reveal them, and put them into your hand. Then, shuffle your deck.
- **Ethan's Adventure** (id 1215): Search your deck for up to 3 in any combination of Ethan’s Pokémon and Basic {R} Energy cards, reveal them, and put them into your hand. Then, shuffle your deck
- **Team Rocket's Proton** (id 1220): If you go first, you may use this card during your first turn. Search your deck for up to 3 Basic Team Rocket’s Pokémon, reveal them, and put them into your han
- **Canari** (id 1233): You can use this card only if you discard another card from your hand. Search your deck for up to 4 {L} Pokémon, reveal them, and put them into your hand. Then,

### Trainer search (5)

- **Secret Box** (id 1092): You can use this card only if you discard 3 other cards from your hand. Search your deck for an Item card, a Pokémon Tool card, a Supporter card, and a Stadium 
- **Call Bell** (id 1101): You can use this card only if you go second, and only during your first turn. Search your deck for a Supporter card, reveal it, and put it into your hand. Then,
- **Team Rocket's Great Ball** (id 1132): Search your deck for a Trainer card, reveal it, and put it into your hand. Then, shuffle your deck.
- **Team Rocket's Transceiver** (id 1134): Search your deck for a Supporter card that has “Team Rocket” in its name, reveal it, and put it into your hand. Then, shuffle your deck.
- **Team Rocket's Petrel** (id 1219): Search your deck for a Trainer card, reveal it, and put it into your hand. Then, shuffle your deck.

### Switch / gust effects (11)

- **Prime Catcher** (id 1088): Switch in 1 of your opponent’s Benched Pokémon to the Active Spot. If you do, switch your Active Pokémon with 1 of your Benched Pokémon.
- **Ogre’s Mask** (id 1090): Choose a Pokémon {ex} in your discard pile that has “Ogerpon” in its name, and switch it with 1 of your Pokémon {ex} in play that has “Ogerpon” in its name. Any
- **Scramble Switch** (id 1107): Switch your Active Pokémon with 1 of your Benched Pokémon. If you do, you may move any amount of Energy from the Pokémon you moved to your Bench to the new Acti
- **Switch** (id 1123): Switch your Active Pokémon with 1 of your Benched Pokémon.  **[real-name analog of Switch]**
- **Pokémon Catcher** (id 1124): Flip a coin. If heads, switch in 1 of your opponent’s Benched Pokémon to the Active Spot.
- **Team Rocket's Bother-Bot** (id 1131): Turn 1 of your opponent’s face-down Prize cards face up and choose a random card from your opponent’s hand. Your opponent reveals that card. You may have your o
- **Repel** (id 1143): Switch out your opponent’s Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)
- **Boss’s Orders** (id 1182): Switch in 1 of your opponent’s Benched Pokémon to the Active Spot.  **[real-name analog of Boss's Orders (gust effect)]**
- **Kieran** (id 1191): Choose 1: • Switch your Active Pokémon with 1 of your Benched Pokémon. • During this turn, attacks used by your Pokémon do 30 more damage to your opponent’s Act
- **Lisia’s Appeal** (id 1204): Switch in 1 of your opponent’s Benched Basic Pokémon to the Active Spot. If you do, the new Active Pokémon is now Confused.
- **Team Rocket's Giovanni** (id 1218): Switch your Active Team Rocket’s Pokémon with 1 of your Benched Team Rocket’s Pokémon. If you do, switch in 1 of your opponent’s Benched Pokémon to the Active S

### Healing (13)

- **Poké Vital A** (id 1096): Heal 150 damage from 1 of your Pokémon. This card can’t be put into your hand or deck from the discard pile.
- **Dragon Elixir** (id 1105): Heal 60 damage from your Active {N} Pokémon.
- **Super Potion** (id 1112): Heal 60 damage from 1 of your Pokémon. If you healed any damage in this way, discard an Energy from that Pokémon.  **[real-name analog of Super Potion]**
- **Potion** (id 1117): Heal 30 damage from 1 of your Pokémon.  **[real-name analog of Potion]**
- **Arven's Sandwich** (id 1130): Heal 30 damage from your Active Pokémon. If that Pokémon is an Arven’s Pokémon, heal 100 damage from it instead.
- **Jumbo Ice Cream** (id 1147): Heal 80 damage from your Active Pokémon that has 3 or more Energy attached.
- **Lumiose Galette** (id 1153): Heal 20 damage and remove a Special Condition from your Active Pokémon.
- **Bianca’s Devotion** (id 1190): Heal all damage from 1 of your Pokémon that has 30 HP or less remaining.
- **Cook** (id 1212): Heal 70 damage from your Active Pokémon.
- **Fennel** (id 1222): Heal 40 damage from each of your Pokémon.
- **Wally's Compassion** (id 1229): Heal all damage from 1 of your Mega Evolution Pokémon {ex}. If you healed any damage in this way, put all Energy attached to that Pokémon into your hand.
- **Jacinthe** (id 1241): Heal 150 damage from 1 of your {P} Pokémon.
- **Community Center** (id 1242): Once during each player’s turn, if they played a Supporter card from their hand this turn, they may heal 10 damage from each of their Pokémon.

### Disruption (11)

- **Enhanced Hammer** (id 1081): Discard a Special Energy from 1 of your opponent’s Pokémon.
- **Hand Trimmer** (id 1087): Each player discards cards from their hand until they have 5 cards in their hand. Your opponent discards first. (If a player has 5 or fewer cards in their hand,
- **Crushing Hammer** (id 1120): Flip a coin. If heads, discard an Energy from 1 of your opponent’s Pokémon.
- **Tool Scrapper** (id 1137): Choose up to 2 Pokémon Tools attached to Pokémon (yours or your opponent’s) and discard them.
- **Blowtorch** (id 1148): You can use this card only if you discard a Basic {R} Energy card from your hand. Discard a Pokémon Tool or Special Energy card from 1 of your opponent’s Pokémo
- **Payapa Berry** (id 1164): If the Pokémon this card is attached to is damaged by an attack from your opponent’s {P} Pokémon, it takes 60 less damage (after applying Weakness and Resistanc
- **Haban Berry** (id 1170): If the Pokémon this card is attached to is damaged by an attack from your opponent’s {N} Pokémon, it takes 60 less damage (after applying Weakness and Resistanc
- **Eri** (id 1186): Your opponent reveals their hand, and you discard up to 2 Item cards you find there.
- **Xerosic’s Machinations** (id 1197): Your opponent discards cards from their hand until they have 3 cards in their hand.
- **Ruffian** (id 1209): Discard a Pokémon Tool and a Special Energy from 1 of your opponent’s Pokémon.
- **Rosa's Encouragement** (id 1240): You can use this card only if you have more Prize cards remaining than your opponent. Attach up to 2 Basic Energy cards from your discard pile to 1 of your Stag

### ACE SPEC (16)

- **Unfair Stamp** (id 1080): You can use this card only if any of your Pokémon were Knocked Out during your opponent’s last turn. Each player shuffles their hand into their deck. Then, you 
- **Awakening Drum** (id 1085): Draw a card for each of your Ancient Pokémon in play.
- **Reboot Pod** (id 1089): Attach a Basic Energy card from your discard pile to each of your Future Pokémon.
- **Scoop Up Cyclone** (id 1093): Put 1 of your Pokémon and all attached cards into your hand.
- **Dangerous Laser** (id 1095): Your opponent’s Active Pokémon is now Burned and Confused.
- **Energy Search Pro** (id 1100): Search your deck for any number of Basic Energy cards of different types, reveal them, and put them into your hand. Then, shuffle your deck.
- **Megaton Blower** (id 1104): Discard all Pokémon Tools and Special Energy from all of your opponent’s Pokémon, and discard a Stadium in play.
- **Miracle Headset** (id 1109): Put up to 2 Supporter cards from your discard pile into your hand.
- **Max Rod** (id 1110): Put up to 5 in any combination of Pokémon and Basic Energy cards from your discard pile into your hand.
- **Precious Trolley** (id 1126): Search your deck for any number of Basic Pokémon and put them onto your Bench. Then, shuffle your deck.
- **Brilliant Blender** (id 1128): Search your deck for up to 5 cards and discard them. Then, shuffle your deck.
- **Survival Brace** (id 1155): If the Pokémon this card is attached to has full HP and would be Knocked Out by damage from an attack from your opponent’s Pokémon, it is not Knocked Out, and i
- **Maximum Belt** (id 1158): Attacks used by the Pokémon this card is attached to do 50 more damage to your opponent’s Active Pokémon {ex} (before applying Weakness and Resistance).
- **Hero’s Cape** (id 1159): The Pokémon this card is attached to gets +100 HP.
- **Sparkling Crystal** (id 1165): When the Tera Pokémon this card is attached to uses an attack, that attack costs 1 Energy less. (The Energy can be of any type.)
- **Deluxe Bomb** (id 1167): If the Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent’s Pokémon (even if this Pokémon is Knocked Out), pu

### Stadiums (25)

- **Perilous Jungle** (id 1243): During Pokémon Checkup, put 2 more damage counters on each Poisoned non-{D} Pokémon (both yours and your opponent’s).
- **Full Metal Lab** (id 1244): {M} Pokémon (both yours and your opponent’s) take 30 less damage from attacks from the opponent’s Pokémon (after applying Weakness and Resistance).
- **Festival Grounds** (id 1245): Each Pokémon that has any Energy attached (both yours and your opponent’s) recovers from all Special Conditions and can’t be affected by any Special Conditions.
- **Jamming Tower** (id 1246): Pokémon Tools attached to each Pokémon (both yours and your opponent’s) have no effect.
- **Neutralization Zone** (id 1247): Prevent all damage done to Pokémon that don’t have a Rule Box (both yours and your opponent’s) by attacks from the opponent’s Pokémon {ex} and Pokémon {V}. (Pok
- **Academy at Night** (id 1248): Once during each player’s turn, that player may put a card from their hand on top of their deck.
- **Grand Tree** (id 1249): Once during each player’s turn, that player may search their deck for a Stage 1 Pokémon that evolves from 1 of their Basic Pokémon and put it onto that Pokémon 
- **Area Zero Underdepths** (id 1250): Each player who has any Tera Pokémon in play can have up to 8 Pokémon on their Bench. If a player no longer has any Tera Pokémon in play, that player discards P
- **Lively Stadium** (id 1251): Each Basic Pokémon in play (both yours and your opponent’s) gets +30 HP.
- **Gravity Mountain** (id 1252): Each Stage 2 Pokémon in play (both yours and your opponent’s) gets -30 HP.
- **N’s Castle** (id 1253): N’s Pokémon in play (both yours and your opponent’s) have no Retreat Cost.
- **Levincia** (id 1254): Once during each player’s turn, that player may put up to 2 Basic {L} Energy cards from their discard pile into their hand.
- **Postwick** (id 1255): Attacks used by Hop’s Pokémon (both yours and your opponent’s) do 30 more damage to the opponent’s Active Pokémon (before applying Weakness and Resistance).
- **Team Rocket's Watchtower** (id 1256): {C} Pokémon in play (both yours and your opponent’s) have no Abilities.
- **Team Rocket's Factory** (id 1257): Once during each player’s turn, if they played a Supporter card that has "Team Rocket" in its name from their hand this turn, they may draw 2 cards.
- **Granite Cave** (id 1258): Steven’s Pokémon (both yours and your opponent’s) take 30 less damage from attacks from the opponent’s Pokémon (after applying Weakness and Resistance).
- **Spikemuth Gym** (id 1259): Once during each player’s turn, that player may search their deck for a Marnie’s Pokémon, reveal it, and put it into their hand. Then, that player shuffles thei
- **Risky Ruins** (id 1260): Whenever any player puts a Basic non-{D} Pokémon onto their Bench during their turn, place 2 damage counters on that Pokémon.
- **Forest of Vitality** (id 1261): Each player’s {G} Pokémon can evolve into {G} Pokémon during the turn they play those Pokémon, except during their first turn.
- **Surfing Beach** (id 1262): Once during each player’s turn, that player may switch their Active {W} Pokémon with 1 of their Benched {W} Pokémon.
- **Mystery Garden** (id 1263): Once during each player’s turn, that player may discard an Energy card from their hand in order to draw cards until they have as many cards in their hand as the
- **Battle Cage** (id 1264): Prevent all damage counters from being placed on Benched Pokémon (both yours and your opponent’s) by effects of attacks and Abilities from the opponent’s Pokémo
- **Dizzying Valley** (id 1265): Confused Pokémon (both yours and your opponent’s) don’t recover from that Special Condition when they evolve or devolve.
- **Nighttime Mine** (id 1266): Attacks used by each Tera Pokémon in play (both yours and your opponent’s) cost {C} more.
- **Lumiose City** (id 1267): Once during each player’s turn, that player may search their deck for a Basic Pokémon and put it onto their Bench. Then, that player shuffles their deck. If a p

### Other (74)

- **Roto-Stick** (id 1077): Look at the top 4 cards of your deck. You may reveal any number of Supporter cards you find there and put them into your hand. Shuffle the other cards back into
- **Hole-Digging Shovel** (id 1078): Discard the top 2 cards of your deck.
- **Rare Candy** (id 1079): Choose 1 of your Basic Pokémon in play. If you have a Stage 2 card in your hand that evolves from that Pokémon, put that card onto the Basic Pokémon to evolve i  **[real-name analog of Rare Candy (Basic -> Stage 2 skip)]**
- **Boxed Order** (id 1084): Search your deck for up to 2 Item cards, reveal them, and put them into your hand. Then, shuffle your deck. Your turn ends.
- **Accompanying Flute** (id 1091): Reveal the top 5 cards of your opponent’s deck. You may choose any number of Basic Pokémon you find there and put those Pokémon onto their Bench. Your opponent 
- **Bug Catching Set** (id 1094): Look at the top 7 cards of your deck. You may reveal up to 2 in any combination of {G} Pokémon and Basic {G} Energy cards you find there and put them into your 
- **Night Stretcher** (id 1097): Put a Pokémon or a Basic Energy card from your discard pile into your hand.
- **Glass Trumpet** (id 1098): You can use this card only if you have any Tera Pokémon in play. Choose up to 2 of your Benched {C} Pokémon and attach a Basic Energy card from your discard pil
- **Antique Root Fossil** (id 1099): As long as this Pokémon is in the Active Spot, attacks used by your opponent’s Basic Pokémon cost {C} more.
- **Dusk Ball** (id 1102): Look at the bottom 7 cards of your deck. You may reveal a Pokémon you find there and put it into your hand. Shuffle the other cards back into your deck.
- **Meddling Memo** (id 1103): Your opponent counts the cards in their hand, shuffles those cards, and puts them on the bottom of their deck. If they do, they draw that many cards.
- **Deduction Kit** (id 1106): Look at the top 3 cards of your deck and put them back in any order, or shuffle them and put them on the bottom of your deck.
- **Chill Teaser Toy** (id 1108): You can use this card only if you go second, and only during your first turn. Put an Energy attached to 1 of your opponent’s Pokémon into their hand.
- **N’s PP Up** (id 1113): Attach a Basic Energy card from your discard pile to 1 of your Benched N’s Pokémon.
- **Redeemable Ticket** (id 1114): Count your Prize cards, shuffle them, and put them on the bottom of your deck. Then, take that many cards from the top of your deck and put them face down as yo
- **Energy Switch** (id 1116): Move a Basic Energy from 1 of your Pokémon to another of your Pokémon.
- **Energy Retrieval** (id 1118): Put up to 2 Basic Energy cards from your discard pile into your hand.
- **Energy Search** (id 1119): Search your deck for a Basic Energy card, reveal it, and put it into your hand. Then, shuffle your deck.
- **Pokégear 3.0** (id 1122): Look at the top 7 cards of your deck. You may reveal a Supporter card you find there and put it into your hand. Shuffle the other cards back into your deck.
- **Tera Orb** (id 1127): Search your deck for a Tera Pokémon, reveal it, and put it into your hand. Then, shuffle your deck.
- **Sacred Ash** (id 1129): Shuffle up to 5 Pokémon from your discard pile into your deck.
- **Team Rocket's Venture Bomb** (id 1133): Flip a coin. If heads, put 2 damage counters on 1 of your opponent’s Pokémon. If tails, put 2 damage counters on your Active Pokémon.
- **Energy Coin** (id 1135): Flip 2 coins. If both of them are heads, search your deck for a Basic Energy card and attach it to 1 of your Pokémon. Then, shuffle your deck.
- **Antique Cover Fossil** (id 1136): Prevent all effects of attacks used by your opponent’s Pokémon done to this Pokémon. (Damage is not an effect.)
- **Antique Plume Fossil** (id 1138): As long as this Pokémon is on your Bench, prevent all damage done to this Pokémon by attacks from your opponent’s Pokémon.
- **Energy Recycler** (id 1139): Shuffle up to 5 Basic Energy cards from your discard pile into your deck.
- **Iron Defender** (id 1140): During your opponent’s next turn, all of your {M} Pokémon take 30 less damage from attacks from your opponent’s Pokémon (after applying Weakness and Resistance)
- **Premium Power Pro** (id 1141): During this turn, attacks used by your {F} Pokémon do 30 more damage to your opponent’s Active Pokémon (before applying Weakness and Resistance).
- **Fighting Gong** (id 1142): Search your deck for a Basic {F} Energy card or a Basic {F} Pokémon, reveal it, and put it into your hand. Then, shuffle your deck.
- **Strange Timepiece** (id 1144): Devolve 1 of your evolved {P} Pokémon by putting any number of Evolution cards on it into your hand. (That Pokémon can’t evolve this turn.)
- **Mega Signal** (id 1145): Search your deck for a Mega Evolution Pokémon {ex}, reveal it, and put it into your hand. Then, shuffle your deck.
- **Wondrous Patch** (id 1146): Attach a Basic {P} Energy card from your discard pile to 1 of your Benched {P} Pokémon.
- **Energy Swatter** (id 1149): Your opponent reveals their hand, and you choose an Energy card you find there and put it on the bottom of their deck.
- **Antique Jaw Fossil** (id 1150): As long as this Pokémon is in the Active Spot, attacks used by your opponent’s Active Pokémon do 30 less damage (before applying Weakness and Resistance).
- **Antique Sail Fossil** (id 1151): Whenever your opponent plays a Supporter card from their hand, prevent all effects of that card done to this Pokémon.
- **Team Rocket’s Hypnotizer** (id 1154): If the Team Rocket’s Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent’s Pokémon (even if this Team Rocket’s
- **Lucky Helmet** (id 1156): If the Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent’s Pokémon (even if this Pokémon is Knocked Out), dr
- **Rescue Board** (id 1157): The Retreat Cost of the Pokémon this card is attached to is {C} less. If that Pokémon’s remaining HP is 30 or less, it has no Retreat Cost.
- **Heavy Baton** (id 1160): If the Pokémon this card is attached to has a Retreat Cost of exactly 4, is in the Active Spot, and is Knocked Out by damage from an attack from your opponent’s
- **Handheld Fan** (id 1161): If the Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent’s Pokémon (even if this Pokémon is Knocked Out), mo
- **Binding Mochi** (id 1162): Attacks used by the Poisoned Pokémon this card is attached to do 40 more damage to your opponent’s Active Pokémon (before applying Weakness and Resistance).
- **Powerglass** (id 1163): At the end of your turn (after your attack), if the Pokémon this card is attached to is in the Active Spot, you may attach a Basic Energy card from your discard
- **Gravity Gemstone** (id 1166): As long as the Pokémon this card is attached to is in the Active Spot, the Retreat Cost of both Active Pokémon is {C} more.
- **Counter Gain** (id 1168): If you have more Prize cards remaining than your opponent, attacks used by the Pokémon this card is attached to cost {C} less.
- **Hop’s Choice Band** (id 1171): Attacks used by the Hop’s Pokémon this card is attached to cost {C} less and do 30 more damage to your opponent’s Active Pokémon (before applying Weakness and R
- **Lillie’s Pearl** (id 1172): If the Lillie’s Pokémon this card is attached to is Knocked Out by damage from an attack from your opponent’s Pokémon, that player takes 1 fewer Prize card.
- **Cynthia's Power Weight** (id 1173): The Cynthia’s Pokémon this card is attached to gets +70 HP.
- **Air Balloon** (id 1174): The Retreat Cost of the Pokémon this card is attached to is {C}{C} less.
- **Brave Bangle** (id 1175): If the Pokémon this card is attached to doesn’t have a Rule Box, the attacks it uses do 30 more damage to your opponent’s Active Pokémon {ex} (before applying W
- **Punk Helmet** (id 1176): If the {D} Pokémon this card is attached to is in the Active Spot and is damaged by an attack from your opponent’s Pokémon (even if this Pokémon is Knocked Out)
- **Sacred Charm** (id 1177): The Pokémon this card is attached to takes 30 less damage from attacks from your opponent’s Pokémon that have an Ability (after applying Weakness and Resistance
- **Light Ball** (id 1178): Attacks used by the Pikachu {ex} this card is attached to do 50 more damage to your opponent’s Active Pokémon {ex} (before applying Weakness and Resistance).
- **Thick Scale** (id 1179): The {N} Pokémon this card is attached to takes 50 less damage from attacks from your opponent’s {G}, {R}, {W}, or {L} Pokémon (after applying Weakness and Resis
- **Core Memory** (id 1180): The Mega Zygarde {ex} this card is attached to can use the attack on this card. (You still need the necessary Energy to use this attack.)
- **Lana’s Aid** (id 1184): Put up to 3 in any combination of Pokémon that don’t have a Rule Box and Basic Energy cards from your discard pile into your hand. (Pokémon {ex}, Pokémon {V}, e
- **Explorer’s Guidance** (id 1185): Look at the top 6 cards of your deck and put 2 of them into your hand. Discard the other cards.
- **Ciphermaniac’s Codebreaking** (id 1188): Search your deck for 2 cards, shuffle your deck, then put those cards on top of it in any order.
- **Salvatore** (id 1189): Search your deck for a card that has no Abilities and evolves from 1 of your Pokémon, and put it onto that Pokémon to evolve it. Then, shuffle your deck. You ca
- **Hassel** (id 1193): You can use this card only if any of your Pokémon were Knocked Out during your opponent’s last turn. Look at the top 8 cards of your deck and put up to 3 of the
- **Colress’s Tenacity** (id 1194): Search your deck for a Stadium card and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck.
- **Janine’s Secret Art** (id 1195): Choose up to 2 of your {D} Pokémon. For each of those Pokémon, search your deck for a Basic {D} Energy card and attach it to that Pokémon. Then, shuffle your de
- **Cassiopeia** (id 1196): You can use this card only when it is the last card in your hand. Search your deck for up to 2 cards and put them into your hand. Then, shuffle your deck.
- **Briar** (id 1201): You can use this card only if your opponent has exactly 2 Prize cards remaining. During this turn, if your opponent’s Active Pokémon is Knocked Out by damage fr
- **Drayton** (id 1202): Look at the top 7 cards of your deck. You may reveal a Pokémon and a Trainer card you find there and put them into your hand. Shuffle the other cards back into 
- **Black Belt’s Training** (id 1211): During this turn, attacks used by your Pokémon do 40 more damage to your opponent’s Active Pokémon {ex} (before applying Weakness and Resistance).
- **N's Plan** (id 1221): Move up to 2 Energy from your Benched Pokémon to your Active Pokémon.
- **Hilda** (id 1225): Search your deck for an Evolution Pokémon and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck.
- **Acerola's Mischief** (id 1228): You can use this card only if your opponent has 2 or fewer Prize cards remaining. Choose 1 of your Pokémon in play. During your opponent’s next turn, prevent al
- **Grimsley's Move** (id 1230): Look at the top 7 cards of your deck and put a {D} Pokémon you find there onto your Bench. Shuffle the other cards and put them on the bottom of your deck. You 
- **Dawn** (id 1231): Search your deck for a Basic Pokémon, a Stage 1 Pokémon, and a Stage 2 Pokémon, reveal them, and put them into your hand. Then, shuffle your deck.
- **Firebreather** (id 1232): Search your deck for up to 7 Basic {R} Energy cards, reveal them, and put them into your hand. Then, shuffle your deck.
- **Anthea & Concordia** (id 1234): You can use this card only if you have N’s Darmanitan, N’s Zoroark {ex}, N’s Vanilluxe, N’s Klinklang, N’s Reshiram, and N’s Zekrom in play. During this turn, i
- **Waitress** (id 1235): Look at the top 6 cards of your deck and attach a Basic Energy card you find there to 1 of your Pokémon. Shuffle the other cards back into your deck.
- **Tarragon** (id 1238): Put up to 4 in any combination of {F} Pokémon and Basic {F} Energy cards from your discard pile into your hand.

## v3 champion deck: the two cards missing above, plus a cross-check

`ptcg_ai/agent/main.py`'s `DECK` (v3, current champion) runs a Snover/Mega
Abomasnow ex evolution line that wasn't previously in this catalog (the
curated lists above are subsets, not exhaustive). Filled in here from the
engine's own `lib.AllCard()`/`lib.AllAttack()` data (same source as the rest
of this file):

- **Snover** (id 722, Water, 90HP, Stage: Basic, retreat 3): Beat (10dmg/1en); Icy Snow (30dmg/2en). Evolves into Mega Abomasnow ex.
- **Mega Abomasnow ex** [megaEx] (id 723, Water, 350HP, retreat 4, evolves from Snover): Hammer-lanche (0dmg/2en) -- discard the top 6 cards of your deck, 100 damage per Basic {W} Energy discarded this way (variance-heavy, big-swing attack); Frost Barrier (200dmg/3en) -- this Pokemon takes 30 less damage from attacks during your opponent's next turn (a defensive follow-up after tagging in).

Separately, as a credibility/consistency check (not a content source -- the
Japanese card database is competition-licensed, use-only, and not
redistributed here per `LicenseRef-PTCG-ABC-Competition-Use-Only`): cross-
referencing DECK's card ids against it confirms every id in v3 maps to its
expected real-world Pokemon/card name and type, e.g. 209 = Chien-Pao
(Water), 721 = Kyogre (Water), 722/723 = Snover/Mega Abomasnow (Water),
1092 = a "Secret Box"-style search Item, 1121 = an Ultra-Ball-style search
Item, 1163 = an end-of-turn Energy-recovery Tool, 1219 = a Trainer-search
Supporter, 1227 = Lillie's Determination (shuffle-hand-and-draw-6/8), 1262
= a Water-type retreat-swap Stadium. This is consistent with the rest of
this catalog's finding that the card pool uses real Pokemon names/likeness
with invented, game-balanced mechanics and numbers rather than verbatim
real-TCG text -- so the Japanese source was used only to validate id<->name
alignment, not as a source of in-game mechanical text (which, where it
differs, is the engine's own `AllCard`/`AllAttack` values quoted above and
throughout this file).

