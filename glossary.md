# Glossary - Ginga Sengoku Gunyuuden Rai

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` warns when a JP term below is in a string and none of its EN forms (split by ` / `) is.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Rai-dono, Rako-sama). Name order: Western (given name first) for Japanese-style
  family + given names (竜我雷 = Rai Ryuga, 大覚屋師真 = Shishin Daigakuya); Chinese-style names keep their order
  (姜子昌 = Kyo Shisho, like Liu Bei).
- Romanisation: no official English release exists (manga by Joji Manabe, 1994 anime unlicensed), so Hepburn
  without macrons from the readings on ja.wikipedia (銀河戦国群雄伝ライ, fetched 2026-11-03): ou/oo -> o, uu -> u.
- Credits: English.
- Register / flavour (D8): space-opera war drama with a Chinese Three Kingdoms veneer. Rai is brash and rough
  ("I'm gonna", "ya", contractions); nobles and old generals formal ("I shall", "thou" never); Ranran and
  Shimon's kansai-ben (うち, や, へん) -> chirpy, casual ("ain't", "y'know"). Sound effects: none in the text.
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening.

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...' (titles of ships: plain), ・・・ / … -> ..., ！？ -> ?!, ～ dropped
  or a stretched vowel ("Hyaaah!").
- Plain ASCII plus the font's `...` glyph; no tabs.
- 専 in the decoded JP is the game's 夢 (dream) read wrong by tbl/jp.tbl: translate as "dream".
- Dialogue: write one paragraph; `tools/batches.py` wraps it under the opening quote. Speaker name before `{c5}`.
- Composite map notices are built as name + fragment + name + fragment: fragments start with a space or a
  colon, never glue a suffix onto a name.

## Characters (officer list names first; full names where the game gives them)

Speech-box speaker tags (advisor and battle-quote boxes, 7 letters; `build.TAG_SHORT`): Sho Shigen -> Shigen,
Rin Sokuka -> Sokuka, Kyo Shisho -> Shisho, Sanrakusai -> Sanraku, Ryogenkaku -> Genkaku. Other 8-letter names
are set in condensed letters there. The box has no quote marks in English.

| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 竜我雷 | Rai Ryuga / Rai | | hero, Nankinro | Ryuuga |
| 竜我 | Ryuga / Rai | 8 | officer record name | |
| 雷 | Rai | | | |
| 大覚屋師真 | Shishin Daigakuya / Shishin | | Rai's strategist | Daikakuya |
| 師真 | Shishin | | | |
| 英真 | Eishin | | Shishin's brother | |
| 紫紋 | Shimon | | Rai's wife, Aso Shuzen's daughter | |
| 麗羅 | Reira | | Hiki Danjo's daughter | |
| 蘭々 | Ranran | | Shimon's attendant, kansai-ben | |
| 林則嘉 | Rin Sokuka | 10 | strategist | |
| 孟閣 | Mokaku | | general | |
| 鐘士元 | Sho Shigen | 10 | one-eyed veteran | |
| 姚文 | Yobun | | | |
| 項武 | Kobu | | ex-pirate | |
| 項焉 | Koen | | Kobu's father, pirate | |
| 三楽斎 | Sanrakusai | 10 | civil official | |
| 雲海 | Unkai | | warrior monk | |
| 太助 | Tasuke | | | |
| 装民 | Somin | | shipwright, built the Kongo | |
| 武尊 | Buson | | Kongo helmsman | |
| 王政 | Osei | | Five Tiger General | |
| 比紀弾正 | Danjo Hiki / Danjo | | founder of Gojo | |
| 弾正 | Danjo | | | |
| 狼刃 | Roha | | woman general of Gojo | |
| 蒲生 | Gamo | | | |
| 僧関 | Sokan | | | |
| 興起 | Koki | | | |
| 骸羅 | Gaira | | Emperor of Great Gojo | |
| 骸山 | Gaizan | | Gaira's brother (calls Gaira 兄者, 11629B) | |
| 骸延 | Gaien | | Gaira's younger brother | |
| 馬元宇 | Ba Genu | | Ryojun fortress commander | |
| 武倒国 | Butokoku | | | |
| 白鬼 | Hakki | | Five Tiger General | |
| 亮厳格 | Ryogenkaku | 10 | Five Tiger General; "Ryo Genkaku" is 11 letters | |
| 武庸 | Buyo | | Five Tiger General | |
| 魏相如 | Gi Shojo | | Five Tiger General | |
| 法権 | Hoken | | | |
| 羅候 | Rako | | Lord of Ren, King of Nanten | Rakou |
| 邑峻 | Yushun | | Rako's wife, Nanban King's daughter | |
| 姜子昌 | Kyo Shisho | 10 | Ren's great general | |
| 蹄庖 | Teiho | | Kyo Shisho's right hand | |
| 究興 | Enko | | Ren officer (wiki 兗興; the game's glyph reads 究) | |
| 龍緒 | Ryusho | | Ren chancellor | |
| 夏候獣 | Kako Ju | | Nanban general | |
| 夏候牙 | Kako Ga | | | |
| 夏候才 | Kako Sai | | | |
| 豪蛮 | Goban | | | |
| 独眼竜正宗 | Masamune / One-Eyed Dragon | | Chi's heroine | |
| 正宗 | Masamune | | | |
| 独眼竜 | One-Eyed Dragon | | | |
| 飛竜 | Hiryu | | Masamune's right hand | |
| 虎丸 | Toramaru | | King of Chi, Masamune's brother | |
| 儒李 | Juri | | | |
| 王華 | Oka | | | |
| 斎遠 | Seien | | wiki 斉遠 | |
| 峰索 | Hosaku | | | |
| 狼平 | Rohei | | | |
| 座楽 | Zaraku | | | |
| 修理 | Shuri | | | |
| 雷神 | Raijin | | Lord of Min | |
| 座苞 | Zaho | | | |
| 剛志 | Goshi | | Lord of Mo | |
| 曹州 | Soshu | | Lord of Cho | |
| 南蛮王 | Nanban King | | Yushun's father | |
| 光輝帝 | Emperor Koki | | | |
| 阿曽主弾 | Aso Shuzen | | Shimon's father (wiki 阿曹主禅) | |

## Factions and titles
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 南京楼軍 | Nankinro Army / Nankinro | | Rai's faction | |
| 南京楼 | Nankinro | | | |
| 練国 | Ren | | Rako's kingdom | |
| 練軍 | Ren Army / Ren | | | |
| 南天連合軍 | Nanten Alliance / Nanten | | Masamune's faction | |
| 南天 | Nanten | | the southern heavens | |
| 大五丈軍 | Great Gojo Army / Great Gojo | | Gaira's faction | |
| 大五丈 | Great Gojo | | | |
| 五丈 | Gojo | | | |
| 智 | Chi | | Masamune's homeland | |
| 南蛮 | Nanban | | | |
| 神聖銀河帝国 | Holy Galactic Empire | | | |
| 五虎将軍 | Five Tiger Generals / Five Tiger General | | | |
| 銀河統一 | unif | | unify / unification of the galaxy | |
| 皇帝 | Emperor | | | |
| 陛下 | Majesty | | | |
| 殿 | -dono | | honorific kept | |
| お館様 | my lord / lord | | | |
| 軍師 | strategist | | | |
| 太守 | Governor | | 大守 in the game too | |

## Places (planets; label max 10)
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 益州都 | Ekishuto | 10 | | |
| 南蛮王都 | Nanban Oto | 10 | royal capital of Nanban | |
| 南帝閣 | Nanteikaku | 10 | | |
| 座王都 | Zaoto | 10 | | |
| 洛火閣 | Rakkakaku | 10 | | |
| 虎卓関 | Kotakukan | 10 | | |
| 流北平 | Ryuhokuhei | 10 | | |
| 斉王都 | Seioto | 10 | | |
| 武王都 | Buoto | 10 | | |
| 遼陽 | Ryoyo | 10 | | |
| 鴨緑江 | Oryokko | 10 | | |
| 魔天嶺 | Matenrei | 10 | | |
| 旅順 | Ryojun | 10 | | |
| 鳳凰城 | Hoojo | 10 | | |
| 艾塔堡子 | Gaitohoshi | 10 | | |
| 言堡子 | Genhoshi | 10 | | |
| 大堡屯 | Daihoton | 10 | | |
| 弓張嶺 | Kyuchorei | 10 | | |
| 紅沙嶺 | Kosarei | 10 | | |
| 孫家塞 | Sonkasai | 10 | | |
| 藍家屯 | Rankaton | 10 | | |
| 延高城 | Enkojo | 10 | | |

## Ships and units
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 金剛 | Kongo | | Rai's flagship | |
| 新金剛 | New Kongo | | | |
| 大帝山 | Taiteizan | | | |
| 威海洋 | Ikaiyo | | Danjo's ship | |
| 鎮遠 | Chinen | | | |
| 定遠 | Teien | | | |
| 帝虎 | Teiko | | | |
| 狼焔 | Roen | | | |
| 比叡 | Hiei | | | |
| 猛虎 | Moko | | | |
| 富嶽 | Fugaku | | | |
| 戦艦 | battleship | | | |
| 巡洋艦 | cruiser | | | |
| 駆逐艦 | destroyer | | | |
| 旗艦 | flagship | | | |
| 要塞 | fortress | | | |
| 艦隊 | fleet | | | |
| 部隊 | unit | | | |
| 武将 | officer | | | |
| 白兵 | melee | | ship-boarding fight | |
| 一騎討ち | duel | | | |
| 轟雷砲 | Thunder Cannon | | New Kongo's line weapon | |
| 艦首砲 | bow cannon | | | |
| 鳳鳴 | Homei | | one of Gaira's four legions | |
| 玄偉 | Geni | | one of Gaira's four legions | |
| 車騎元帥 | Chariot Marshal | | | |

## Decisions from earlier batches
- b001 南京楼軍 etc. in 10-letter labels: Nankinro / Ren Army / Nanten / Great Gojo.
- Review (all batches): old-man わし/じゃ/のう lines get a marker ("eh", "ye", "I say", "mind"); Ranran's and
  Shimon's kansai-ben always gets one ("y'know", "ya hear", "ain't", -in'); 甘い in a taunt = naive, not sweet;
  王 = king (陛下 = Majesty). Melee orders (14884A): Free Fight / Hit Leader / Bodyguard / Retreat / Duel / Wait.
- b001 composite notices: は、 -> ":" style ("Nankinro: Ren has taken it!").
