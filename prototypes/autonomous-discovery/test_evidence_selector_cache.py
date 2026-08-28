from dataclasses import dataclass

from PIL import Image, ImageDraw

from evidence_selector import EvidenceAuthoritySelector


@dataclass
class C:
    id: str
    value: int
    checks: dict
    route: str = 'recurrence'


def test_repeated_comparisons_render_each_candidate_once_per_time():
    counts = {}
    times = (0, 1, 2)

    def render(c, t):
        counts[c.id] = counts.get(c.id, 0) + 1
        im = Image.new('L', (40, 40), 0)
        d = ImageDraw.Draw(im)
        d.ellipse((4 + c.value, 7 + t, 18 + c.value, 21 + t), outline=180, width=2)
        return im

    a = C('a', 2, {'valid': True})
    b = C('b', 10, {'valid': True})
    selector = EvidenceAuthoritySelector(render_frame=render, times=times)

    first = selector.compare(a, b, {'brief': 'x'})
    second = selector.compare(a, b, {'brief': 'x'})
    reversed_pair = selector.compare(b, a, {'brief': 'x'})

    assert first.verdict == second.verdict == reversed_pair.verdict == 'tie'
    assert first.confidence == second.confidence == reversed_pair.confidence == 'defer'
    assert counts == {'a': len(times), 'b': len(times)}


def test_cache_is_scoped_to_one_selector_replay():
    calls = 0
    times = (0, 1)

    def render(c, t):
        nonlocal calls
        calls += 1
        return Image.new('L', (20, 20), c.value + t)

    a = C('a', 2, {'valid': True})
    b = C('b', 10, {'valid': True})
    EvidenceAuthoritySelector(render_frame=render, times=times).compare(a, b, {'brief': 'x'})
    EvidenceAuthoritySelector(render_frame=render, times=times).compare(a, b, {'brief': 'x'})

    assert calls == 2 * 2 * len(times)
