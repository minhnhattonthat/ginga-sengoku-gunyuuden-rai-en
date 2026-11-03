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
- [ ] 0118DA-011900 - battle_result left labels (7 letters) touch the count digits; abbreviations Flagshp/Btlship/Destryr (engine: move the count right)
- [ ] fleet_list, planet_list - cursor box covers the first letter of the selected name
