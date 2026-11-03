# Polish pass

Reviewer Minors, deferred to one pass before release (`tools/release.py` refuses while a line is unticked).
Tick each `[x]`: fixed, or `waived: reason`.

## b001
- [x] 000CA6 - 大五丈軍 "Gojo" vs "Great Gojo" elsewhere (if width allows) -> waived: 10-byte field holds {end}, "Great Gojo" is 12 bytes
- [x] 000D3D, 000D51, 000D5C - 大型戦艦/南蛮大型/南蛮戦艦 split unclear ("Large Ship"?) -> waived: Heavy Ship / Big Nanban / Nanban mirror Big Pirate / Pirate; 10-letter label has no room for "battleship"
- [x] 006187 - " has taken it!": "it" ambiguous if first name is a faction (check in game) -> waived: JP order is place は、 faction に, so "it" is the name before the colon; cannot settle further from text

## b002
- [x] 010466, 01215E, 013774 - 野郎ども "ya dogs" too harsh: "you lot" -> fixed
- [x] 01079A - "Taiteizan joins in.{n}Don't fight shamefully,{n}{FFFE}!" -> fixed
- [x] 010A60 - "How long are you taking on these brats?! Finish them!" -> fixed
- [x] 010CB6 - Hoken old-man register: "Old Hoken's here! You could've fought fine without me." -> fixed
- [x] 010D3C - drop added "sir": "Me! Leave it all to me!" -> fixed
- [x] 010704 - ウォ〜ッ war cry: "Rrraah! I'm itching for a fight!" -> fixed
- [x] 01050A - "Ahem... Might someone have called Sanrakusai?" -> fixed

## b003
- [x] 010E2C - 待たせたな: "Rai Ryuga is here! Kept ya waitin', {FFFE}!{n}Let me cut loose too!" -> fixed (name moved last: pad box needs the name on the last line)
- [x] 011702 - lead with 御無事ですか: "Are you safe, {FFFE}-dono?..." -> waived: pad box needs the name on the last line; leading with it overflows to 4 lines
- [x] 01121C - "Nanban King! Please watch how I fight!" -> fixed
- [x] 011076 - Ranran "Y'all" is Southern; 暴れたる: "...I'll raise some hell!" -> fixed
- [x] 0110BE - 天下統一 "my unification" vague -> fixed
- [x] 011A96 - "burns with ambition" dropped for width -> fixed

## b004
- [x] 012070 - 野望 = ambition, not dream -> fixed
- [x] 0125BE - "Wasting my fleet on a planet like this!" -> fixed
- [x] 012DF6 - old-man: "Guhuhuhu... How's that for skill, eh? Defense is child's play!" -> fixed
- [x] 012F66 - six dots: "...Victory is mine." -> fixed
- [x] 012C76 - 暇な所: "If I'd slacked off at a dull post like this..." -> fixed

## b005
- [x] 013924 - stray space "Shimon-chan... ?!" -> fixed
- [x] 0138DE - 『情』 "feeling" cold: "heart" -> waived: current line already says "heart"; quoting 'heart'/'reason' overflows the box
- [x] 014532 - "Show me this so-called caliber to take the realm!!" -> fixed
- [x] 0142F4 - six dots -> fixed
- [x] 0146C8 - かしら: "Which of us is prettier, I wonder?" -> fixed
- [x] 01348C - "Show me everything, galaxy's finest talent... Shishin Daigakuya!!" -> fixed ("Show me it all": "everything" overflows)
- [x] 014C54 - "All troops, fight without fear!" -> fixed ("fear nothing" for width)
- [x] 013F2A - ほう: "Hoh..." -> fixed

## b006
- [x] 014DA8 - 義兄上: "brother-in-law" if it fits -> fixed
- [x] 014E80, 014EB0, 0150C6 - わし lords neutral; 014EB0 drops いまいましい奴め -> fixed (014EB0); 014E80/0150C6 kept, neutral わし is fine
- [x] 015866 - "Repent, and learn my way!" -> waived: overflows the 3-line box; "learn mine" already says it
- [x] 015BE0 - Ranran: "Lemme at it, I'd take it in no time, y'know!!" -> fixed (kept JP "if it was me")
- [x] 015B42 - 星の一つくらい: "taking a single planet is easy!!" -> fixed

## b007
- [x] 01627C - 甘い専 = naive dream -> fixed
- [x] 016EE8 - Kako Ju くだされ: "Decide the survivors' fate, and press on to unify the galaxy!!" -> fixed

## b008
- [x] 0623E0 - 艦種艦数 "Type/Size": "Type/Qty" -> fixed
- [x] 0403AE - ませんぞ: "..., mind!" -> fixed
- [x] 0623D8 - "Flag" for 旗艦 forced by 4-cell column (engine) -> waived: engine item, 4-cell column; text cannot fix

## b009
- [x] 0FC029 - 十三代 and 元帝国左将軍 cut (attract keeps JP line cells) -> waived: fixed 248-cell attract layout has no room
- [x] 10EC7E - four legions sentence garbled across split strings -> fixed
- [x] 10EE02 - 共謀 = conspired -> fixed
- [x] 116AED - Nanban King じゃ flat -> fixed

## b010
- [x] 12EAF7 - Shishin いいだろう: "All right." -> fixed
- [x] 11FDC0 - 一軍の将には飽き足らず, 南蛮諸国: "Not content as a mere general, he's in league with the Nanban realms..." -> fixed ("with Nanban": "realms" overflows)
- [x] 11FE4A - むうう "Grrr...": "Mmgh..." -> fixed
- [x] 11629B, 116A8B, 116B57 - {c5} after the opening quote: confirm in game it matches the JP -> waived: EN codes mirror the JP (Name{c5}" as Name{c5}「); on-screen check is the playtester's

## b011
- [x] 17FE98, 187D7B - Rako: "I did it! I've finally united the galaxy!" -> fixed (187D7B "Couldn't be better!")
- [x] 17FF4C - "for those who fell" -> fixed

## b012
- [x] 18FACB - "Is that so!" -> fixed
- [x] 18F57B - "Emperor of the great galactic empire" if the page fits -> fixed ("the great galaxy's Emperor": full phrase overflows)
- [x] 19E244, 19E2DA, 19E36E, 19E408 - "fell halfway": "died with it unfinished" -> fixed ("died with the same dream unfulfilled")
- [x] 19E56A - "raced through" -> fixed

## b013
- [x] 1D8548 - おぬしは父のかたき: "You're my father's enemy..." (check scene) -> waived: 父のかたき = father's killer; "You killed my father" is the standard reading
- [x] 1D8264, 1D82A8, 1D8BDA - 勝負ありましたね: "It's over." -> fixed
- [x] 1D8766, 1D906E - それがし/くだされ: "I humbly beg you..." -> fixed (1D8766; 1D906E has no くだされ, six dots trimmed)
- [x] 1D946E - "...my best friend... always..." -> fixed
- [x] 1D9572 - "Broken by a dream, scattered by a dream... huh." -> fixed
- [x] 1D8844 - "If you grasp what a supreme king needs, brother, you'll find your path!" -> fixed ("Grasp what...": suggestion overflows)

## b014
- [x] 1DA988 - "You have the worth to value my talent." -> fixed
- [x] 1DAB08 - "I'll live! I might go with you!" -> fixed
- [x] 1DA0A6 - 義兄上 "Brother-in-law" (check scene) -> waived: current line already says it (matches 014DA8)
- [x] 1D9F34 - old-man register optional -> fixed

## b015
- [x] 1DAF9C, 1DB022, 1DAFBC - kansai refusals flat -> fixed (1DB022, 1DAFBC; 1DAF9C is standard 私 speech, kept)
- [x] 1DB11E - "My king, thank you, but I won't live on in shame." -> fixed
- [x] 1DADF0 - 国難, 後世 dropped -> fixed
- [x] 1DB6AE - 名を偽っているうちは dropped -> fixed
- [x] 1DB1E0 - feminine ね: "Hmph, " -> fixed
- [x] 1DB92C - "stature" for variety -> fixed

## b016
- [x] 1DC4FA - 惜しまれつつ散るのも一興: "To fall mourned is its own pleasure!" -> fixed
- [x] 1DC56C - 命数が尽きた: "So my time has run out..." -> fixed
- [x] 1DC9A4 - 逃げてもらいます: "To unify the galaxy, I'll have you flee!" -> fixed
- [x] 1DCB48 - 早く dropped: "Hurry up and get strong enough to beat me!" -> fixed
- [x] 1DCC8A - 覇者としての器: "...judge my worth as conqueror from outside!" -> fixed
- [x] 1DCE32 - "not that into" reads romantic: "Kyo Shisho barely interests me! Just scram!!" -> fixed
- [x] 1DCEBC - 信じる道: "I want to see where the path you believe in leads...!" -> fixed
- [x] 1DD6FA - 命預けておく: "Gaien! Your life can wait for now!!" -> fixed ("I'll let you keep your life for now")
- [x] 1DD880 - この白鬼 self-reference: "I, Hakki, spare no foe out of mercy!!" -> fixed
- [x] 1DDB7A - "soft enough to lose" stiff: "I'm not fool enough to lose again next time!!" -> fixed
- [x] 1DC54E - capitalize "Brother" (as 1DD03E, 1DE4F8) -> fixed

## b017
- [x] 1DDD2A - わ voice: "You needn't tell me! I'm not coming back!!" -> fixed
- [x] 1DDDEE - 無駄なことを: "How futile..." -> fixed
- [x] 1DE24A - "Enjoy that smugness while it lasts...!" -> fixed
- [x] 1DE432 - "I... I'll surely get you...!" -> fixed
- [x] 1DE4CE - neutral, unfinished: "That side of you is what I..." -> fixed
- [x] 1DE56E, 1DE5B0 - 狼刃め contempt: "Damn Roha! ..." / "... Damn you, Roha, ..." -> fixed
- [x] 1DE5EE, 1DE806, 1DE846, 1DE3F8 - vary the stock "You'll pay for this" ("Remember this!") -> fixed (1DE806 "Remember this!!", 1DE846 "You haven't seen the last of me!!"; 1DE3F8 is not a stock line)

## b018
- [x] 14884A - "Hit Leader" could read as own leader ("Hit Enemy"?) -> waived: beside "Bodyguard" it reads as the enemy leader; "Hit Enemy" loses 将 (10-letter field)
- [x] 1481A0 - "I won't fall easily!" -> fixed
- [x] 14821C - 覇道: "Kyo Shisho won't let anyone block my lord's conquest!" -> fixed ("lets none block": suggestion overflows)
- [x] 14829E - "Justice is on my side!" -> waived: 16-letter line; "Justice is mine!" already says it
- [x] 14858E - 大銀河, 様: "The Emperor of the great galaxy is me!" -> fixed ("I'm the Emperor of the great galaxy!")
- [x] 148050 - 竜我雷様 swagger: "I, the great Rai Ryuga, lead Nankinro!" -> fixed ("Face the great Rai Ryuga of Nankinro!")
- [x] 1483C2 - ノコノコ: "You strolled right out, but it ends here!" -> fixed
- [x] 148A6C - "I can't fight any further." -> fixed
- [x] 149118 - "Next time will be different!" -> fixed
- [x] 1485FA - ほめてやるぞ: "Well done, coming this far! I commend you!" -> fixed ("You made it this far! I commend you!")

## Phase 8 tour
- [x] 0118DA-011900 - battle_result left labels (7 letters) touch the count digits; abbreviations Flagshp/Btlship/Destryr (engine: move the count right) -> waived: readable; moving the count column needs a code hook, not worth the risk for v1
- [x] fleet_list, planet_list - cursor box covers the first letter of the selected name -> waived: engine draws the 5-cell label from x=0; JP names were centred; listed as a known limit in docs/visual-qa-brief.md

## Story pass (b010-b013)
- [x] 176EF0 - Tasuke アニキ: "You did it, big bro!" -> fixed
- [x] 12EC6F - Rai 時間だな: "Time, then." -> waived: "Time, huh?" answers Shishin's "If there's a problem..." in Rai's voice; "Time, then." reads as "let's go"
- [x] 17FE7E - Kyo Shisho はっ after "My lord" line: "At once." -> waived: Rako gives no order there ("I'm counting on you"); "My lord." is the acknowledgment
- [x] 18F269, 18F657 - Gaira まったくだ "Sure have." too casual: "Indeed." (keep the echo of Roha if it fits) -> fixed ("Indeed I have.")
- [x] 18EEF1 - Toramaru 姉上: "Sister" capitalised as 18F08F -> fixed
- [x] 18F57B - Gaira: "I'm the Emperor of this great galactic empire!!" (as 18F42F) -> waived: line 2 holds ~34 letters; 18F42F's wording needs two lines there
- [x] 18FA3F-18FB85 - 西羌 = Seikyo: add to glossary -> fixed (Places table)
- [x] 19E56A - "each cast away all he had": "each threw away everything for what they believed in"; title wording vs 戦国 -> fixed; title kept ("Warlords" = 群雄, the age of war already said)
- [x] 1D8C92, 1D8CC4 - old man わし/じゃ: add "eh"/"ye see" markers -> fixed
- [x] 1D9418 - Ranran ええか: "Shimon! Ready, y'know?!" -> fixed ("Shimon! Ya ready?!": "y'know" on a question reads odd)
- [x] 1D8114 - Rai too stiff: "Let's make the dream of a united realm come true together!" -> fixed
- [x] 1D8B2A - 私の勝ちだ: "The victory is mine..." -> fixed

## Story pass (b002-b005)
- [x] 010600 - "What's wrong, {FFFE}?! Quit fumblin' with this rabble!" -> fixed (name moved last: pad boxes need the name on the last line)
- [x] 01094E - vary "Blast it! You lot!": "Damn it all! Is this the best you can do? Spineless cowards!" -> fixed
- [x] 010BFC - "Why fear men like these? Shame on you, {FFFE}! Shame!" -> fixed
- [x] 0110BE - Rako colder: "Anyone who stands in the way of my conquest of the realm will be crushed!" -> fixed ("Anyone who blocks my conquest of the realm will be crushed!")
- [x] 011702 - order: "Are you safe, {FFFE}-dono? Moving to support! All guns, stand ready!" -> waived: pad boxes need the name on the last line, so the question stays last
- [x] 01147E - 殿ともあろうお方が: "...How pitiful for one of your standing!" -> fixed ("My, my! Beset by this lot? Pitiful, for one like {FFFE}-dono!": name must end the box)
- [x] 011EAC - "Remember this! Next time I'll bring you down for sure!" -> fixed
- [x] 010E6E - "Now that yours truly's here, ya got nothin' to worry about!" -> fixed ("...ya got nothin' to fear!" for 3 lines)
- [x] 012070 - "the mighty Gairas' ambition": "the Gaira brothers'" if it fits -> fixed ("The mighty Gaira brothers' dream": "ambition" does not fit 32)
- [x] 01261A - 沈黙した: "{FFFD} has been silenced!" -> fixed ("All right! We've silenced {FFFD}!": name must end the box)
- [x] 01459A - 覇王: "the makings of an overlord" -> fixed ("overlord material")
- [x] 0142B8 - "Late Nanban King... forgive my disloyalty..." -> fixed
- [x] 013924 - もう忘れたはずだろ: "you'd forgotten her!" -> fixed ("You were supposed to forget her!")

## Story pass (b006-b009)
- [x] 0158F4 - gag form: "My way is a man's way!! Behold my way!" -> fixed
- [x] 015DD8 - 何とか: "we can manage to take it!" -> fixed ("we can manage it!")
- [x] 01604C - map image: "Take this place and the galaxy's map changes; an officer's way never will!" -> fixed ("Take it, and the map changes! An officer's way never will!": "galaxy's" does not fit 3 lines)
- [x] 015D1E - "in a jiffy" too light if the speaker is Masamune (check speaker) -> waived: あたし/こ～んな is a playful speaker, not Masamune (私)
- [x] 0165D0 - Hakki 虫が良い: "Such presumption!!" -> fixed ("Take a demon's planet? Such presumption!!...")
- [x] 01695E - "I'm dying, I'm dying... ME!!" -> fixed
- [x] 016EE8 - Kako Ju くだされ: optional old-man marker -> waived: くだされ is formal-archaic, no わし/じゃ; the formal line fits the old-general voice
- [x] 016F40, 016F9E - お館様 to Masamune: "my lord" (glossary) vs style row "My lady": decide, update style-reference -> fixed (glossary "my lord" kept; style-reference Hiryu row now "My lord!")
- [x] 0623D8 - "Unit{n}Flag": "Flagship" if the field allows -> fixed ("Flag{n}ship")
- [x] 08F8E7 - Rako 皆の者: "Hear me!" -> fixed
- [x] 0FC029 - spacing ("away,   ending", "destiny.One"); thirteen generations / 270 years, Left General if room -> waived: the gaps are per-line padding to the JP line cells (data/boxes.tsv), each piece shows on its own line; no room for 13 reigns or Left General
- [x] 116ED1 - "that is..." lowercase at box start: "That is..." -> fixed
- [x] 116FB1 - "I swear I'll unify the galaxy with my own hands!" -> fixed ("I'll unify the galaxy by my hand!": the line holds ~34 letters)

## Story pass (b014-b018)
- [x] 1D9F92 - 感謝: "I'm grateful for my king's greatness." -> fixed ("Leaving for another nation was folly." to fit 3 lines)
- [x] 1DA390 - 才: name (Sai) or "talent"? check -> waived: 才 = Kako Sai (glossary 夏候才) addressed by name ("Let's go, Sai!"), as it stands
- [x] 1D9758, 1D97B8, 1D9804, 1D99EA, 1D9B42 - vary "Are you prepared...?" by register -> fixed ("Prepare yourself..." / "Are you prepared?" / "Are you quite prepared...?" / "Ready to die...?" / "Are you... quite prepared?")
- [x] 1DAC7E - あっし: "Ya got me beat... I'll put my life in your hands!" -> fixed
- [x] 1DC070 - "Hurry... Kyo Shi... sho-sa... ma...!" -> fixed ("Kyo Shisho-sa... ma...!": the JP breaks only さ…ま)
- [x] 1DC800 - "If I kill you, I can't face Lord Danjo... But never show yourself to me again." -> fixed ("Kill you, and..." for 3 lines)
- [x] 1DCCCE - "Go live in shame...! You're my father's enemy!!" -> fixed
- [x] 1DDB7A - "I'm not so naive that I'll lose again next time!!" -> fixed
- [x] 148286 - 刀のサビ: "You'll be rust on my blade!" -> waived: needs a second line the 10-letter JP line does not have; "Taste my sword!" is the idiom
- [x] 148050 - 総大将: "Nankinro's commander, Rai Ryuga, is your opponent!" if width allows -> fixed ("Face Nankinro's commander, Rai Ryuga!", one line)
- [x] 14858E - Gaira: "The Emperor of the great galaxy is ME!" -> fixed ("The great galaxy's{br}Emperor is ME!", the JP's 2 lines)
- [x] 14829E - "Justice is on my side!" if width allows (was waived at 16 letters) -> waived: still 16 letters; would need a second line

## Story pass re-review (post-fix deltas)
- [x] 1DDB7A - echo Ranran's "softness" line: "I'm not soft enough to lose again next time!!" -> waived: optional; current line reviewed ok
- [x] 1DCCCE - かたき alternative wording -> waived: reviewer: current line OK
- [x] 1D99EA - "Ready to die...?" stronger than 覚悟は良いか -> waived: reviewer: acceptable for the duel
- [x] 015DD8 - 占領: "we can somehow take it!" -> waived: optional; meaning kept
- [x] 116FB1 - 必ずや lost; "with my own hands" -> waived: optional; tone kept
- [x] 01147E - stiff mocking line -> waived: optional
- [x] 01459A - "overlord material" casual for a formal speaker -> waived: optional
- [x] 0125BE - add "you" (resentful at the lord) -> waived: optional
