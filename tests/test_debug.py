"""Phase 2 debug tool: the scene list regen.py reads from scenes.lua (the emulator runs themselves are regen.py)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools' / 'debug'))
import regen  # noqa: E402


def test_scene_list_parsed():
    names = regen.scene_names()
    assert len(names) == len(set(names)) >= 50
    for must in ('title', 'map_nankyourou', 'battle_result', 'prisoner_recruit', 'game_over', 'credits',
                 'ending_nankyourou', 'ending_ren', 'ending_nanten', 'ending_daigojou'):
        assert must in names


def test_scene_saves():
    # fixture scenes name their save; everything else boots blank; every fixture has a maker scene
    assert regen.scene_sav('title') == 'blank'
    assert regen.scene_sav('load_screen') == 'nankyourou_start'
    for fixture, maker in regen.FIXTURES.items():
        assert maker in regen.scene_names()
        assert any(regen.scene_sav(n) == fixture for n in regen.scene_names())
