from bilibili_cover_fetcher import extract_aid, extract_bvid


def test_extract_bvid_from_url():
    assert extract_bvid("https://www.bilibili.com/video/BV1xx411c7mD") == "BV1xx411c7mD"


def test_extract_bvid_from_plain_text():
    assert extract_bvid("BV1Q5411W7Ar") == "BV1Q5411W7Ar"


def test_extract_aid_from_url():
    assert extract_aid("https://www.bilibili.com/video/av170001") == 170001


def test_extract_aid_from_plain_digits():
    assert extract_aid("170001") == 170001


def test_extract_aid_none():
    assert extract_aid("hello") is None
