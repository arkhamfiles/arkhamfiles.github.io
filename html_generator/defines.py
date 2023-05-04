""" definitions
"""
from typing import Dict, List
from collections import OrderedDict

ICON: Dict[str, str] = {
    'reaction': '반응 격발', 'free': '자유 격발', 'action': '행동 격발',
    'elder_sign': '고대 표식', 'elder_thing': '옛것',
    'skull': '해골', 'auto_fail': '자동 실패',
    'cultist': '추종자', 'tablet': '석판',
    'bless': '축복', 'curse': '저주',
    'combat': '힘', 'agility': '민첩',
    'willpower': '의지', 'intellect': '지식', 'wild': '만능',
    'unique': '고유', 'per_investigator': '조사자당', 'null': '–',
    'guardian': '수호자', 'mystic': '신비주의자',
    'seeker': '탐구자', 'rogue': '무법자', 'survivor': '생존자'
}

ICON_REDIRECT: Dict[str, str] = {
    'fast': 'free', 'elder_sign': 'elder_sign', 'elderthing': 'elder_thing',
    'autofail': 'auto_fail', 'will': 'willpower'
}

ICON_IGNORE: List[str] = [
    'endif', 'accessory', 'body', 'ally', 'hand', 'hand_2',
    'arcane', 'arcane_2', 'health', 'sanity'
]

SYMBOLS: Dict[str, str] = OrderedDict([
    ('core', '기본판'),
    ('rcore', '돌아온 광신도의 밤'),
    ('tdl', '던위치의 유산'),
    ('rtdl', '돌아온 던위치의 유산'),
    ('tpc', '카르코사로 가는 길'),
    ('rtpc', '돌아온 카르코사로 가는 길'),
    ('tfa', '잊힌 시대'),
    ('rtfa', '돌아온 잊힌 시대'),
    ('tcu', '끝맺지 못한 의식'),
    ('rtcu', '돌아온 끝맺지 못한 의식'),
    ('nc', '너새니얼 조'),
    ('hw', '하비 월터스'),
    ('wh', '위니프리드 해버먹'),
    ('jf', '재클린 파인'),
    ('sc', '스텔라 클라크'),
    ('par', '평행 조사자'),
    ('tde', '꿈을 먹는 자'),
    ('tic', '인스머스에 드리운 음모'),
    ('eoep', '지구의 끝자락'),
    ('eoec', '지구의 끝자락 캠페인 확장'),
    ('tskp', '진홍색 열쇠'),
    ('tskc', '진홍색 열쇠 캠페인 확장')
])

EXPANSION: Dict[str, str] = OrderedDict([
    ('core', '기본판'),
    ('tdl', '던위치의 유산'),
    ('tpc', '카르코사로 가는 길'),
    ('tfa', '잊힌 시대'),
    ('book', '서적'),
    ('promo', '프로모'),
    ('parallel', '평행'),
    ('tcu', '끝맺지 못한 의식'),
    ('starter', '초심자 덱'),
    ('nc', '너새니얼 조'),
    ('hw', '하비 월터스'),
    ('wh', '위니프리드 해버먹'),
    ('jf', '재클린 파인'),
    ('sc', '스텔라 클라크'),
    ('par', '평행 조사자'),
    ('tde', '꿈을 먹는 자'),
    ('tic', '인스머스에 드리운 음모'),
    ('eoep', '지구의 끝자락'),
    ('eoec', '지구의 끝자락 캠페인 확장'),
    ('tskp', '진홍색 열쇠'),
    ('tskc', '진홍색 열쇠 캠페인 확장')
])
